import click
from pathlib import Path
from typing import Optional

from kb.core import KnowledgeParser
from kb.dependency import DependencyResolver, PackageDownloader, ConflictDetector
from kb.exceptions import DependencyConflictError, KnowledgeBaseError

# 常量定义
DEFAULT_KNOWLEDGE_FILE = "Knowledge.md"
DEPS_DIR_NAME = "deps"


def _validate_knowledge_file(knowledge_file: Path) -> None:
    """验证知识库文件的有效性

    Args:
        knowledge_file: 知识库文件路径

    Raises:
        SystemExit: 如果文件无效
    """
    # 检查文件是否存在
    if not knowledge_file.exists():
        click.echo(f"错误: 未找到知识库文件 '{knowledge_file}'")
        click.echo("请确保文件存在，或使用 --path 参数指定正确的路径")
        raise SystemExit(1)

    # 检查路径是否为目录
    if knowledge_file.is_dir():
        click.echo(f"错误: 指定的路径 '{knowledge_file}' 是一个目录")
        click.echo("请指定Knowledge.md文件路径，而不是目录")
        raise SystemExit(1)

    # 检查文件是否为空
    if knowledge_file.stat().st_size == 0:
        click.echo(f"错误: 知识库文件 '{knowledge_file}' 为空")
        click.echo("请确保文件包含内容")
        raise SystemExit(1)


def _determine_knowledge_file(path: Optional[str]) -> Path:
    """确定知识库文件路径，优先在src目录下查找

    Args:
        path: 用户指定的路径

    Returns:
        Path: 知识库文件的绝对路径
    """
    # 尝试在src目录下查找Knowledge.md
    src_path = Path.cwd() / "src"
    if src_path.exists() and src_path.is_dir():
        knowledge_file = src_path / "Knowledge.md"
        if knowledge_file.exists() and knowledge_file.is_file():
            return knowledge_file

    # 如果src目录不存在，使用默认路径或用户指定路径
    return (Path.cwd() / DEFAULT_KNOWLEDGE_FILE).resolve() if path is None else Path(path).resolve()
def _determine_knowledge_file(path: Optional[str]) -> Path:
    """确定知识库文件路径

    Args:
        path: 用户指定的路径

    Returns:
        Path: 知识库文件的绝对路径
    """
    if path is None:
        return (Path.cwd() / DEFAULT_KNOWLEDGE_FILE).resolve()
    else:
        return Path(path).resolve()


def _display_metadata_info(metadata) -> None:
    """显示元数据信息

    Args:
        metadata: 解析后的知识库元数据
    """
    click.echo(f"正在解析知识库文件: {metadata.name}")
    click.echo(f"知识库名称: {metadata.name}")
    click.echo(f"版本: {metadata.version}")
    click.echo(f"类型: {metadata.type}")
    click.echo(f"职责描述: {metadata.description}")

    # 显示依赖信息
    if metadata.dependencies:
        click.echo(f"依赖数量: {len(metadata.dependencies)}")
        for dep in metadata.dependencies:
            click.echo(f"  - {dep.name}@{dep.version} ({dep.git_url})")


def _resolve_dependencies(resolver: DependencyResolver, metadata) -> list:
    """解析依赖关系

    Args:
        resolver: 依赖解析器
        metadata: 知识库元数据

    Returns:
        list: 解析后的依赖列表

    Raises:
        SystemExit: 如果解析失败
    """
    try:
        resolved_deps = resolver.resolve(metadata)
        click.echo("✓ 依赖解析完成")
        return resolved_deps
    except DependencyConflictError as e:
        click.echo(f"✗ 依赖冲突: {str(e)}")
        raise SystemExit(1)
    except KnowledgeBaseError as e:
        click.echo(f"✗ 依赖解析错误: {str(e)}")
        raise SystemExit(1)


def _check_conflicts(conflict_detector: ConflictDetector, resolved_deps: list) -> None:
    """检查依赖版本冲突

    Args:
        conflict_detector: 冲突检测器
        resolved_deps: 解析后的依赖列表

    Raises:
        SystemExit: 如果检测到冲突
    """
    try:
        conflict_detector.check_conflicts(resolved_deps)
        click.echo("✓ 版本冲突检查通过")
    except DependencyConflictError as e:
        click.echo(f"✗ 版本冲突: {str(e)}")
        raise SystemExit(1)


def _download_dependency(downloader: PackageDownloader, dep: any, deps_dir: Path) -> None:
    """下载并设置单个依赖

    Args:
        downloader: 包下载器
        dep: 依赖对象
        deps_dir: 依赖目录

    Raises:
        SystemExit: 如果下载或解压失败
    """
    try:
        click.echo(f"  正在下载 {dep.name}@{dep.version}...")
        # downloader.download() 现在返回版本目录路径（已解压）
        version_dir = downloader.download(dep.name, dep.version, dep.git_url)
        click.echo(f"  ✓ 下载完成: {version_dir.name}")

        # 将缓存版本目录链接或复制到项目的依赖目录
        dep_dir = deps_dir / dep.name
        dep_dir.mkdir(exist_ok=True)

        # 创建指向版本目录的符号链接（如果不存在）
        version_link = dep_dir / dep.version
        if not version_link.exists():
            version_link.symlink_to(version_dir)
        click.echo(f"  ✓ 依赖已链接到 {version_link}")
    except KnowledgeBaseError as e:
        click.echo(f"  ✗ 处理依赖失败: {str(e)}")
        raise SystemExit(1)


def _process_dependencies(metadata, deps_dir: Path) -> None:
    """处理所有依赖

    Args:
        metadata: 知识库元数据
        deps_dir: 依赖目录
    """
    if not metadata.dependencies:
        click.echo("✓ 没有发现依赖")
        return

    click.echo(f"发现 {len(metadata.dependencies)} 个依赖")

    # 初始化依赖管理组件
    resolver = DependencyResolver()
    downloader = PackageDownloader()
    conflict_detector = ConflictDetector()

    # 解析依赖
    resolved_deps = _resolve_dependencies(resolver, metadata)

    # 检查版本冲突
    _check_conflicts(conflict_detector, resolved_deps)

    # 下载和解压依赖
    for i, dep in enumerate(resolved_deps, 1):
        click.echo(f"\n处理依赖 {i}/{len(resolved_deps)}: {dep.name}@{dep.version}")
        _download_dependency(downloader, dep, deps_dir)


def _setup_dependencies(knowledge_file: Path) -> Path:
    """设置依赖目录并处理依赖

    Args:
        knowledge_file: 知识库文件路径

    Returns:
        Path: 依赖目录路径
    """
    deps_dir = knowledge_file.parent / DEPS_DIR_NAME
    deps_dir.mkdir(exist_ok=True)
    return deps_dir


def _parse_knowledge_file(knowledge_file: Path):
    """解析知识库文件

    Args:
        knowledge_file: 知识库文件路径

    Returns:
        Metadata: 解析后的元数据

    Raises:
        SystemExit: 如果解析失败
    """
    try:
        parser = KnowledgeParser()
        metadata = parser.parse(knowledge_file)
        return metadata
    except DependencyConflictError as e:
        click.echo(f"依赖冲突错误: {str(e)}")
        raise SystemExit(1)
    except KnowledgeBaseError as e:
        click.echo(f"知识库错误: {str(e)}")
        raise SystemExit(1)


@click.command()
@click.option("--path", type=click.Path(exists=False), default=None, help="知识库文件路径")
def init(path: Optional[str]) -> int:
    """初始化知识库，下载所有依赖

    Returns:
        int: 0 on success, 1 on error
    """
    # 确定知识库文件路径
    knowledge_file = _determine_knowledge_file(path)

    # 验证知识库文件
    _validate_knowledge_file(knowledge_file)

    try:
        # 解析知识库文件
        metadata = _parse_knowledge_file(knowledge_file)

        # 显示元数据信息
        _display_metadata_info(metadata)

        # 开始处理依赖
        click.echo("\n开始处理依赖...")

        # 设置依赖目录
        deps_dir = _setup_dependencies(knowledge_file)

        # 处理依赖
        _process_dependencies(metadata, deps_dir)

        click.echo("\n✓ 初始化完成")
        return 0

    except DependencyConflictError as e:
        click.echo(f"依赖冲突错误: {str(e)}")
        return 1
    except KnowledgeBaseError as e:
        click.echo(f"知识库错误: {str(e)}")
        return 1
    except Exception as e:
        click.echo(f"未知错误: {str(e)}")
        return 1


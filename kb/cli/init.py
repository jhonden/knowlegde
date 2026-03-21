import click
from pathlib import Path
from typing import Optional

from kb.core import KnowledgeParser
from kb.dependency import DependencyResolver, PackageDownloader, PackageExtractor, ConflictDetector
from kb.exceptions import DependencyConflictError, KnowledgeBaseError


@click.command()
@click.option("--path", type=click.Path(exists=False), default=None, help="知识库文件路径")
def init(path: Optional[str]) -> int:
    """初始化知识库，下载所有依赖

    Returns:
        int: 0 on success, 1 on error
    """
    # 确定知识库文件路径
    if path is None:
        knowledge_file = (Path.cwd() / "Knowledge.md").resolve()
    else:
        knowledge_file = Path(path).resolve()

    # 检查文件是否存在
    if not knowledge_file.exists():
        click.echo(f"错误: 未找到知识库文件 '{knowledge_file}'")
        click.echo("请确保文件存在，或使用 --path 参数指定正确的路径")
        return 1

    # 检查路径是否为目录
    if knowledge_file.is_dir():
        click.echo(f"错误: 指定的路径 '{knowledge_file}' 是一个目录")
        click.echo("请指定Knowledge.md文件路径，而不是目录")
        return 1

    # 检查文件是否为空
    if knowledge_file.stat().st_size == 0:
        click.echo(f"错误: 知识库文件 '{knowledge_file}' 为空")
        click.echo("请确保文件包含内容")
        return 1

    # 使用KnowledgeParser解析Knowledge.md
    try:
        parser = KnowledgeParser()
        metadata = parser.parse(knowledge_file)

        # 显示元数据信息
        click.echo(f"正在解析知识库文件: {knowledge_file}")
        click.echo(f"知识库名称: {metadata.name}")
        click.echo(f"版本: {metadata.version}")
        click.echo(f"类型: {metadata.type}")
        click.echo(f"职责描述: {metadata.description}")

        # 显示依赖信息
        if metadata.dependencies:
            click.echo(f"依赖数量: {len(metadata.dependencies)}")
            for dep in metadata.dependencies:
                click.echo(f"  - {dep.name}@{dep.version} ({dep.git_url})")

        # 初始化依赖管理组件
        click.echo("\n开始处理依赖...")

        deps_dir = knowledge_file.parent / "deps"
        deps_dir.mkdir(exist_ok=True)

        # 初始化依赖管理组件
        resolver = DependencyResolver()
        downloader = PackageDownloader()
        extractor = PackageExtractor()
        conflict_detector = ConflictDetector()

        # 处理依赖
        if metadata.dependencies:
            click.echo(f"发现 {len(metadata.dependencies)} 个依赖")

            # 解析依赖
            try:
                resolved_deps = resolver.resolve(metadata.dependencies)
                click.echo("✓ 依赖解析完成")
            except DependencyConflictError as e:
                click.echo(f"✗ 依赖冲突: {str(e)}")
                return 1
            except KnowledgeBaseError as e:
                click.echo(f"✗ 依赖解析错误: {str(e)}")
                return 1

            # 检查版本冲突
            try:
                conflict_detector.check_conflicts(resolved_deps)
                click.echo("✓ 版本冲突检查通过")
            except DependencyConflictError as e:
                click.echo(f"✗ 版本冲突: {str(e)}")
                return 1

            # 下载和解压依赖
            for i, dep in enumerate(resolved_deps, 1):
                click.echo(f"\n处理依赖 {i}/{len(resolved_deps)}: {dep.name}@{dep.version}")

                try:
                    # 依赖
                    click.echo(f"  正在下载 {dep.name}@{dep.version}...")
                    downloaded_file = downloader.download(dep)
                    click.echo(f"  ✓ 下载完成: {downloaded_file.name}")

                    # 解压
                    click.echo(f"  正在解压到 {deps_dir}...")
                    extractor.extract(downloaded_file, deps_dir)
                    click.echo(f"  ✓ 解压完成")

                except KnowledgeBaseError as e:
                    click.echo(f"  ✗ 处理依赖失败: {str(e)}")
                    return 1
        else:
            click.echo("✓ 没有发现依赖")

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


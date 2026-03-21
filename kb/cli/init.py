import click
from pathlib import Path
from typing import Optional

from kb.core import KnowledgeParser


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

        # TODO: 检查缓存
        # TODO: 下载依赖
        # TODO: 解压到deps目录

        click.echo("初始化完成")
        return 0
    except Exception as e:
        click.echo(f"解析知识库文件时发生错误: {str(e)}")
        return 1


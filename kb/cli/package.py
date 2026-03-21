import tarfile
from pathlib import Path

import click

from kb.core import KnowledgeParser


@click.command()
@click.option("--src", type=click.Path(exists=False), default="src", help="源码目录")
def package(src: str) -> None:
    """打包当前知识库并生成发布包"""
    # 转换为Path对象
    src_path = Path(src)
    cwd = Path.cwd()

    # 检查src目录是否存在
    if not src_path.exists():
        click.echo(f"错误: 源码目录 '{src_path}' 不存在")
        raise click.Abort()

    if not src_path.is_dir():
        click.echo(f"错误: '{src_path}' 不是目录")
        raise click.Abort()

    # 检查Knowledge.md是否存在
    knowledge_file = cwd / "Knowledge.md"
    if not knowledge_file.exists():
        click.echo(f"错误: 未找到知识库文件 '{knowledge_file}'")
        click.echo("请确保文件存在")
        raise click.Abort()

    # 创建publish目录（如果不存在）
    publish_dir = cwd / "publish"
    publish_dir.mkdir(exist_ok=True)

    # 使用KnowledgeParser解析Knowledge.md获取名称和版本
    try:
        parser = KnowledgeParser()
        metadata = parser.parse(knowledge_file)
        name = metadata.name
        version = metadata.version

        click.echo(f"正在解析知识库文件: {knowledge_file}")
        click.echo(f"知识库名称: {name}")
        click.echo(f"版本: {version}")
    except Exception as e:
        click.echo(f"警告: 解析知识库文件失败，使用默认值: {str(e)}")
        name = "knowledge-package"
        version = "1.0.0"
        click.echo(f"知识库名称: {name}")
        click.echo(f"版本: {version}")

    # 创建发布包文件名
    package_name = f"{name}-{version}.tar.gz"
    package_path = publish_dir / package_name

    # 创建tar.gz包
    with tarfile.open(package_path, "w:gz") as tar:
        # 添加src目录下的所有文件
        for item in src_path.rglob("*"):
            if item.is_file():
                arcname = f"src/{item.relative_to(src_path)}"
                tar.add(item, arcname=arcname)

        # 添加Knowledge.md
        tar.add(knowledge_file, arcname="Knowledge.md")

    click.echo(f"打包完成: {package_path}")

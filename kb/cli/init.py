import click
from typing import Optional


@click.command()
@click.option("--path", type=click.Path(exists=False), default=None, help="知识库文件路径")
def init(path: Optional[str]):
    """初始化知识库，下载所有依赖"""
    # TODO: 解析Knowledge.md
    # TODO: 检查缓存
    # TODO: 下载依赖
    # TODO: 解压到deps目录
    click.echo("初始化完成")


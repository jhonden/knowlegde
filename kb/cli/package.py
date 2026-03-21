import click
from kb.cli.main import cli


@cli.command()
@click.option("--src", type=click.Path(exists=False), default="src", help="源码目录")
def package(src: str):
    """打包当前知识库并生成发布包"""
    # TODO: 读取.kb-package.yml配置
    # TODO: 确保src目录存在
    # TODO: 读取Knowledge.md获取名称和版本
    # TODO: 创建发布包
    # TODO: 保存到publish目录
    click.echo("打包完成")

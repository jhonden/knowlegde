import click


@click.group()
@click.version_option(version="0.1.0", prog_name="kb")
def cli():
    """Knowledge Base CLI Tool - 知识库命令行工具"""
    pass


if __name__ == "__main__":
    cli()

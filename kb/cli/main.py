import click


@click.group()
@click.version_option(version="0.1.0", prog_name="kb")
def cli():
    """Knowledge Base CLI Tool - 知识库命令行工具"""
    pass


# Import and register commands
from kb.cli.init import init as init_command  # noqa: F401, E402
from kb.cli.package import package as package_command  # noqa: F401, E402
from kb.cli.cache import cache as cache_command  # noqa: F401, E402
from kb.cli.update import check_updates, update  # noqa: F401, E402
cli.add_command(init_command)
cli.add_command(package_command)
cli.add_command(cache_command)
cli.add_command(check_updates)
cli.add_command(update)


if __name__ == "__main__":
    cli()

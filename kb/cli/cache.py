"""Cache command implementation for kb CLI."""

import click
from pathlib import Path
from typing import List, Optional

from kb.cache.manager import CacheManager, CacheInfo, LibraryInfo


# Global variable for testing
_cache_manager_instance = None


def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance."""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    return _cache_manager_instance


def set_cache_manager(manager: CacheManager) -> None:
    """Set cache manager instance for testing."""
    global _cache_manager_instance
    _cache_manager_instance = manager


@click.group()
def cache():
    """Knowledge Base cache management commands."""
    pass


@cache.command()
def info():
    """Display cache information."""
    manager = get_cache_manager()
    cache_info = manager.get_info()

    click.echo(f"Cache directory: {cache_info['cache_dir']}")
    click.echo(f"Total size: {_format_size(cache_info['total_size'])}")
    click.echo(f"Library count: {cache_info['library_count']}")
    click.echo(f"Version count: {cache_info['version_count']}")


@cache.command()
def list():
    """List all cached knowledge bases."""
    manager = get_cache_manager()
    libraries = manager.list()

    if not libraries:
        click.echo("No cached knowledge bases found.")
        return

    click.echo(f"{'Library':<30} {'Version':<15} {'Size':<10}")
    click.echo("-" * 55)

    for lib in libraries:
        click.echo(
            f"{lib['name']:<30} {lib['version']:<15} {_format_size(lib['size']):<10}"
        )


@cache.command()
@click.argument("target", required=False)
def clean(target: Optional[str]):
    """Clean cache. TARGET can be 'all', 'library:name', or 'library:version'."""
    manager = get_cache_manager()

    if not target:
        # Ask for confirmation before cleaning all
        if not click.confirm("Are you sure you want to clean all cache?"):
            click.echo("Operation cancelled.")
            return

        manager.clean_all()
        click.echo("All cache cleaned.")
        return

    if target == "all":
        if not click.confirm("Are you sure you want to clean all cache?"):
            click.echo("Operation cancelled.")
            return

        manager.clean_all()
        click.echo("All cache cleaned.")
        return

    # Handle library:name or library:version format
    if ":" in target:
        library_name, version = target.split(":", 1)
        manager.clean_version(library_name, version)
        click.echo(f"Cleaned cache for {library_name}:{version}")
    else:
        # Treat as library name
        manager.clean_library(target)
        click.echo(f"Cleaned cache for library {target}")


def _format_size(size: int) -> str:
    """Format size in bytes to human readable format.

    Args:
        size: Size in bytes.

    Returns:
        Formatted size string (B, KB, MB, GB, TB).
    """
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f}MB"
    elif size < 1024 * 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024 * 1024):.1f}GB"
    else:
        return f"{size / (1024 * 1024 * 1024 * 1024):.1f}TB"
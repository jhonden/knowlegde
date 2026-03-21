"""Cache manager implementation for library cache operations."""

import shutil
from pathlib import Path
from typing import TypedDict, List, Optional


class LibraryInfo(TypedDict):
    """Information about a cached library version."""
    name: str
    version: str
    path: Path
    size: int


class CacheInfo(TypedDict):
    """Overall cache information."""
    total_size: int
    library_count: int
    version_count: int
    cache_dir: Path


class CacheManager:
    """Manages library cache operations."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage. Defaults to ~/.kb-cache
        """
        self.cache_dir = cache_dir or Path.home() / ".kb-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_info(self) -> CacheInfo:
        """Get overall cache information.

        Returns:
            CacheInfo with total size, library count, version count, and cache directory.
        """
        total_size = 0
        library_count = 0
        version_count = 0

        for library_path in self.cache_dir.iterdir():
            if library_path.is_dir():
                library_count += 1
                for version_path in library_path.iterdir():
                    if version_path.is_dir():
                        version_count += 1
                        total_size += self._get_dir_size(version_path)

        return {
            "total_size": total_size,
            "library_count": library_count,
            "version_count": version_count,
            "cache_dir": self.cache_dir
        }

    def list(self) -> List[LibraryInfo]:
        """List all cached library versions.

        Returns:
            List of LibraryInfo objects for all cached versions.
        """
        libraries = []

        for library_path in self.cache_dir.iterdir():
            if library_path.is_dir():
                library_name = library_path.name
                for version_path in library_path.iterdir():
                    if version_path.is_dir():
                        version_name = version_path.name
                        size = self._get_dir_size(version_path)
                        libraries.append({
                            "name": library_name,
                            "version": version_name,
                            "path": version_path,
                            "size": size
                        })

        return libraries

    def clean_all(self) -> None:
        """Clean all cached libraries and versions."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def clean_library(self, library_name: str) -> None:
        """Clean a specific library and all its versions.

        Args:
            library_name: Name of the library to clean.
        """
        library_path = self.cache_dir / library_name
        if library_path.exists():
            self._remove_directory(library_path)

    def clean_version(self, library_name: str, version: str) -> None:
        """Clean a specific library version.

        Args:
            library_name: Name of the library.
            version: Version to clean.
        """
        version_path = self.cache_dir / library_name / version
        if version_path.exists():
            self._remove_directory(version_path)

    def _remove_directory(self, dir_path: Path) -> None:
        """Remove a directory safely.

        Args:
            dir_path: Path to the directory to remove.
        """
        if dir_path.exists():
            shutil.rmtree(dir_path)

    def _get_dir_size(self, dir_path: Path) -> int:
        """Calculate total size of a directory in bytes.

        Args:
            dir_path: Path to the directory.

        Returns:
            Total size in bytes.
        """
        total_size = 0
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
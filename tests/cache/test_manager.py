"""Tests for CacheManager."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from kb.cache.manager import CacheManager, LibraryInfo, CacheInfo


class TestCacheManager:
    """Test cases for CacheManager."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache_manager = CacheManager(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_init_default_cache_dir(self):
        """Test initialization with default cache directory."""
        cache_manager = CacheManager()
        assert cache_manager.cache_dir == Path.home() / ".kb-cache"

    def test_init_custom_cache_dir(self):
        """Test initialization with custom cache directory."""
        custom_dir = self.temp_dir / "custom/cache/dir"
        cache_manager = CacheManager(custom_dir)
        assert cache_manager.cache_dir == custom_dir

    def test_get_info_empty_cache(self):
        """Test get_info with empty cache."""
        info = self.cache_manager.get_info()
        expected_info: CacheInfo = {
            "total_size": 0,
            "library_count": 0,
            "version_count": 0,
            "cache_dir": self.temp_dir
        }
        assert info == expected_info

    def test_get_info_with_cached_libraries(self):
        """Test get_info with cached libraries."""
        # Create test structure
        lib1_dir = self.temp_dir / "requests"
        lib1_dir.mkdir()
        lib1_v1_dir = lib1_dir / "2.28.0"
        lib1_v1_dir.mkdir()
        (lib1_v1_dir / "file1.txt").write_text("test content")

        lib2_dir = self.temp_dir / "numpy"
        lib2_dir.mkdir()
        lib2_v1_dir = lib2_dir / "1.21.0"
        lib2_v1_dir.mkdir()
        (lib2_v1_dir / "file2.txt").write_text("test content 2")
        (lib2_v1_dir / "file3.txt").write_text("test content 3")

        info = self.cache_manager.get_info()

        assert info["library_count"] == 2
        assert info["version_count"] == 2
        assert info["total_size"] > 0
        assert info["cache_dir"] == self.temp_dir

    def test_list_empty_cache(self):
        """Test list with empty cache."""
        libraries = self.cache_manager.list()
        assert libraries == []

    def test_list_cached_libraries(self):
        """Test list with cached libraries."""
        # Create test structure
        lib1_dir = self.temp_dir / "requests"
        lib1_dir.mkdir()
        lib1_v1_dir = lib1_dir / "2.28.0"
        lib1_v1_dir.mkdir()
        (lib1_v1_dir / "file1.txt").write_text("test content")

        lib2_dir = self.temp_dir / "numpy"
        lib2_dir.mkdir()
        lib2_v1_dir = lib2_dir / "1.21.0"
        lib2_v1_dir.mkdir()
        (lib2_v1_dir / "file2.txt").write_text("test content 2")

        libraries = self.cache_manager.list()

        assert len(libraries) == 2

        # Check requests library
        requests_libs = [lib for lib in libraries if lib["name"] == "requests"]
        assert len(requests_libs) == 1
        assert requests_libs[0]["version"] == "2.28.0"
        assert requests_libs[0]["path"] == lib1_v1_dir
        assert requests_libs[0]["size"] > 0

        # Check numpy library
        numpy_libs = [lib for lib in libraries if lib["name"] == "numpy"]
        assert len(numpy_libs) == 1
        assert numpy_libs[0]["version"] == "1.21.0"
        assert numpy_libs[0]["path"] == lib2_v1_dir
        assert numpy_libs[0]["size"] > 0

    def test_clean_all(self):
        """Test clean_all operation."""
        # Create test structure
        lib_dir = self.temp_dir / "requests"
        lib_dir.mkdir()
        version_dir = lib_dir / "2.28.0"
        version_dir.mkdir()
        (version_dir / "file.txt").write_text("test")

        # Verify structure exists
        assert (self.temp_dir / "requests" / "2.28.0").exists()

        # Clean all
        self.cache_manager.clean_all()

        # Verify cache directory exists but is empty
        assert self.temp_dir.exists()
        assert not any(self.temp_dir.iterdir())

    def test_clean_library(self):
        """Test clean_library operation."""
        # Create test structure
        lib_dir = self.temp_dir / "requests"
        lib_dir.mkdir()
        lib_dir.joinpath("2.28.0").mkdir()
        lib_dir.joinpath("2.29.0").mkdir()

        # Create another library
        self.temp_dir.joinpath("numpy").mkdir()

        # Verify structure exists
        assert lib_dir.exists()
        assert len(list(lib_dir.iterdir())) == 2
        assert (self.temp_dir / "numpy").exists()

        # Clean library
        self.cache_manager.clean_library("requests")

        # Verify library is removed but other library remains
        assert not lib_dir.exists()
        assert (self.temp_dir / "numpy").exists()

    def test_clean_version(self):
        """Test clean_version operation."""
        # Create test structure
        lib_dir = self.temp_dir / "requests"
        lib_dir.mkdir()
        lib_dir.joinpath("2.28.0").mkdir()
        lib_dir.joinpath("2.29.0").mkdir()

        # Verify structure exists
        assert lib_dir.joinpath("2.28.0").exists()
        assert lib_dir.joinpath("2.29.0").exists()

        # Clean version
        self.cache_manager.clean_version("requests", "2.28.0")

        # Verify version is removed
        assert not lib_dir.joinpath("2.28.0").exists()
        assert lib_dir.joinpath("2.29.0").exists()

    def test_clean_nonexistent_library(self):
        """Test clean_library with non-existent library."""
        # Should not raise any exception
        self.cache_manager.clean_library("nonexistent")

    def test_clean_nonexistent_version(self):
        """Test clean_version with non-existent version."""
        # Should not raise any exception
        self.cache_manager.clean_version("nonexistent", "1.0.0")

    def test_get_dir_size(self):
        """Test _get_dir_size helper method."""
        # Create test directory structure
        test_dir = self.temp_dir / "test_lib"
        test_dir.mkdir()

        # Create test files
        file1 = test_dir / "file1.txt"
        file1.write_text("test content 1")

        file2 = test_dir / "file2.txt"
        file2.write_text("test content 2")

        # Calculate expected size
        expected_size = len(file1.read_text()) + len(file2.read_text())

        # Test size calculation
        assert self.cache_manager._get_dir_size(test_dir) == expected_size

    def test_init_creates_cache_dir(self):
        """Test that init creates cache directory if it doesn't exist."""
        non_existent_dir = Path("/tmp/nonexistent/cache/dir")
        cache_manager = CacheManager(non_existent_dir)

        assert non_existent_dir.exists()
        assert non_existent_dir.is_dir()

    def test_multiple_versions_same_library(self):
        """Test listing multiple versions of the same library."""
        # Create test structure
        lib_dir = self.temp_dir / "requests"
        lib_dir.mkdir()

        versions = ["2.28.0", "2.29.0", "2.30.0"]
        for version in versions:
            version_dir = lib_dir / version
            version_dir.mkdir()
            (version_dir / f"file_{version}.txt").write_text(f"content for {version}")

        libraries = self.cache_manager.list()

        # Should have 3 entries for the same library
        requests_libs = [lib for lib in libraries if lib["name"] == "requests"]
        assert len(requests_libs) == 3

        # Check all versions are present
        versions_found = {lib["version"] for lib in requests_libs}
        assert set(versions) == versions_found

    def test_nested_directory_size_calculation(self):
        """Test size calculation with nested directories."""
        # Create nested structure
        root_dir = self.temp_dir / "test_lib"
        root_dir.mkdir()

        # Create subdirectory
        subdir = root_dir / "subdir"
        subdir.mkdir()

        # Create files in root and subdir
        (root_dir / "root_file.txt").write_text("root content")
        (subdir / "sub_file.txt").write_text("sub content")

        # Calculate size
        size = self.cache_manager._get_dir_size(root_dir)

        # Should include both files
        assert size == len("root content") + len("sub content")
"""Tests for kb cache CLI commands."""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from kb.cli.main import cli
from kb.cli.cache import get_cache_manager, set_cache_manager
from kb.cache.manager import CacheManager


class TestCacheCommands:
    """Test cache command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        # Reset cache manager instance after each test
        set_cache_manager(None)

    def test_cache_list(self):
        """Test cache list command."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.list.return_value = [
            {
                "name": "test-lib",
                "version": "1.0.0",
                "path": Path(self.temp_dir) / "test-lib" / "1.0.0",
                "size": 1024,
            },
            {
                "name": "another-lib",
                "version": "2.1.0",
                "path": Path(self.temp_dir) / "another-lib" / "2.1.0",
                "size": 2048,
            },
        ]
        set_cache_manager(mock_instance)

        result = self.runner.invoke(cli, ["cache", "list"])

        assert result.exit_code == 0
        assert "test-lib" in result.output
        assert "another-lib" in result.output
        assert "1.0.0" in result.output
        assert "2.1.0" in result.output
        assert "1.0KB" in result.output
        assert "2.0KB" in result.output

    def test_cache_info(self):
        """Test cache info command."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get_info.return_value = {
            "total_size": 3072,
            "library_count": 2,
            "version_count": 3,
            "cache_dir": Path(self.temp_dir),
        }
        set_cache_manager(mock_instance)

        result = self.runner.invoke(cli, ["cache", "info"])

        assert result.exit_code == 0
        assert "Cache directory:" in result.output
        assert "Total size:" in result.output
        assert "3.0KB" in result.output
        assert "Library count:" in result.output
        assert "2" in result.output
        assert "Version count:" in result.output
        assert "3" in result.output

    def test_cache_clean_all(self):
        """Test cache clean all command."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.clean_all.return_value = None
        set_cache_manager(mock_instance)

        # Mock click.confirm to always return True
        with patch("click.confirm", return_value=True):
            result = self.runner.invoke(cli, ["cache", "clean", "all"])

        assert result.exit_code == 0
        mock_instance.clean_all.assert_called_once()
        assert "All cache cleaned." in result.output

    def test_cache_clean_library(self):
        """Test cache clean library command."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.clean_library.return_value = None
        set_cache_manager(mock_instance)

        result = self.runner.invoke(cli, ["cache", "clean", "test-lib"])

        assert result.exit_code == 0
        mock_instance.clean_library.assert_called_once_with("test-lib")
        assert "Cleaned cache for library test-lib" in result.output

    def test_cache_clean_version(self):
        """Test cache clean version command."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.clean_version.return_value = None
        set_cache_manager(mock_instance)

        result = self.runner.invoke(cli, ["cache", "clean", "test-lib:1.0.0"])

        assert result.exit_code == 0
        mock_instance.clean_version.assert_called_once_with("test-lib", "1.0.0")
        assert "Cleaned cache for test-lib:1.0.0" in result.output

    def test_cache_clean_no_target_confirm_yes(self):
        """Test cache clean without target with confirmed yes."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.clean_all.return_value = None
        set_cache_manager(mock_instance)

        # Mock click.confirm to return True
        with patch("click.confirm", return_value=True):
            result = self.runner.invoke(cli, ["cache", "clean"])

        assert result.exit_code == 0
        mock_instance.clean_all.assert_called_once()
        assert "All cache cleaned." in result.output

    def test_cache_clean_no_target_confirm_no(self):
        """Test cache clean without target with confirmed no."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.clean_all.return_value = None
        set_cache_manager(mock_instance)

        # Mock click.confirm to return False
        with patch("click.confirm", return_value=False):
            result = self.runner.invoke(cli, ["cache", "clean"])

        assert result.exit_code == 0
        mock_instance.clean_all.assert_not_called()
        assert "Operation cancelled." in result.output

    def test_cache_clean_all_confirm_no(self):
        """Test cache clean all with confirmed no."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.clean_all.return_value = None
        set_cache_manager(mock_instance)

        # Mock click.confirm to return False
        with patch("click.confirm", return_value=False):
            result = self.runner.invoke(cli, ["cache", "clean", "all"])

        assert result.exit_code == 0
        mock_instance.clean_all.assert_not_called()
        assert "Operation cancelled." in result.output

    def test_cache_list_empty(self):
        """Test cache list command with empty cache."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.list.return_value = []
        set_cache_manager(mock_instance)

        result = self.runner.invoke(cli, ["cache", "list"])

        assert result.exit_code == 0
        assert "No cached knowledge bases found." in result.output

    def test_cache_format_sizes(self):
        """Test various size formatting scenarios."""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.list.return_value = [
            {"name": "small", "version": "1.0.0", "path": Path(self.temp_dir) / "small" / "1.0.0", "size": 512},
            {"name": "medium", "version": "1.0.0", "path": Path(self.temp_dir) / "medium" / "1.0.0", "size": 1536},
            {"name": "large", "version": "1.0.0", "path": Path(self.temp_dir) / "large" / "1.0.0", "size": 1048576},
        ]
        set_cache_manager(mock_instance)

        result = self.runner.invoke(cli, ["cache", "list"])

        assert result.exit_code == 0
        assert "512B" in result.output
        assert "1.5KB" in result.output
        assert "1.0MB" in result.output
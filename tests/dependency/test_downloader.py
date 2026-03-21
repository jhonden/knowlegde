"""知识库依赖下载器测试。"""

import pytest
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock

from kb.dependency.downloader import PackageDownloader
from kb.exceptions import KnowledgeBaseError


class TestPackageDownloader:
    """PackageDownloader 测试类。"""

    @pytest.fixture
    def downloader(self):
        """创建测试用的下载器实例。"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/tmp")
            return PackageDownloader(cache_dir=Path("/tmp/test-cache"))

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """临时缓存目录。"""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir

    def test_download_package_invalid_url(self, downloader):
        """测试无效URL下载失败。"""
        invalid_url = "https://invalid-url.com/owner/repo"

        with pytest.raises(KnowledgeBaseError, match="只支持GitHub和GitLab"):
            downloader.download("test-package", "1.0.0", invalid_url)

    def test_build_download_url_github(self, downloader):
        """测试GitHub URL构建。"""
        github_url = "https://github.com/owner/repo"
        result = downloader._build_download_url(github_url, "test-package", "1.0.0")

        expected = "https://github.com/owner/repo/releases/download/v1.0.0/test-package.tar.gz"
        assert result == expected

    def test_build_download_url_gitlab(self, downloader):
        """测试GitLab URL构建。"""
        gitlab_url = "https://gitlab.com/owner/repo"
        result = downloader._build_download_url(gitlab_url, "test-package", "1.0.0")

        expected = "https://gitlab.com/owner/repo/-/archive/v1.0.0/repo-v1.0.0.tar.gz"
        assert result == expected

    @patch('kb.dependency.downloader.requests.get')
    def test_download_package_success(self, mock_get, downloader, temp_cache_dir):
        """测试成功下载包。"""
        # 更新下载器的缓存目录
        downloader.cache_dir = temp_cache_dir

        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b"file content"]
        mock_get.return_value = mock_response

        # 调用下载方法
        result = downloader.download("test-package", "1.0.0", "https://github.com/owner/repo")

        # 验证结果
        assert result.exists()
        assert "test-package_1.0.0_" in result.name
        assert result.suffix == ".gz"

        # 验证缓存文件内容
        with open(result, 'rb') as f:
            content = f.read()
            assert content == b"file content"

    @patch('kb.dependency.downloader.requests.get')
    def test_download_package_force_redownload(self, mock_get, downloader, temp_cache_dir):
        """测试强制重新下载。"""
        # 更新下载器的缓存目录
        downloader.cache_dir = temp_cache_dir

        # 创建一个存在的缓存文件
        cache_file = temp_cache_dir / "test_1.0_abcdef.tar.gz"
        cache_file.write_text("old content")

        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b"new content"]
        mock_get.return_value = mock_response

        # 强制重新下载
        result = downloader.download("test", "1.0.0", "https://github.com/owner/repo", force=True)

        # 验证结果（返回新的文件）
        assert result.exists()
        with open(result, 'rb') as f:
            content = f.read()
            assert content == b"new content"

    @patch('kb.dependency.downloader.requests.get')
    def test_download_package_network_error(self, mock_get, downloader, temp_cache_dir):
        """测试网络错误时清理部分下载文件。"""
        # 更新下载器的缓存目录
        downloader.cache_dir = temp_cache_dir

        # 模拟网络错误
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # 验证抛出异常
        with pytest.raises(KnowledgeBaseError, match="下载失败"):
            downloader.download("test-package", "1.0.0", "https://github.com/owner/repo")

    def test_validate_inputs(self, downloader):
        """测试输入验证。"""
        # 测试空包名
        with pytest.raises(KnowledgeBaseError, match="包名不能为空"):
            downloader._validate_inputs("", "1.0.0", "https://github.com/owner/repo")

        # 测试无效包名
        with pytest.raises(KnowledgeBaseError, match="包名格式无效"):
            downloader._validate_inputs("123package", "1.0.0", "https://github.com/owner/repo")

        # 测试空版本号
        with pytest.raises(KnowledgeBaseError, match="版本号不能为空"):
            downloader._validate_inputs("package", "", "https://github.com/owner/repo")

        # 测试无效版本号
        with pytest.raises(KnowledgeBaseError, match="版本号格式无效"):
            downloader._validate_inputs("package", "invalid", "https://github.com/owner/repo")

        # 测试空URL
        with pytest.raises(KnowledgeBaseError, match="Git URL不能为空"):
            downloader._validate_inputs("package", "1.0.0", "")

        # 测试无效协议URL
        with pytest.raises(KnowledgeBaseError, match="Git URL格式无效"):
            downloader._validate_inputs("package", "1.0.0", "ftp://github.com/owner/repo")

        # 测试不支持的平台
        with pytest.raises(KnowledgeBaseError, match="只支持GitHub和GitLab"):
            downloader._validate_inputs("package", "1.0.0", "https://bitbucket.com/owner/repo")

        # 测试有效输入应该通过
        downloader._validate_inputs("my-package", "1.0.0", "https://github.com/owner/repo")

    def test_build_cache_path(self, downloader, temp_cache_dir):
        """测试缓存路径构建。"""
        downloader.cache_dir = temp_cache_dir

        # 测试特殊字符的处理
        path = downloader._build_cache_path("my-package@#$", "1.0.0", "https://github.com/owner/repo")
        assert "my-package___" in path.name  # 特殊字符被替换为下划线
        assert path.parent == temp_cache_dir

    def test_validate_cache_dir(self, downloader):
        """测试缓存目录验证。"""
        # 测试相对路径（应该失败）
        with pytest.raises(KnowledgeBaseError, match="缓存目录必须是绝对路径"):
            downloader._validate_cache_dir(Path("relative/path"))

        # 测试路径遍历攻击（应该失败）
        with pytest.raises(KnowledgeBaseError, match="不安全的缓存目录路径"):
            downloader._validate_cache_dir(Path("/safe/../../../etc/passwd"))

        # 测试正常绝对路径（应该通过）
        downloader._validate_cache_dir(Path("/safe/directory"))
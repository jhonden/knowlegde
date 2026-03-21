"""知识库依赖下载器测试。"""

import pytest
import requests
import tarfile
import tempfile
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

    def _create_test_tarball(self, content_dict, output_path):
        """创建测试用的 tar.gz 文件。

        Args:
            content_dict: 文件路径到内容的字典
            output_path: 输出的 tar.gz 文件路径
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建文件
            for file_path, content in content_dict.items():
                file = temp_path / file_path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(content)

            # 创建 tar.gz
            with tarfile.open(output_path, 'w:gz') as tar:
                for file_path in content_dict.keys():
                    tar.add(temp_path / file_path, arcname=file_path)

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
    def test_download_package_success(self, mock_get, downloader, temp_cache_dir, tmp_path):
        """测试成功下载包并解压到版本目录。"""
        # 更新下载器的缓存目录
        downloader.cache_dir = temp_cache_dir

        # 创建测试 tar.gz 文件
        tarball_path = tmp_path / "test.tar.gz"
        self._create_test_tarball(
            {"content.md": "test content", "src/file.py": "print('hello')"},
            tarball_path
        )

        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [tarball_path.read_bytes()]
        mock_get.return_value = mock_response

        # 调用下载方法
        result = downloader.download("test-package", "1.0.0", "https://github.com/owner/repo")

        # 验证结果：应该返回版本目录路径
        assert result.is_dir()
        assert result.name == "1.0.0"
        assert result.parent.name == "test-package"
        assert result.parent == temp_cache_dir / "test-package"

        # 验证目录包含解压的文件
        assert (result / "content.md").exists()
        assert (result / "src" / "file.py").exists()
        assert (result / "content.md").read_text() == "test content"

    @patch('kb.dependency.downloader.requests.get')
    def test_download_package_cache_hit(self, mock_get, downloader, temp_cache_dir):
        """测试缓存命中时不重新下载。"""
        # 更新下载器的缓存目录
        downloader.cache_dir = temp_cache_dir

        # 创建已存在的版本目录
        version_dir = temp_cache_dir / "test-package" / "1.0.0"
        version_dir.mkdir(parents=True)
        (version_dir / "existing.txt").write_text("existing content")

        # 调用下载方法（不应该触发网络请求）
        result = downloader.download("test-package", "1.0.0", "https://github.com/owner/repo")

        # 验证结果：返回已存在的目录
        assert result == version_dir
        assert (result / "existing.txt").exists()
        assert (result / "existing.txt").read_text() == "existing content"

        # 验证没有发起网络请求
        mock_get.assert_not_called()

    @patch('kb.dependency.downloader.requests.get')
    def test_download_package_force_redownload(self, mock_get, downloader, temp_cache_dir, tmp_path):
        """测试强制重新下载。"""
        # 更新下载器的缓存目录
        downloader.cache_dir = temp_cache_dir

        # 创建已存在的版本目录
        version_dir = temp_cache_dir / "test" / "1.0.0"
        version_dir.mkdir(parents=True)
        (version_dir / "old.txt").write_text("old content")

        # 创建新的测试 tar.gz 文件
        tarball_path = tmp_path / "new.tar.gz"
        self._create_test_tarball(
            {"new.txt": "new content"},
            tarball_path
        )

        # 模拟成功的HTTP响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [tarball_path.read_bytes()]
        mock_get.return_value = mock_response

        # 强制重新下载
        result = downloader.download("test", "1.0.0", "https://github.com/owner/repo", force=True)

        # 验证结果：应该有新内容
        assert result == version_dir
        assert (result / "new.txt").exists()
        assert (result / "new.txt").read_text() == "new content"
        # 旧文件应该被删除
        assert not (result / "old.txt").exists()

        # 验证发起了网络请求
        mock_get.assert_called_once()

    @patch('kb.dependency.downloader.requests.get')
    def test_download_package_network_error(self, mock_get, downloader, temp_cache_dir):
        """测试网络错误时不创建目录。"""
        # 更新下载器的缓存目录
        downloader.cache_dir = temp_cache_dir

        # 模拟网络错误
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # 验证抛出异常
        with pytest.raises(KnowledgeBaseError, match="下载失败"):
            downloader.download("test-package", "1.0.0", "https://github.com/owner/repo")

        # 验证没有创建版本目录
        version_dir = temp_cache_dir / "test-package" / "1.0.0"
        assert not version_dir.exists()

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

    def test_build_version_dir_path(self, downloader, temp_cache_dir):
        """测试版本目录路径构建。"""
        downloader.cache_dir = temp_cache_dir

        # 测试正常路径
        path = downloader._build_version_dir_path("my-package", "1.0.0")
        assert path == temp_cache_dir / "my-package" / "1.0.0"

        # 测试特殊字符的处理
        path = downloader._build_version_dir_path("my-package@#$", "1.0.0")
        # 特殊字符被替换为下划线，但path.name是版本号，path.parent.name才是包名
        assert path.name == "1.0.0"
        assert path.parent.name == "my-package___"
        assert path.parent.parent == temp_cache_dir

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

    def test_extract_downloaded_package_security(self, downloader, temp_cache_dir, tmp_path):
        """测试解压时的安全检查。"""
        # 创建一个包含恶意路径的 tar.gz
        tarball_path = tmp_path / "malicious.tar.gz"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            safe_file = temp_path / "safe.txt"
            safe_file.write_text("safe content")

            with tarfile.open(tarball_path, 'w:gz') as tar:
                tar.add(safe_file, arcname="safe.txt")
                # 尝试添加路径遍历攻击（虽然这会被我们的安全检查阻止）
                import tarfile as tf
                info = tf.TarInfo(name="../etc/passwd")
                tar.addfile(info)

        version_dir = temp_cache_dir / "test" / "1.0.0"
        version_dir.mkdir(parents=True)

        # 验证抛出安全错误
        with pytest.raises(KnowledgeBaseError, match="不安全路径"):
            downloader._extract_downloaded_package(tarball_path, version_dir)

    @patch('kb.dependency.downloader.requests.get')
    def test_multiple_versions_same_package(self, mock_get, downloader, temp_cache_dir, tmp_path):
        """测试同一包的多个版本。"""
        downloader.cache_dir = temp_cache_dir

        # 创建两个版本的 tar.gz
        tarball_v1 = tmp_path / "v1.tar.gz"
        tarball_v2 = tmp_path / "v2.tar.gz"
        self._create_test_tarball({"file.txt": "version 1"}, tarball_v1)
        self._create_test_tarball({"file.txt": "version 2"}, tarball_v2)

        # 模拟HTTP响应
        def mock_response_func(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            if "1.0.0" in args[0]:
                mock_response.iter_content.return_value = [tarball_v1.read_bytes()]
            else:
                mock_response.iter_content.return_value = [tarball_v2.read_bytes()]
            return mock_response

        mock_get.side_effect = mock_response_func

        # 下载两个版本
        v1_dir = downloader.download("test", "1.0.0", "https://github.com/owner/repo")
        v2_dir = downloader.download("test", "2.0.0", "https://github.com/owner/repo")

        # 验证两个版本都存在
        assert v1_dir.exists()
        assert v2_dir.exists()
        assert v1_dir != v2_dir
        assert (v1_dir / "file.txt").read_text() == "version 1"
        assert (v2_dir / "file.txt").read_text() == "version 2"

        # 验证目录结构
        assert v1_dir.parent == temp_cache_dir / "test"
        assert v2_dir.parent == temp_cache_dir / "test"

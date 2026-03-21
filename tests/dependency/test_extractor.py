"""测试包解压器。"""

import os
import tempfile
import tarfile
from pathlib import Path
from typing import Optional

import pytest

from kb.dependency.extractor import PackageExtractor
from kb.exceptions import KnowledgeBaseError


class TestPackageExtractor:
    """测试 PackageExtractor 类。"""

    def setup_method(self):
        """每个测试方法执行前的设置。"""
        self.extractor = PackageExtractor()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_package_name = "test_package"

    def teardown_method(self):
        """每个测试方法执行后的清理。"""
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_package(self, package_name: str, files: Optional[list] = None) -> Path:
        """创建测试用的tar.gz包。

        Args:
            package_name: 包名
            files: 要包含的文件列表

        Returns:
            包文件路径
        """
        if files is None:
            files = ["README.md", "src/main.py", "config/settings.json"]

        # 创建临时包文件
        package_path = self.temp_dir / f"{package_name}.tar.gz"

        with tarfile.open(package_path, 'w:gz') as tar:
            # 添加文件
            for file_path in files:
                # 创建临时文件
                temp_file = self.temp_dir / file_path
                temp_file.parent.mkdir(parents=True, exist_ok=True)
                temp_file.write_text(f"Content of {file_path}")
                tar.add(temp_file, arcname=file_path)

        return package_path

    def create_corrupted_package(self, package_name: str) -> Path:
        """创建损坏的包文件。

        Args:
            package_name: 包名

        Returns:
            包文件路径
        """
        package_path = self.temp_dir / f"{package_name}.tar.gz"
        # 写入无效的tar.gz内容
        package_path.write_text("This is not a valid tar.gz file")
        return package_path

    def test_extract_package(self):
        """测试正常解压包。"""
        # Arrange
        package_path = self.create_test_package(self.test_package_name)
        target_dir = self.temp_dir / "extracted"

        # Act
        self.extractor.extract(package_path, target_dir)

        # Assert
        assert target_dir.exists()
        assert (target_dir / "README.md").exists()
        assert (target_dir / "src/main.py").exists()
        assert (target_dir / "config/settings.json").exists()

        # 验证文件内容
        assert (target_dir / "README.md").read_text() == "Content of README.md"
        assert (target_dir / "src/main.py").read_text() == "Content of src/main.py"
        assert (target_dir / "config/settings.json").read_text() == "Content of config/settings.json"

    def test_extract_package_with_complex_structure(self):
        """测试解压包含复杂目录结构的包。"""
        # Arrange
        files = [
            "kb/__init__.py",
            "kb/core/models.py",
            "kb/core/parser.py",
            "kb/dependency/downloader.py",
            "kb/cli/utils.py",
            "tests/test_core.py",
            "pyproject.toml",
            "README.md"
        ]
        package_path = self.create_test_package("complex_package", files)
        target_dir = self.temp_dir / "extracted_complex"

        # Act
        self.extractor.extract(package_path, target_dir)

        # Assert
        assert target_dir.exists()
        assert (target_dir / "kb" / "__init__.py").exists()
        assert (target_dir / "kb" / "core" / "models.py").exists()
        assert (target_dir / "tests" / "test_core.py").exists()

    def test_extract_nonexistent_package(self):
        """测试解压不存在的包。"""
        # Arrange
        nonexistent_path = self.temp_dir / "nonexistent.tar.gz"
        target_dir = self.temp_dir / "extract_target"

        # Act & Assert
        with pytest.raises(KnowledgeBaseError) as exc_info:
            self.extractor.extract(nonexistent_path, target_dir)

        assert "发布包文件不存在" in str(exc_info.value)
        assert str(nonexistent_path) in str(exc_info.value)

    def test_extract_path_is_directory(self):
        """测试解压路径是目录而非文件。"""
        # Arrange
        dir_path = self.temp_dir / "directory"
        dir_path.mkdir()
        target_dir = self.temp_dir / "extract_target"

        # Act & Assert
        with pytest.raises(KnowledgeBaseError) as exc_info:
            self.extractor.extract(dir_path, target_dir)

        assert "发布包路径必须是文件" in str(exc_info.value)

    def test_extract_wrong_format(self):
        """测试解压非.tar.gz格式的文件。"""
        # Arrange
        wrong_path = self.temp_dir / "wrong.txt"
        wrong_path.write_text("This is a text file, not a tar.gz")
        target_dir = self.temp_dir / "extract_target"

        # Act & Assert
        with pytest.raises(KnowledgeBaseError) as exc_info:
            self.extractor.extract(wrong_path, target_dir)

        assert "只支持 .tar.gz 格式的发布包" in str(exc_info.value)

    def test_extract_corrupted_package(self):
        """测试解压损坏的包。"""
        # Arrange
        package_path = self.create_corrupted_package("corrupted")
        target_dir = self.temp_dir / "extract_target"

        # Act & Assert
        with pytest.raises(KnowledgeBaseError) as exc_info:
            self.extractor.extract(package_path, target_dir)

        assert "无法读取tar.gz文件" in str(exc_info.value)

    def test_extract_target_dir_creation(self):
        """测试自动创建目标目录。"""
        # Arrange
        package_path = self.create_test_package(self.test_package_name)
        target_dir = self.temp_dir / "nested" / "path" / "to" / "extract"

        # Act
        self.extractor.extract(package_path, target_dir)

        # Assert
        assert target_dir.exists()
        assert (target_dir / "README.md").exists()

    def test_extract_with_empty_files(self):
        """测试解压包含空文件的包。"""
        # Arrange
        files = ["empty.txt", "file_with_content.txt"]
        package_path = self.create_test_package("empty_package", files)

        # 修改第一个文件为空
        empty_file = self.temp_dir / "empty.txt"
        empty_file.write_text("")

        # 重新创建包
        with tarfile.open(package_path, 'w:gz') as tar:
            empty_file = self.temp_dir / "empty.txt"
            tar.add(empty_file, arcname="empty.txt")

            content_file = self.temp_dir / "file_with_content.txt"
            content_file.write_text("Hello World")
            tar.add(content_file, arcname="file_with_content.txt")

        target_dir = self.temp_dir / "extracted_empty"

        # Act
        self.extractor.extract(package_path, target_dir)

        # Assert
        assert target_dir.exists()
        assert (target_dir / "empty.txt").exists()
        assert (target_dir / "file_with_content.txt").exists()
        assert (target_dir / "empty.txt").read_text() == ""
        assert (target_dir / "file_with_content.txt").read_text() == "Hello World"

    def test_extract_tarfile_error(self):
        """测试tarfile打开失败的情况。"""
        # Arrange
        package_path = self.temp_dir / "corrupted.tar.gz"
        # 创建一个会触发tarfile.ReadError的文件
        package_path.write_bytes(b"not a valid tar file")

        target_dir = self.temp_dir / "extract_target"

        # Act & Assert
        with pytest.raises(KnowledgeBaseError) as exc_info:
            self.extractor.extract(package_path, target_dir)

        assert "无法读取tar.gz文件" in str(exc_info.value)

    def test_extract_path_traversal_attack(self):
        """测试路径遍历攻击防护。"""
        # Arrange
        # 创建包含恶意路径的包
        package_path = self.temp_dir / "malicious.tar.gz"

        with tarfile.open(package_path, 'w:gz') as tar:
            # 尝试添加遍历路径
            malicious_file = self.temp_dir / "malicious.txt"
            malicious_file.write_text("Malicious content")

            # 添加包含遍历序列的文件
            tar.add(malicious_file, arcname="../escape.txt")

            # 添加绝对路径的文件
            another_file = self.temp_dir / "another.txt"
            another_file.write_text("Another file")
            tar.add(another_file, arcname="/absolute/path/file.txt")

        target_dir = self.temp_dir / "safe_extract"

        # Act & Assert
        with pytest.raises(KnowledgeBaseError) as exc_info:
            self.extractor.extract(package_path, target_dir)

        assert "发布包包含不安全路径" in str(exc_info.value)

    def test_extract_relative_path_escape_attempt(self):
        """测试相对路径逃逸尝试防护。"""
        # Arrange
        package_path = self.temp_dir / "escape_attempt.tar.gz"

        with tarfile.open(package_path, 'w:gz') as tar:
            # 创建文件
            temp_file = self.temp_dir / "test.txt"
            temp_file.write_text("Test content")

            # 尝试从目标目录逃逸
            tar.add(temp_file, arcname="../../../etc/passwd")

        target_dir = self.temp_dir / "safe_dir"

        # Act & Assert
        with pytest.raises(KnowledgeBaseError) as exc_info:
            self.extractor.extract(package_path, target_dir)

        # 检查错误消息中是否包含相关信息（不关心具体哪个错误先触发）
        error_message = str(exc_info.value)
        assert "发布包包含不安全路径" in error_message or "发布包包含试图逃逸目标目录的路径" in error_message
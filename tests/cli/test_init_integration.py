"""kb init命令集成测试"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import pytest
from click.testing import CliRunner

from kb.cli.init import init, DEFAULT_KNOWLEDGE_FILE, DEPS_DIR_NAME
from kb.core import KnowledgeParser, KnowledgeMetadata, Dependency
from kb.dependency import DependencyResolver, PackageDownloader, PackageExtractor, ConflictDetector
from kb.exceptions import DependencyConflictError, KnowledgeBaseError


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_knowledge_md(temp_dir):
    """创建示例知识库文件"""
    content = """# 知识库名称: 测试知识库
## 版本: 1.0.0
### 类型: Python库
#### 职责描述: 这是一个测试知识库

## 依赖
- 依赖名称: test-package
  版本: ^1.0.0
  Git URL: https://github.com/example/test-package.git
- 依赖名称: another-package
  版本: ^2.0.0
  Git URL: https://github.com/example/another-package.git
"""

    knowledge_file = temp_dir / "Knowledge.md"
    knowledge_file.write_text(content)
    return knowledge_file


class TestInitIntegration:
    """kb init命令集成测试"""

    @staticmethod
    def create_dependency(name: str, version: str, git_url: str):
        """创建依赖对象"""
        return Dependency(
            name=name,
            version=version,
            git_url=git_url
        )

    def test_init_with_dependencies(self, temp_dir, sample_knowledge_md):
        """测试有依赖的初始化"""
        runner = CliRunner()

        # 创建更规范的Mock对象
        mock_parser = Mock(spec=KnowledgeParser)
        mock_resolver = Mock(spec=DependencyResolver)
        mock_downloader = Mock(spec=PackageDownloader)
        mock_extractor = Mock(spec=PackageExtractor)
        mock_conflict_detector = Mock(spec=ConflictDetector)

        # 设置mock返回值
        mock_metadata = KnowledgeMetadata(
            name="测试知识库",
            version="1.0.0",
            type="Python库",
            description="这是一个测试知识库",
            dependencies=[
                self.create_dependency("test-package", "1.0.0", "https://github.com/example/test-package.git"),
                self.create_dependency("another-package", "2.0.0", "https://github.com/example/another-package.git")
            ]
        )
        mock_parser.return_value.parse.return_value = mock_metadata

        # 模拟依赖解析
        resolved_deps = mock_metadata.dependencies
        mock_resolver.return_value.resolve.return_value = resolved_deps

        # 模拟下载和解压
        mock_downloader.return_value.download.return_value = Path("mock_package.tar.gz")
        mock_extractor.return_value.extract.return_value = None

        # 应用patch - 使用正确的路径
        with patch('kb.core.KnowledgeParser', return_value=mock_parser), \
             patch('kb.dependency.DependencyResolver', return_value=mock_resolver), \
             patch('kb.dependency.PackageDownloader', return_value=mock_downloader), \
             patch('kb.dependency.PackageExtractor', return_value=mock_extractor), \
             patch('kb.dependency.ConflictDetector', return_value=mock_conflict_detector):

            # 运行命令 - 直接调用 init 命令，使用 --path 参数
            result = runner.invoke(init, ["--path", str(sample_knowledge_md)])

            # 验证结果 - 应该成功退出码为0
            assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"

            # 验证组件调用
            mock_parser.assert_called_once_with()
            mock_parser.return_value.parse.assert_called_once_with(sample_knowledge_md)
            mock_resolver.assert_called_once_with()
            mock_resolver.return_value.resolve.assert_called_once_with(mock_metadata.dependencies)
            mock_conflict_detector.assert_called_once_with()
            mock_conflict_detector.return_value.check_conflicts.assert_called_once_with(resolved_deps)

            # 验证下载和解压调用
            assert mock_downloader.return_value.download.call_count == 2  # 两个依赖
            mock_extractor.return_value.extract.assert_called()

            # 验证deps目录创建
            deps_dir = sample_knowledge_md.parent / DEPS_DIR_NAME
            assert deps_dir.exists(), f"Dependencies directory {deps_dir} was not created"

    def test_init_with_version_conflict(self, temp_dir, sample_knowledge_md):
        """测试版本冲突报错"""
        runner = CliRunner()

        # 创建Mock对象
        mock_parser = Mock(spec=KnowledgeParser)
        mock_resolver = Mock(spec=DependencyResolver)

        # 设置mock返回值
        mock_metadata = KnowledgeMetadata(
            name="测试知识库",
            version="1.0.0",
            type="Python库",
            description="这是一个测试知识库",
            dependencies=[
                self.create_dependency("conflict-package", "1.0.0", "https://github.com/example/conflict-package.git")
            ]
        )
        mock_parser.return_value.parse.return_value = mock_metadata

        # 模拟依赖冲突
        conflict_error = DependencyConflictError(
            "版本冲突: conflict-package 版本要求 ^1.0.0 但系统要求 ^2.0.0"
        )
        mock_resolver.return_value.resolve.side_effect = conflict_error

        # 应用patch
        with patch('kb.core.KnowledgeParser', return_value=mock_parser), \
             patch('kb.dependency.DependencyResolver', return_value=mock_resolver):

            # 运行命令 - 直接调用 init 命令，使用 --path 参数
            result = runner.invoke(init, ["--path", str(sample_knowledge_md)])

            # 验证结果
            assert result.exit_code == 1, f"Expected exit code 1, got {result.exit_code}. Output: {result.output}"

            # 验证具体的错误消息
            assert "✗ 依赖冲突" in result.output
            assert "conflict-package" in result.output
            assert "^1.0.0" in result.output
            assert "版本冲突" in result.output

            # 验证组件调用
            mock_parser.assert_called_once_with()
            mock_parser.return_value.parse.assert_called_once_with(sample_knowledge_md)
            mock_resolver.assert_called_once_with()
            mock_resolver.return_value.resolve.assert_called_once_with(mock_metadata.dependencies)

    def test_init_with_empty_dependencies(self, temp_dir):
        """测试没有依赖的初始化"""
        # 创建没有依赖的知识库文件
        content = """# 知识库名称: 测试知识库
## 版本: 1.0.0
### 类型: Python库
#### 职责描述: 这是一个测试知识库

## 依赖
"""

        knowledge_file = temp_dir / "Knowledge.md"
        knowledge_file.write_text(content)

        runner = CliRunner()

        # 创建Mock对象
        mock_parser = Mock(spec=KnowledgeParser)

        # 设置mock返回值
        mock_metadata = KnowledgeMetadata(
            name="测试知识库",
            version="1.0.0",
            type="Python库",
            description="这是一个测试知识库",
            dependencies=[]
        )
        mock_parser.return_value.parse.return_value = mock_metadata

        # 应用patch
        with patch('kb.core.KnowledgeParser', return_value=mock_parser):

            # 运行命令
            result = runner.invoke(init, ["--path", str(knowledge_file)])

            # 验证结果
            assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"

            # 验元数据解析调用
            mock_parser.assert_called_once_with()
            mock_parser.return_value.parse.assert_called_once_with(knowledge_file)

    def test_init_with_parse_error(self, temp_dir):
        """测试解析错误"""
        # 创建一个错误的知识库文件
        content = "这是一个无效的知识库文件"
        knowledge_file = temp_dir / "Knowledge.md"
        knowledge_file.write_text(content)

        runner = CliRunner()

        # 创建Mock对象
        mock_parser = Mock(spec=KnowledgeParser)

        # 模拟解析错误
        parse_error = KnowledgeBaseError("解析错误: 无法解析知识库文件格式")
        mock_parser.return_value.parse.side_effect = parse_error

        # 应用patch
        with patch('kb.core.KnowledgeParser', return_value=mock_parser):

            # 运行命令
            result = runner.invoke(init, ["--path", str(knowledge_file)])

            # 验证结果 - 应该返回错误退出码1
            assert result.exit_code == 1, f"Expected exit code 1, got {result.exit_code}. Output: {result.output}"

            # 验证具体的错误消息
            assert "✗ 知识库错误" in result.output
            assert "解析错误" in result.output

            # 验证组件调用
            mock_parser.assert_called_once_with()
            mock_parser.return_value.parse.assert_called_once_with(knowledge_file)

    def test_init_with_download_error(self, temp_dir, sample_knowledge_md):
        """测试下载错误"""
        runner = CliRunner()

        # 创建Mock对象
        mock_parser = Mock(spec=KnowledgeParser)
        mock_resolver = Mock(spec=DependencyResolver)
        mock_downloader = Mock(spec=PackageDownloader)
        mock_extractor = Mock(spec=PackageExtractor)
        mock_conflict_detector = Mock(spec=ConflictDetector)

        # 设置mock返回值
        mock_metadata = KnowledgeMetadata(
            name="测试知识库",
            version="1.0.0",
            type="Python库",
            description="这是一个测试知识库",
            dependencies=[
                self.create_dependency("test-package", "1.0.0", "https://github.com/example/test-package.git")
            ]
        )
        mock_parser.return_value.parse.return_value = mock_metadata

        # 模拟依赖解析
        resolved_deps = mock_metadata.dependencies
        mock_resolver.return_value.resolve.return_value = resolved_deps

        # 模拟下载错误
        download_error = KnowledgeBaseError("网络连接失败: 连接超时")
        mock_downloader.return_value.download.side_effect = download_error

        # 应用patch
        with patch('kb.core.KnowledgeParser', return_value=mock_parser), \
             patch('kb.dependency.DependencyResolver', return_value=mock_resolver), \
             patch('kb.dependency.PackageDownloader', return_value=mock_downloader), \
             patch('kb.dependency.PackageExtractor', return_value=mock_extractor), \
             patch('kb.dependency.ConflictDetector', return_value=mock_conflict_detector):

            # 运行命令 - 直接调用 init 命令，使用 --path 参数
            result = runner.invoke(init, ["--path", str(sample_knowledge_md)])

            # 验证结果
            assert result.exit_code == 1, f"Expected exit code 1, got {result.exit_code}. Output: {result.output}"

            # 验证具体的错误消息
            assert "✗ 处理依赖失败" in result.output
            assert "网络连接失败" in result.output
            assert "test-package" in result.output

            # 验证组件调用
            mock_parser.assert_called_once_with()
            mock_parser.return_value.parse.assert_called_once_with(sample_knowledge_md)
            mock_resolver.assert_called_once_with()
            mock_resolver.return_value.resolve.assert_called_once_with(mock_metadata.dependencies)
            mock_conflict_detector.assert_called_once_with()
            mock_conflict_detector.return_value.check_conflicts.assert_called_once_with(resolved_deps)
            mock_downloader.return_value.download.assert_called_once_with(resolved_deps[0])
            # extractor不应该被调用，因为下载失败
            mock_extractor.return_value.extract.assert_not_called()
"""测试依赖版本更新器。"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from kb.update.updater import DependencyUpdater
from kb.exceptions import KnowledgeBaseError


@pytest.fixture
def updater():
    """创建更新器实例。"""
    return DependencyUpdater()


@pytest.fixture
def knowledge_file(tmp_path):
    """创建测试用的知识库文件。"""
    file_path = tmp_path / "Knowledge.md"
    content = """# TestLibrary

## 基本信息

- **名称**: TestLibrary
- **版本**: 1.0.0
- **类型**: structure-knowledge
- **职责描述**: 测试库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
| UtilsLib | 2.1.0 | https://github.com/example/utils-lib |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
"""
    with open(file_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(content)
    return file_path


@pytest.fixture
def knowledge_with_deps():
    """提供包含依赖的知识库文件。"""
    return Path(__file__).parent / "fixtures" / "knowledge_with_dependencies.md"


class TestDependencyUpdaterInit:
    """测试 DependencyUpdater 初始化。"""

    def test_init(self, updater):
        """测试初始化。"""
        assert updater is not None
        assert hasattr(updater, 'parser')


class TestUpdateDependency:
    """测试 update_dependency 方法。"""

    def test_update_single_dependency(self, updater, knowledge_file):
        """测试更新单个依赖。"""
        # 更新依赖
        updater.update_dependency(
            knowledge_file,
            "CommonDataTypes",
            "2.0.0"
        )

        # 验证更新
        content = knowledge_file.read_text(encoding="utf-8")
        assert "| CommonDataTypes | 2.0.0 |" in content

        # 验证备份文件存在
        backup_file = knowledge_file.with_suffix(".md.backup")
        assert backup_file.exists()

    def test_update_dependency_with_new_url(self, updater, knowledge_file):
        """测试更新依赖并更新URL。"""
        # 更新依赖和URL
        updater.update_dependency(
            knowledge_file,
            "UtilsLib",
            "3.0.0",
            "https://github.com/new-owner/utils-lib"
        )

        # 验证更新
        content = knowledge_file.read_text(encoding="utf-8")
        assert "| UtilsLib | 3.0.0 | https://github.com/new-owner/utils-lib |" in content

    def test_update_all_dependencies(self, updater, knowledge_file):
        """测试更新所有依赖。"""
        # 更新多个依赖
        updates = {
            "CommonDataTypes": "2.0.0",
            "UtilsLib": "3.0.0"
        }
        updater.update_all_dependencies(knowledge_file, updates)

        # 验证更新
        content = knowledge_file.read_text(encoding="utf-8")
        assert "| CommonDataTypes | 2.0.0 |" in content
        assert "| UtilsLib | 3.0.0 |" in content

        # 验证备份文件存在
        backup_file = knowledge_file.with_suffix(".md.backup")
        assert backup_file.exists()

    def test_update_all_dependencies_with_invalid_version(self, updater, knowledge_file):
        """测试更新所有依赖时使用无效版本号。"""
        updates = {
            "CommonDataTypes": "invalid-version",
            "UtilsLib": "3.0.0"
        }
        with pytest.raises(KnowledgeBaseError, match="版本号格式无效"):
            updater.update_all_dependencies(knowledge_file, updates)

    def test_update_all_dependencies_nonexistent(self, updater, knowledge_file):
        """测试更新所有依赖时包含不存在的依赖。"""
        updates = {
            "CommonDataTypes": "2.0.0",
            "NonExistentLib": "3.0.0"
        }
        with pytest.raises(KnowledgeBaseError, match="不存在"):
            updater.update_all_dependencies(knowledge_file, updates)

    def test_update_nonexistent_dependency(self, updater, knowledge_file):
        """测试更新不存在的依赖。"""
        with pytest.raises(KnowledgeBaseError, match="不存在"):
            updater.update_dependency(
                knowledge_file,
                "NonExistentLib",
                "2.0.0"
            )

    def test_update_file_not_found(self, updater):
        """测试更新不存在的文件。"""
        with pytest.raises(FileNotFoundError):
            updater.update_dependency(
                Path("nonexistent.md"),
                "TestLib",
                "2.0.0"
            )

    def test_update_invalid_version_format(self, updater, knowledge_file):
        """测试无效的版本号格式。"""
        with pytest.raises(KnowledgeBaseError, match="版本号格式无效"):
            updater.update_dependency(
                knowledge_file,
                "CommonDataTypes",
                "invalid-version"
            )


class TestBackupKnowledgeFile:
    """测试备份功能。"""

    def test_create_backup(self, updater, knowledge_file):
        """测试创建备份文件。"""
        # 直接调用创建备份方法
        backup_file = updater._create_backup(knowledge_file)

        # 验证备份文件路径
        assert backup_file == knowledge_file.with_suffix(".md.backup")

        # 验证备份文件存在
        assert backup_file.exists()

        # 验证备份内容与原文件一致
        backup_content = backup_file.read_text(encoding="utf-8")
        original_content = knowledge_file.read_text(encoding="utf-8")
        assert backup_content == original_content

    def test_backup_knowledge_file(self, updater, knowledge_file):
        """测试备份知识库文件。"""
        # 更新依赖会自动创建备份
        updater.update_dependency(
            knowledge_file,
            "CommonDataTypes",
            "2.0.0"
        )

        # 验证备份文件存在
        backup_file = knowledge_file.with_suffix(".md.backup")
        assert backup_file.exists()

        # 验证备份内容与原文件一致
        backup_content = backup_file.read_text(encoding="utf-8")
        assert "| CommonDataTypes | 1.0.0 |" in backup_content
        assert "| CommonDataTypes | 2.0.0 |" not in backup_content

    def test_backup_missing(self, updater, knowledge_file):
        """测试更新后备份文件不存在的情况。"""
        # 手动删除备份文件
        backup_file = knowledge_file.with_suffix(".md.backup")
        if backup_file.exists():
            backup_file.unlink()

        # 更新依赖
        updater.update_dependency(
            knowledge_file,
            "CommonDataTypes",
            "2.0.0"
        )

        # 验证备份文件被创建
        assert backup_file.exists()

    def test_backup_replaces_existing_backup(self, updater, knowledge_file):
        """测试重复更新时替换现有备份。"""
        # 第一次更新
        updater.update_dependency(
            knowledge_file,
            "CommonDataTypes",
            "2.0.0"
        )

        backup_file = knowledge_file.with_suffix(".md.backup")
        first_backup_mtime = backup_file.stat().st_mtime

        # 稍等一下（确保mtime不同）
        import time
        time.sleep(0.1)

        # 第二次更新
        updater.update_dependency(
            knowledge_file,
            "CommonDataTypes",
            "3.0.0"
        )

        # 验证备份文件被替换（mtime更新）
        assert backup_file.stat().st_mtime > first_backup_mtime

        # 验证备份内容是第二次更新前的状态
        backup_content = backup_file.read_text(encoding="utf-8")
        assert "| CommonDataTypes | 2.0.0 |" in backup_content


class TestUpdateWithoutGitRepo:
    """测试在没有Git仓库的情况下更新。"""

    def test_update_without_git_repo(self, updater, tmp_path):
        """测试在非Git仓库目录中更新。"""
        # 创建不在Git仓库中的文件
        knowledge_file = tmp_path / "Knowledge.md"
        content = """# TestLibrary

## 基本信息

- **名称**: TestLibrary
- **版本**: 1.0.0
- **类型**: structure-knowledge
- **职责描述**: 测试库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
"""
        with open(knowledge_file, "w", encoding="utf-8", newline='\n') as f:
            f.write(content)

        # 普通更新应该成功（不依赖Git）
        updater.update_dependency(
            knowledge_file,
            "CommonDataTypes",
            "2.0.0"
        )

        # 验证更新成功
        content = knowledge_file.read_text(encoding="utf-8")
        assert "| CommonDataTypes | 2.0.0 |" in content


class TestUpdateWithConflict:
    """测试更新时的冲突处理。"""

    def test_update_with_conflict(self, updater, knowledge_file):
        """测试更新可能导致格式冲突的情况。"""
        # 先更新一个依赖
        updater.update_dependency(
            knowledge_file,
            "CommonDataTypes",
            "2.0.0"
        )

        # 验证其他依赖未被影响
        content = knowledge_file.read_text(encoding="utf-8")
        assert "| UtilsLib | 2.1.0 |" in content

        # 更新另一个依赖
        updater.update_dependency(
            knowledge_file,
            "UtilsLib",
            "3.0.0"
        )

        # 验证两个依赖都被正确更新
        content = knowledge_file.read_text(encoding="utf-8")
        assert "| CommonDataTypes | 2.0.0 |" in content
        assert "| UtilsLib | 3.0.0 |" in content


class TestValidateVersionFormat:
    """测试版本号格式验证。"""

    def test_validate_valid_versions(self, updater):
        """测试有效的版本号格式。"""
        # 这些不应该抛出异常
        updater._validate_version_format("1.0.0")
        updater._validate_version_format("10.20.30")
        updater._validate_version_format("0.0.1")

    def test_validate_invalid_versions(self, updater):
        """测试无效的版本号格式。"""
        with pytest.raises(KnowledgeBaseError):
            updater._validate_version_format("1.0")
        with pytest.raises(KnowledgeBaseError):
            updater._validate_version_format("v1.0.0")
        with pytest.raises(KnowledgeBaseError):
            updater._validate_version_format("1.0.0-alpha")
        with pytest.raises(KnowledgeBaseError):
            updater._validate_version_format("invalid")


class TestDependencyExists:
    """测试依赖存在性检查。"""

    def test_dependency_exists(self, updater):
        """测试检查存在的依赖。"""
        content = """## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
"""
        assert updater._dependency_exists(content, "CommonDataTypes") is True

    def test_dependency_not_exists(self, updater):
        """测试检查不存在的依赖。"""
        content = """## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
"""
        assert updater._dependency_exists(content, "NonExistentLib") is False


class TestValidateUpdatedContent:
    """测试更新后内容的验证。"""

    def test_validate_valid_content(self, updater, knowledge_file):
        """测试验证有效的内容。"""
        content = knowledge_file.read_text(encoding="utf-8")
        # 不应该抛出异常
        updater._validate_updated_content(content, knowledge_file)

    def test_validate_invalid_content(self, updater, knowledge_file):
        """测试验证无效的内容。"""
        invalid_content = "This is not valid markdown"

        with pytest.raises(KnowledgeBaseError, match="格式无效"):
            updater._validate_updated_content(invalid_content, knowledge_file)


class TestUpdateFromGitRepo:
    """测试从Git仓库更新。"""

    def test_update_from_git_repo_no_gitpython(self, updater, tmp_path):
        """测试没有GitPython时的情况。"""
        knowledge_file = tmp_path / "Knowledge.md"
        content = """# TestLibrary

## 基本信息

- **名称**: TestLibrary
- **版本**: 1.0.0
- **类型**: structure-knowledge
- **职责描述**: 测试库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
"""
        with open(knowledge_file, "w", encoding="utf-8", newline='\n') as f:
            f.write(content)

        # 模拟没有GitPython
        with patch.dict('sys.modules', {'git': None}):
            with pytest.raises(ImportError, match="GitPython"):
                updater.update_from_git_repo(
                    knowledge_file,
                    "CommonDataTypes",
                    "https://github.com/example/common-data-types"
                )

    def test_update_from_git_repo_not_in_repo(self, updater, tmp_path):
        """测试不在Git仓库中时的情况。"""
        knowledge_file = tmp_path / "Knowledge.md"
        content = """# TestLibrary

## 基本信息

- **名称**: TestLibrary
- **版本**: 1.0.0
- **类型**: structure-knowledge
- **职责描述**: 测试库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
"""
        with open(knowledge_file, "w", encoding="utf-8", newline='\n') as f:
            f.write(content)

        # 模拟Git模块存在但不在Git仓库中
        # 使用sys.modules来模拟git模块
        import sys
        mock_git = MagicMock()
        mock_git.InvalidGitRepositoryError = Exception
        mock_git.Repo = MagicMock(side_effect=Exception("Not a git repo"))

        with patch.dict('sys.modules', {'git': mock_git}):
            # 模拟_get_git_repo返回None
            with patch.object(updater, '_get_git_repo', return_value=None):
                with pytest.raises(KnowledgeBaseError, match="不是Git仓库"):
                    updater.update_from_git_repo(
                        knowledge_file,
                        "CommonDataTypes",
                        "https://github.com/example/common-data-types"
                    )

    def test_update_from_git_repo_fetch_failure(self, updater, tmp_path):
        """测试获取最新版本失败的情况。"""
        knowledge_file = tmp_path / "Knowledge.md"
        content = """# TestLibrary

## 基本信息

- **名称**: TestLibrary
- **版本**: 1.0.0
- **类型**: structure-knowledge
- **职责描述**: 测试库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
"""
        with open(knowledge_file, "w", encoding="utf-8", newline='\n') as f:
            f.write(content)

        # 模拟Git仓库存在但获取版本失败
        mock_repo = Mock()
        mock_git = MagicMock()

        with patch.dict('sys.modules', {'git': mock_git}):
            with patch.object(updater, '_get_git_repo', return_value=mock_repo):
                with patch.object(updater, '_fetch_latest_tag', return_value=None):
                    with pytest.raises(KnowledgeBaseError, match="无法从.*获取最新版本"):
                        updater.update_from_git_repo(
                            knowledge_file,
                            "CommonDataTypes",
                            "https://github.com/example/common-data-types"
                        )


class TestExtractGithubOwnerRepo:
    """测试GitHub URL提取。"""

    def test_extract_github_owner_repo(self, updater):
        """测试提取GitHub owner和repo。"""
        owner, repo = updater._extract_github_owner_repo(
            "https://github.com/example/repo"
        )
        assert owner == "example"
        assert repo == "repo"

    def test_extract_github_owner_repo_with_trailing_slash(self, updater):
        """测试处理尾部斜杠。"""
        owner, repo = updater._extract_github_owner_repo(
            "https://github.com/example/repo/"
        )
        assert owner == "example"
        assert repo == "repo"


class TestExtractGitlabOwnerRepo:
    """测试GitLab URL提取。"""

    def test_extract_gitlab_owner_repo(self, updater):
        """测试提取GitLab owner和repo。"""
        owner, repo = updater._extract_gitlab_owner_repo(
            "https://gitlab.com/example/repo"
        )
        assert owner == "example"
        assert repo == "repo"

    def test_extract_gitlab_owner_repo_with_trailing_slash(self, updater):
        """测试处理尾部斜杠。"""
        owner, repo = updater._extract_gitlab_owner_repo(
            "https://gitlab.com/example/repo/"
        )
        assert owner == "example"
        assert repo == "repo"

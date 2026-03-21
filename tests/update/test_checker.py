# tests/update/test_checker.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import Timeout, HTTPError

from kb.update.checker import VersionChecker
from kb.update.models import VersionUpdate, VersionUpdateList
from kb.core.models import Dependency
from kb.exceptions import KnowledgeBaseError


@pytest.fixture
def checker():
    """创建版本检查器实例。"""
    return VersionChecker()


@pytest.fixture
def sample_dependencies():
    """创建示例依赖列表。"""
    return [
        Dependency(
            name="CommonDataTypes",
            version="1.0.0",
            git_url="https://github.com/example/common-data-types"
        ),
        Dependency(
            name="UtilsLib",
            version="2.1.0",
            git_url="https://github.com/example/utils-lib"
        ),
    ]


@pytest.fixture
def knowledge_with_deps():
    """提供包含依赖的知识库文件。"""
    return Path(__file__).parent / "fixtures" / "knowledge_with_dependencies.md"


class TestVersionCheckerInit:
    """测试 VersionChecker 初始化。"""

    def test_init(self, checker):
        """测试初始化。"""
        assert checker is not None
        assert hasattr(checker, 'parser')
        assert hasattr(checker, 'API_TIMEOUT')


class TestExtractOwnerRepo:
    """测试 _extract_owner_repo 私有方法。"""

    def test_extract_github_owner_repo(self, checker):
        """测试提取 GitHub owner 和 repo。"""
        owner, repo = checker._extract_owner_repo(
            "https://github.com/example/repo"
        )
        assert owner == "example"
        assert repo == "repo"

    def test_extract_gitlab_owner_repo(self, checker):
        """测试提取 GitLab owner 和 repo。"""
        owner, repo = checker._extract_owner_repo(
            "https://gitlab.com/example/repo"
        )
        assert owner == "example"
        assert repo == "repo"

    def test_extract_owner_repo_trailing_slash(self, checker):
        """测试处理尾部斜杠。"""
        owner, repo = checker._extract_owner_repo(
            "https://github.com/example/repo/"
        )
        assert owner == "example"
        assert repo == "repo"

    def test_extract_owner_repo_invalid_url(self, checker):
        """测试无效 URL。"""
        with pytest.raises(KnowledgeBaseError):
            checker._extract_owner_repo("invalid-url")

    def test_extract_owner_repo_missing_repo(self, checker):
        """测试缺少 repo 部分的 URL。"""
        with pytest.raises(KnowledgeBaseError):
            checker._extract_owner_repo("https://github.com/example")


class TestParseVersion:
    """测试 _parse_version 私有方法。"""

    def test_parse_standard_version(self, checker):
        """测试解析标准版本号。"""
        parts = checker._parse_version("1.2.3")
        assert parts == [1, 2, 3]

    def test_parse_version_with_v_prefix(self, checker):
        """测试解析带 v 前缀的版本号。"""
        parts = checker._parse_version("v1.2.3")
        assert parts == [1, 2, 3]

    def test_parse_version_with_prerelease(self, checker):
        """测试解析带预发布标签的版本号。"""
        parts = checker._parse_version("1.2.3-alpha.1")
        assert parts == [1, 2, 3]

    def test_parse_version_longer(self, checker):
        """测试解析更长的版本号。"""
        parts = checker._parse_version("1.2.3.4.5")
        assert parts == [1, 2, 3, 4, 5]

    def test_parse_version_invalid_format(self, checker):
        """测试无效的版本号格式。"""
        with pytest.raises(ValueError):
            checker._parse_version("1.2")

    def test_parse_version_non_numeric(self, checker):
        """测试非数字版本号。"""
        with pytest.raises(ValueError):
            checker._parse_version("1.a.3")


class TestCompareVersions:
    """测试 _compare_versions 私有方法。"""

    def test_compare_newer_major(self, checker):
        """测试主版本更新。"""
        assert checker._compare_versions("1.2.3", "2.0.0") is True

    def test_compare_newer_minor(self, checker):
        """测试次版本更新。"""
        assert checker._compare_versions("1.2.3", "1.3.0") is True

    def test_compare_newer_patch(self, checker):
        """测试修订版本更新。"""
        assert checker._compare_versions("1.2.3", "1.2.4") is True

    def test_compare_same_version(self, checker):
        """测试相同版本。"""
        assert checker._compare_versions("1.2.3", "1.2.3") is False

    def test_compare_older_version(self, checker):
        """测试旧版本。"""
        assert checker._compare_versions("2.0.0", "1.2.3") is False

    def test_compare_prerelease_versions(self, checker):
        """测试带预发布标签的版本。"""
        assert checker._compare_versions("1.2.3", "v1.2.4-alpha.1") is True


class TestFetchLatestVersion:
    """测试 _fetch_latest_version 私有方法。"""

    @patch('kb.update.checker.requests.get')
    def test_fetch_github_latest_version_success(self, mock_get, checker):
        """测试成功获取 GitHub 最新版本。"""
        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "v2.0.0"}
        mock_get.return_value = mock_response

        version = checker._fetch_latest_version(
            "https://github.com/example/repo"
        )
        assert version == "2.0.0"

    @patch('kb.update.checker.requests.get')
    def test_fetch_github_latest_version_without_v_prefix(self, mock_get, checker):
        """测试获取不带 v 前缀的 GitHub 版本。"""
        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "2.0.0"}
        mock_get.return_value = mock_response

        version = checker._fetch_latest_version(
            "https://github.com/example/repo"
        )
        assert version == "2.0.0"

    @patch('kb.update.checker.requests.get')
    def test_fetch_github_latest_version_not_found(self, mock_get, checker):
        """测试 GitHub 仓库未找到。"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(KnowledgeBaseError):
            checker._fetch_latest_version(
                "https://github.com/example/nonexistent-repo"
            )

    @patch('kb.update.checker.requests.get')
    def test_fetch_github_latest_version_timeout(self, mock_get, checker):
        """测试 GitHub API 超时。"""
        mock_get.side_effect = Timeout()

        with pytest.raises(KnowledgeBaseError):
            checker._fetch_latest_version(
                "https://github.com/example/repo"
            )

    @patch('kb.update.checker.requests.get')
    def test_fetch_gitlab_latest_version_success(self, mock_get, checker):
        """测试成功获取 GitLab 最新版本。"""
        mock_response = Mock()
        mock_response.json.return_value = [{"tag_name": "v2.0.0"}]
        mock_get.return_value = mock_response

        version = checker._fetch_latest_version(
            "https://gitlab.com/example/repo"
        )
        assert version == "2.0.0"

    @patch('kb.update.checker.requests.get')
    def test_fetch_gitlab_latest_version_no_releases(self, mock_get, checker):
        """测试 GitLab 仓库没有 releases。"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        with pytest.raises(KnowledgeBaseError):
            checker._fetch_latest_version(
                "https://gitlab.com/example/repo"
            )

    def test_fetch_latest_version_unsupported_platform(self, checker):
        """测试不支持的 Git 平台。"""
        with pytest.raises(KnowledgeBaseError):
            checker._fetch_latest_version("https://bitbucket.org/example/repo")


class TestCheckSingleDependency:
    """测试 _check_single_dependency 私有方法。"""

    @patch('kb.update.checker.requests.get')
    def test_check_single_dependency_with_update(self, mock_get, checker):
        """测试检查单个依赖（有更新）。"""
        dependency = Dependency(
            name="TestLib",
            version="1.0.0",
            git_url="https://github.com/example/test-lib"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "v2.0.0"}
        mock_get.return_value = mock_response

        update = checker._check_single_dependency(dependency)

        assert isinstance(update, VersionUpdate)
        assert update.name == "TestLib"
        assert update.current_version == "1.0.0"
        assert update.latest_version == "2.0.0"
        assert update.update_available is True

    @patch('kb.update.checker.requests.get')
    def test_check_single_dependency_no_update(self, mock_get, checker):
        """测试检查单个依赖（无更新）。"""
        dependency = Dependency(
            name="TestLib",
            version="2.0.0",
            git_url="https://github.com/example/test-lib"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "v2.0.0"}
        mock_get.return_value = mock_response

        update = checker._check_single_dependency(dependency)

        assert update.update_available is False


class TestCheckUpdates:
    """测试 check_updates 方法。"""

    @patch('kb.update.checker.requests.get')
    def test_check_updates_multiple(self, mock_get, checker, sample_dependencies):
        """测试检查多个依赖。"""
        # 模拟第一个依赖有更新
        mock_response_1 = Mock()
        mock_response_1.json.return_value = {"tag_name": "v2.0.0"}

        # 模拟第二个依赖无更新
        mock_response_2 = Mock()
        mock_response_2.json.return_value = {"tag_name": "v2.1.0"}

        mock_get.side_effect = [mock_response_1, mock_response_2]

        update_list = checker.check_updates(sample_dependencies)

        assert isinstance(update_list, VersionUpdateList)
        assert len(update_list) == 1
        assert update_list.has_updates() is True

    @patch('kb.update.checker.requests.get')
    def test_check_updates_no_updates(self, mock_get, checker, sample_dependencies):
        """测试检查多个依赖（无更新）。"""
        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "1.0.0"}
        mock_get.return_value = mock_response

        update_list = checker.check_updates(sample_dependencies)

        assert len(update_list) == 0
        assert update_list.has_updates() is False

    @patch('kb.update.checker.requests.get')
    def test_check_updates_empty_list(self, mock_get, checker):
        """测试检查空依赖列表。"""
        update_list = checker.check_updates([])

        assert len(update_list) == 0
        assert update_list.has_updates() is False

    @patch('kb.update.checker.requests.get')
    def test_check_updates_with_error(self, mock_get, checker, sample_dependencies):
        """测试检查依赖时出现错误。"""
        # 第一个依赖成功
        mock_response_1 = Mock()
        mock_response_1.json.return_value = {"tag_name": "v2.0.0"}

        # 第二个依赖失败
        mock_response_2 = Mock()
        mock_response_2.status_code = 404
        mock_response_2.raise_for_status.side_effect = HTTPError()

        mock_get.side_effect = [mock_response_1, mock_response_2]

        # 应该继续处理，只返回成功的更新
        update_list = checker.check_updates(sample_dependencies)

        assert len(update_list) == 1


class TestCheckSingleDependencyFromFile:
    """测试 check_single_dependency 方法（从文件读取）。"""

    def test_check_single_dependency_from_file(self, checker, knowledge_with_deps):
        """测试从文件中检查单个依赖。"""
        with patch('kb.update.checker.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"tag_name": "v2.0.0"}
            mock_get.return_value = mock_response

            update_list = checker.check_single_dependency(
                knowledge_with_deps, "CommonDataTypes"
            )

            assert isinstance(update_list, VersionUpdateList)
            assert len(update_list) == 1
            assert update_list.updates[0].name == "CommonDataTypes"

    def test_check_single_dependency_not_found(self, checker, knowledge_with_deps):
        """测试查找不存在的依赖。"""
        with pytest.raises(KnowledgeBaseError):
            checker.check_single_dependency(
                knowledge_with_deps, "NonExistentLib"
            )

    def test_check_single_dependency_file_not_found(self, checker):
        """测试文件不存在的情况。"""
        with pytest.raises(FileNotFoundError):
            checker.check_single_dependency(
                Path("nonexistent.md"), "TestLib"
            )


class TestVersionUpdateList:
    """测试 VersionUpdateList 模型。"""

    def test_add_update(self):
        """测试添加更新。"""
        update_list = VersionUpdateList()
        update = VersionUpdate(
            name="TestLib",
            current_version="1.0.0",
            latest_version="2.0.0",
            git_url="https://github.com/example/test-lib"
        )

        update_list.add_update(update)

        assert len(update_list) == 1
        assert update_list.has_updates() is True

    def test_has_updates_empty(self):
        """测试空列表是否有更新。"""
        update_list = VersionUpdateList()
        assert update_list.has_updates() is False

    def test_iteration(self):
        """测试迭代。"""
        update_list = VersionUpdateList()
        update_1 = VersionUpdate(
            name="TestLib1",
            current_version="1.0.0",
            latest_version="2.0.0",
            git_url="https://github.com/example/test-lib-1"
        )
        update_2 = VersionUpdate(
            name="TestLib2",
            current_version="1.0.0",
            latest_version="2.0.0",
            git_url="https://github.com/example/test-lib-2"
        )

        update_list.add_update(update_1)
        update_list.add_update(update_2)

        updates = list(update_list)
        assert len(updates) == 2
        assert updates[0].name == "TestLib1"
        assert updates[1].name == "TestLib2"


class TestVersionUpdate:
    """测试 VersionUpdate 模型。"""

    def test_version_update_creation(self):
        """测试创建版本更新对象。"""
        update = VersionUpdate(
            name="TestLib",
            current_version="1.0.0",
            latest_version="2.0.0",
            git_url="https://github.com/example/test-lib",
            update_available=True
        )

        assert update.name == "TestLib"
        assert update.current_version == "1.0.0"
        assert update.latest_version == "2.0.0"
        assert update.git_url == "https://github.com/example/test-lib"
        assert update.update_available is True

    def test_version_update_default_update_available(self):
        """测试默认 update_available 值。"""
        update = VersionUpdate(
            name="TestLib",
            current_version="1.0.0",
            latest_version="2.0.0",
            git_url="https://github.com/example/test-lib"
        )

        assert update.update_available is True

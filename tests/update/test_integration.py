# tests/update/test_integration.py
"""版本检查器集成测试。"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from kb.update.checker import VersionChecker
from kb.update.models import VersionUpdateList
from kb.core.models import Dependency


@pytest.fixture
def checker():
    """创建版本检查器实例。"""
    return VersionChecker()


@pytest.fixture
def knowledge_file(tmp_path):
    """创建临时的知识库文件。"""
    knowledge_content = """# TestLib

## 基本信息

- **名称**: TestLib
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试知识库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonLib | 1.0.0 | https://github.com/example/common-lib |
"""
    knowledge_file = tmp_path / "Knowledge.md"
    knowledge_file.write_text(knowledge_content)
    return knowledge_file


class TestVersionCheckerIntegration:
    """版本检查器集成测试。"""

    @patch('kb.update.checker.requests.get')
    def test_check_updates_integration(self, mock_get, checker, knowledge_file):
        """测试完整的版本检查流程。"""
        # 模拟 GitHub API 响应
        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "v2.0.0"}
        mock_get.return_value = mock_response

        # 1. 解析知识库文件
        metadata = checker.parser.parse(knowledge_file)
        assert len(metadata.dependencies) == 1

        # 2. 检查依赖更新
        update_list = checker.check_updates(metadata.dependencies)

        # 3. 验证结果
        assert isinstance(update_list, VersionUpdateList)
        assert len(update_list) == 1
        assert update_list.has_updates() is True

        update = update_list.updates[0]
        assert update.name == "CommonLib"
        assert update.current_version == "1.0.0"
        assert update.latest_version == "2.0.0"
        assert update.update_available is True

    @patch('kb.update.checker.requests.get')
    def test_check_single_dependency_integration(self, mock_get, checker, knowledge_file):
        """测试检查单个依赖的完整流程。"""
        # 模拟 GitHub API 响应
        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "v1.5.0"}
        mock_get.return_value = mock_response

        # 从文件检查单个依赖
        update_list = checker.check_single_dependency(knowledge_file, "CommonLib")

        # 验证结果
        assert isinstance(update_list, VersionUpdateList)
        assert len(update_list) == 1

        update = update_list.updates[0]
        assert update.name == "CommonLib"
        assert update.current_version == "1.0.0"
        assert update.latest_version == "1.5.0"
        assert update.update_available is True

    @patch('kb.update.checker.requests.get')
    def test_no_updates_available(self, mock_get, checker, knowledge_file):
        """测试没有可用更新的情况。"""
        # 模拟 GitHub API 响应（版本相同）
        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "v1.0.0"}
        mock_get.return_value = mock_response

        # 检查依赖更新
        metadata = checker.parser.parse(knowledge_file)
        update_list = checker.check_updates(metadata.dependencies)

        # 验证结果
        assert len(update_list) == 0
        assert update_list.has_updates() is False

    @patch('kb.update.checker.requests.get')
    def test_github_vs_gitlab(self, mock_get, checker):
        """测试 GitHub 和 GitLab 的版本检查。"""
        dependencies = [
            Dependency(
                name="GitHubLib",
                version="1.0.0",
                git_url="https://github.com/example/github-lib"
            ),
            Dependency(
                name="GitLabLib",
                version="1.0.0",
                git_url="https://gitlab.com/example/gitlab-lib"
            ),
        ]

        # 模拟 GitHub API 响应
        mock_github_response = Mock()
        mock_github_response.json.return_value = {"tag_name": "v2.0.0"}

        # 模拟 GitLab API 响应
        mock_gitlab_response = Mock()
        mock_gitlab_response.json.return_value = [{"tag_name": "v3.0.0"}]

        mock_get.side_effect = [mock_github_response, mock_gitlab_response]

        # 检查更新
        update_list = checker.check_updates(dependencies)

        # 验证结果
        assert len(update_list) == 2

        # 验证 GitHub 依赖
        github_update = next(u for u in update_list if u.name == "GitHubLib")
        assert github_update.latest_version == "2.0.0"

        # 验证 GitLab 依赖
        gitlab_update = next(u for u in update_list if u.name == "GitLabLib")
        assert gitlab_update.latest_version == "3.0.0"

    @patch('kb.update.checker.requests.get')
    def test_version_comparison_scenarios(self, mock_get, checker):
        """测试各种版本比较场景。"""
        test_cases = [
            ("1.0.0", "1.0.1", True),  # 修订版本更新
            ("1.0.0", "1.1.0", True),  # 次版本更新
            ("1.0.0", "2.0.0", True),  # 主版本更新
            ("2.0.0", "1.0.0", False),  # 降级
            ("1.0.0", "1.0.0", False),  # 相同版本
        ]

        for i, (current, latest, has_update) in enumerate(test_cases):
            dependency = Dependency(
                name=f"TestLib{i}",
                version=current,
                git_url="https://github.com/example/test-lib"
            )

            # 模拟 API 响应
            mock_response = Mock()
            mock_response.json.return_value = {"tag_name": f"v{latest}"}
            mock_get.reset_mock()
            mock_get.return_value = mock_response

            # 检查更新
            update = checker._check_single_dependency(dependency)

            # 验证
            assert update.update_available == has_update
            assert update.current_version == current
            assert update.latest_version == latest

"""版本检查器 - 检查依赖项的最新版本。"""

from __future__ import annotations
import re
from pathlib import Path
from typing import List, Optional, Tuple

import requests

from kb.core.models import Dependency
from kb.core.parser import KnowledgeParser
from kb.update.models import VersionUpdate, VersionUpdateList
from kb.exceptions import KnowledgeBaseError


class VersionChecker:
    """版本检查器，用于检查知识库依赖的最新版本。"""

    # API 超时设置（秒）
    API_TIMEOUT = 30

    # GitHub API 基础 URL
    GITHUB_API_BASE = "https://api.github.com"

    # GitLab API 基础 URL
    GITLAB_API_BASE = "https://gitlab.com/api/v4"

    def __init__(self):
        """初始化版本检查器。"""
        self.parser = KnowledgeParser()

    def check_updates(self, dependencies: List[Dependency]) -> VersionUpdateList:
        """检查多个依赖的更新情况。

        Args:
            dependencies: 依赖列表

        Returns:
            VersionUpdateList: 版本更新列表
        """
        update_list = VersionUpdateList()

        for dependency in dependencies:
            try:
                update_info = self._check_single_dependency(dependency)
                if update_info.update_available:
                    update_list.add_update(update_info)
            except KnowledgeBaseError as e:
                # 记录错误但继续检查其他依赖
                print(f"检查依赖 {dependency.name} 失败: {e}")
                continue

        return update_list

    def check_single_dependency(
        self, knowledge_file: Path, dependency_name: str
    ) -> VersionUpdateList:
        """检查知识库文件中单个依赖的更新情况。

        Args:
            knowledge_file: Knowledge.md 文件路径
            dependency_name: 要检查的依赖名称

        Returns:
            VersionUpdateList: 版本更新列表（只包含一个更新）

        Raises:
            FileNotFoundError: 知识库文件不存在
            KnowledgeBaseError: 依赖不存在或检查失败
        """
        # 解析知识库文件
        metadata = self.parser.parse(knowledge_file)

        # 查找指定的依赖
        target_dependency = None
        for dep in metadata.dependencies:
            if dep.name == dependency_name:
                target_dependency = dep
                break

        if target_dependency is None:
            raise KnowledgeBaseError(
                f"在知识库中未找到依赖: {dependency_name}"
            )

        # 检查更新
        update_info = self._check_single_dependency(target_dependency)
        update_list = VersionUpdateList()
        update_list.add_update(update_info)

        return update_list

    def _check_single_dependency(self, dependency: Dependency) -> VersionUpdate:
        """检索单个依赖的更新信息（私有方法）。

        Args:
            dependency: 依赖项

        Returns:
            VersionUpdate: 版本更新信息

        Raises:
            KnowledgeBaseError: 检查失败
        """
        # 获取最新版本
        latest_version = self._fetch_latest_version(dependency.git_url)

        # 比较版本
        update_available = self._compare_versions(
            dependency.version, latest_version
        )

        return VersionUpdate(
            name=dependency.name,
            current_version=dependency.version,
            latest_version=latest_version,
            git_url=dependency.git_url,
            update_available=update_available,
        )

    def _fetch_latest_version(self, git_url: str) -> str:
        """从 Git API 获取最新版本号（私有方法）。

        Args:
            git_url: Git 仓库 URL

        Returns:
            str: 最新版本号

        Raises:
            KnowledgeBaseError: 获取失败
        """
        if "github.com" in git_url:
            return self._fetch_github_latest_version(git_url)
        elif "gitlab.com" in git_url:
            return self._fetch_gitlab_latest_version(git_url)
        else:
            raise KnowledgeBaseError(f"不支持的 Git 平台: {git_url}")

    def _fetch_github_latest_version(self, git_url: str) -> str:
        """从 GitHub API 获取最新版本（私有方法）。

        Args:
            git_url: GitHub 仓库 URL

        Returns:
            str: 最新版本号

        Raises:
            KnowledgeBaseError: 获取失败
        """
        owner, repo = self._extract_owner_repo(git_url)

        # 调用 GitHub API 获取最新 release
        api_url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/releases/latest"

        try:
            response = requests.get(api_url, timeout=self.API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            # 从 tag_name 中提取版本号（去除 'v' 前缀）
            tag_name = data.get("tag_name", "")
            if tag_name.startswith("v"):
                version = tag_name[1:]
            else:
                version = tag_name

            return version

        except requests.exceptions.Timeout as e:
            raise KnowledgeBaseError(f"GitHub API 请求超时: {e}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise KnowledgeBaseError(f"仓库未找到或没有 releases: {git_url}")
            raise KnowledgeBaseError(f"GitHub API HTTP 错误: {e}")
        except requests.exceptions.RequestException as e:
            raise KnowledgeBaseError(f"GitHub API 请求失败: {e}")
        except (KeyError, ValueError) as e:
            raise KnowledgeBaseError(f"解析 GitHub API 响应失败: {e}")

    def _fetch_gitlab_latest_version(self, git_url: str) -> str:
        """从 GitLab API 获取最新版本（私有方法）。

        Args:
            git_url: GitLab 仓库 URL

        Returns:
            str: 最新版本号

        Raises:
            KnowledgeBaseError: 获取失败
        """
        owner, repo = self._extract_owner_repo(git_url)

        # 调用 GitLab API 获取最新 release
        api_url = f"{self.GITLAB_API_BASE}/projects/{owner}%2F{repo}/releases"

        try:
            response = requests.get(api_url, timeout=self.API_TIMEOUT)
            response.raise_for_status()
            releases = response.json()

            if not releases:
                raise KnowledgeBaseError(f"仓库没有 releases: {git_url}")

            # 获取第一个（最新）release
            latest_release = releases[0]
            tag_name = latest_release.get("tag_name", "")

            # 从 tag_name 中提取版本号（去除 'v' 前缀）
            if tag_name.startswith("v"):
                version = tag_name[1:]
            else:
                version = tag_name

            return version

        except requests.exceptions.Timeout as e:
            raise KnowledgeBaseError(f"GitLab API 请求超时: {e}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise KnowledgeBaseError(f"仓库未找到或没有 releases: {git_url}")
            raise KnowledgeBaseError(f"GitLab API HTTP 错误: {e}")
        except requests.exceptions.RequestException as e:
            raise KnowledgeBaseError(f"GitLab API 请求失败: {e}")
        except (KeyError, ValueError, IndexError) as e:
            raise KnowledgeBaseError(f"解析 GitLab API 响应失败: {e}")

    def _extract_owner_repo(self, git_url: str) -> Tuple[str, str]:
        """从 Git URL 提取 owner 和 repo（私有方法）。

        Args:
            git_url: Git 仓库 URL

        Returns:
            (owner, repo) 元组

        Raises:
            KnowledgeBaseError: URL 格式错误
        """
        try:
            # 移除协议部分
            if "://" in git_url:
                git_url = git_url.split("://", 1)[1]

            # 移除域名
            if "/" in git_url:
                path = git_url.split("/", 1)[1]
                if path.endswith("/"):
                    path = path[:-1]
                parts = path.split("/", 1)
                if len(parts) != 2:
                    raise KnowledgeBaseError(f"无效的 Git URL 格式: {git_url}")
                return parts[0], parts[1]
            else:
                raise KnowledgeBaseError(f"无效的 Git URL 格式: {git_url}")
        except (ValueError, IndexError) as e:
            raise KnowledgeBaseError(f"解析 Git URL 失败: {e}")

    def _compare_versions(self, current: str, latest: str) -> bool:
        """比较两个版本号，判断是否有更新（私有方法）。

        Args:
            current: 当前版本
            latest: 最新版本

        Returns:
            bool: 如果最新版本更新，返回 True

        Raises:
            KnowledgeBaseError: 版本号格式错误
        """
        try:
            current_parts = self._parse_version(current)
            latest_parts = self._parse_version(latest)

            # 比较版本号
            for i in range(max(len(current_parts), len(latest_parts))):
                current_val = current_parts[i] if i < len(current_parts) else 0
                latest_val = latest_parts[i] if i < len(latest_parts) else 0

                if latest_val > current_val:
                    return True
                elif latest_val < current_val:
                    return False

            return False

        except (ValueError, IndexError) as e:
            raise KnowledgeBaseError(f"比较版本号失败: {e}")

    def _parse_version(self, version: str) -> List[int]:
        """解析版本号，返回整数列表（私有方法）。

        Args:
            version: 版本号字符串（如 "1.2.3"）

        Returns:
            List[int]: 版本号各部分的整数列表

        Raises:
            ValueError: 版本号格式错误
        """
        # 移除可能的 'v' 前缀
        if version.startswith("v"):
            version = version[1:]

        # 移除可能的预发布标签（如 -alpha.1）
        version = version.split("-")[0]

        parts = version.split(".")
        if len(parts) < 3:
            raise ValueError(f"版本号格式错误: {version}")

        try:
            return [int(part) for part in parts]
        except ValueError as e:
            raise ValueError(f"版本号部分不是数字: {version}")

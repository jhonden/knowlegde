"""依赖版本更新器。"""

import re
import shutil
from pathlib import Path
from typing import Optional

from kb.core.models import Dependency
from kb.core.parser import KnowledgeParser
from kb.exceptions import KnowledgeBaseError


class DependencyUpdater:
    """依赖版本更新器，负责更新知识库文件中的依赖版本。"""

    def __init__(self):
        """初始化更新器。"""
        self.parser = KnowledgeParser()

    def update_dependency(
        self,
        knowledge_file: Path,
        dependency_name: str,
        new_version: str,
        new_git_url: Optional[str] = None
    ) -> None:
        """更新知识库文件中的依赖版本。

        Args:
            knowledge_file: 知识库文件路径 (Knowledge.md)
            dependency_name: 要更新的依赖名称
            new_version: 新版本号
            new_git_url: 新的Git仓库地址（可选，如果不提供则保留原值）

        Raises:
            FileNotFoundError: 知识库文件不存在
            KnowledgeBaseError: 依赖不存在或更新失败
        """
        # 验证文件存在
        if not knowledge_file.exists():
            raise FileNotFoundError(f"知识库文件不存在: {knowledge_file}")

        # 验证版本号格式
        self._validate_version_format(new_version)

        # 读取文件内容
        with open(knowledge_file, "r", encoding="utf-8", newline='\n') as f:
            content = f.read()

        # 检查依赖是否存在
        if not self._dependency_exists(content, dependency_name):
            raise KnowledgeBaseError(f"依赖 '{dependency_name}' 不存在")

        # 创建备份
        self._create_backup(knowledge_file)

        # 更新依赖
        updated_content = self._update_dependency_in_content(
            content, dependency_name, new_version, new_git_url
        )

        # 验证更新后的内容
        self._validate_updated_content(updated_content, knowledge_file)

        # 写回文件
        with open(knowledge_file, "w", encoding="utf-8", newline='\n') as f:
            f.write(updated_content)

    def _validate_version_format(self, version: str) -> None:
        """验证版本号格式。

        Args:
            version: 版本号

        Raises:
            KnowledgeBaseError: 版本号格式无效
        """
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            raise KnowledgeBaseError(f"版本号格式无效: {version} (必须是 X.Y.Z 格式)")

    def _dependency_exists(self, content: str, dependency_name: str) -> bool:
        """检查依赖是否存在。

        Args:
            content: 文件内容
            dependency_name: 依赖名称

        Returns:
            依赖是否存在
        """
        # 匹配表格格式: | 依赖名称 |
        pattern = rf"\|\s*{re.escape(dependency_name)}\s*\|"
        return re.search(pattern, content) is not None

    def _create_backup(self, knowledge_file: Path) -> Path:
        """创建备份文件。

        Args:
            knowledge_file: 知识库文件路径

        Returns:
            备份文件路径
        """
        backup_file = knowledge_file.with_suffix(".md.backup")

        # 如果备份已存在，先删除
        if backup_file.exists():
            backup_file.unlink()

        # 创建备份
        shutil.copy2(knowledge_file, backup_file)
        return backup_file

    def _update_dependency_in_content(
        self,
        content: str,
        dependency_name: str,
        new_version: str,
        new_git_url: Optional[str]
    ) -> str:
        """在内容中更新依赖。

        Args:
            content: 文件内容
            dependency_name: 依赖名称
            new_version: 新版本号
            new_git_url: 新的Git仓库地址（可选）

        Returns:
            更新后的内容
        """
        # 构建匹配模式：| 依赖名称 | 旧版本号 | 旧URL |
        # 匹配整行，包括换行符
        pattern = rf"(^\|[^|]*{re.escape(dependency_name)}[^|]*\|[^|]*\|[^|]*\|.*$)"

        def replacer(match):
            """替换函数。"""
            # 分割表格行
            row = match.group(0)
            parts = [part.strip() for part in row.split("|")]

            # parts[0]: 空字符串（开头）
            # parts[1]: 依赖名称
            # parts[2]: 版本号
            # parts[3]: URL
            # parts[4]: 空字符串（结尾）

            if len(parts) >= 4:
                # 更新版本号
                parts[2] = new_version

                # 更新URL（如果提供了新的URL）
                if new_git_url:
                    parts[3] = new_git_url

                # 重建行，保持原有的格式
                # 重新分割以保留原始空格
                original_parts = row.split("|")
                updated_parts = original_parts.copy()

                # 更新版本号部分（保留原始空格）
                if len(updated_parts) >= 3:
                    old_version = updated_parts[2].strip()
                    updated_parts[2] = updated_parts[2].replace(old_version, new_version, 1)

                # 更新URL部分（保留原始空格或使用新值）
                if len(updated_parts) >= 4 and new_git_url:
                    updated_parts[3] = f" {new_git_url} "

                return "|".join(updated_parts)

            return row

        # 执行替换（多行模式）
        updated_content, count = re.subn(
            pattern, replacer, content, flags=re.MULTILINE
        )

        if count == 0:
            raise KnowledgeBaseError(f"无法找到依赖 '{dependency_name}' 的匹配项")

        return updated_content

        # 执行替换
        updated_content, count = re.subn(pattern, replacer, content)

        if count == 0:
            raise KnowledgeBaseError(f"无法找到依赖 '{dependency_name}' 的匹配项")

        return updated_content

    def _validate_updated_content(self, content: str, knowledge_file: Path) -> None:
        """验证更新后的内容是否有效。

        Args:
            content: 更新后的内容
            knowledge_file: 知识库文件路径（用于错误消息）

        Raises:
            KnowledgeBaseError: 内容无效
        """
        # 尝试解析更新后的内容
        try:
            # 使用临时路径来解析（避免文件路径问题）
            temp_file = knowledge_file.parent / f".{knowledge_file.name}.tmp"
            try:
                with open(temp_file, "w", encoding="utf-8", newline='\n') as f:
                    f.write(content)
                self.parser.parse(temp_file)
            finally:
                # 清理临时文件
                if temp_file.exists():
                    temp_file.unlink()
        except Exception as e:
            raise KnowledgeBaseError(f"更新后的内容格式无效: {e}")

    def update_from_git_repo(
        self,
        knowledge_file: Path,
        dependency_name: str,
        git_url: str
    ) -> None:
        """从Git仓库获取最新版本并更新依赖。

        Args:
            knowledge_file: 知识库文件路径
            dependency_name: 依赖名称
            git_url: Git仓库URL

        Raises:
            FileNotFoundError: 知识库文件不存在
            KnowledgeBaseError: 更新失败或依赖不存在
            ImportError: GitPython未安装
        """
        try:
            import git
        except ImportError:
            raise ImportError(
                "需要安装 GitPython 库。请运行: pip install gitpython"
            )

        # 验证文件存在
        if not knowledge_file.exists():
            raise FileNotFoundError(f"知识库文件不存在: {knowledge_file}")

        # 检查是否在Git仓库中
        repo = self._get_git_repo(knowledge_file)
        if not repo:
            raise KnowledgeBaseError("当前目录不是Git仓库")

        # 获取最新版本标签
        latest_version = self._fetch_latest_tag(git_url)
        if not latest_version:
            raise KnowledgeBaseError(f"无法从 {git_url} 获取最新版本")

        # 更新依赖
        self.update_dependency(
            knowledge_file, dependency_name, latest_version, git_url
        )

    def _get_git_repo(self, file_path: Path) -> Optional[object]:
        """获取文件所在的Git仓库。

        Args:
            file_path: 文件路径

        Returns:
            Git仓库对象，如果不在仓库中则返回None
        """
        try:
            import git
        except ImportError:
            return None

        try:
            # 获取文件所在的目录
            search_dir = file_path.parent if file_path.is_file() else file_path

            # 搜索Git仓库
            repo = git.Repo(search_dir, search_parent_directories=True)
            return repo
        except git.InvalidGitRepositoryError:
            return None

    def _fetch_latest_tag(self, git_url: str) -> Optional[str]:
        """从Git URL获取最新版本标签。

        Args:
            git_url: Git仓库URL

        Returns:
            最新版本号，如果无法获取则返回None
        """
        try:
            import git
        except ImportError:
            return None

        import tempfile
        import requests

        # 判断是否为GitHub或GitLab
        if "github.com" in git_url:
            # 使用GitHub API获取最新release
            owner, repo = self._extract_github_owner_repo(git_url)
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    tag_name = data.get("tag_name", "")
                    # 移除 'v' 前缀
                    return tag_name.lstrip("v")
            except Exception:
                pass

        elif "gitlab.com" in git_url:
            # 使用GitLab API获取最新release
            owner, repo = self._extract_gitlab_owner_repo(git_url)
            api_url = f"https://gitlab.com/api/v4/projects/{owner}%2F{repo}/releases"

            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        tag_name = data[0].get("tag_name", "")
                        # 移除 'v' 前缀
                        return tag_name.lstrip("v")
            except Exception:
                pass

        return None

    def _extract_github_owner_repo(self, git_url: str) -> tuple[str, str]:
        """从GitHub URL提取owner和repo。

        Args:
            git_url: Git URL

        Returns:
            (owner, repo) 元组
        """
        # 移除协议和域名
        parts = git_url.split("github.com/")[-1].rstrip("/")
        owner, repo = parts.split("/")
        return owner, repo

    def _extract_gitlab_owner_repo(self, git_url: str) -> tuple[str, str]:
        """从GitLab URL提取owner和repo。

        Args:
            git_url: Git URL

        Returns:
            (owner, repo) 元组
        """
        # 移除协议和域名
        parts = git_url.split("gitlab.com/")[-1].rstrip("/")
        owner, repo = parts.split("/")
        return owner, repo

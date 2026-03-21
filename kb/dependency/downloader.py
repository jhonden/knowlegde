"""知识库依赖下载器。"""

import hashlib
import os
import re
from pathlib import Path
from typing import Optional

import requests

from kb.exceptions import KnowledgeBaseError

# 常量定义
CHUNK_SIZE = 8192
REQUEST_TIMEOUT = 30
CACHE_DIR = Path.home() / ".kb-cache"
PACKAGE_NAME_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
VERSION_PATTERN = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9_.-]+)?$'


class PackageDownloader:
    """知识库发布包下载器。"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """初始化下载器。

        Args:
            cache_dir: 缓存目录，默认为 ~/.kb-cache
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self._validate_cache_dir(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download(self, name: str, version: str, git_url: str, force: bool = False) -> Path:
        """下载发布包。

        Args:
            name: 包名
            version: 版本号
            git_url: Git仓库URL
            force: 是否强制重新下载

        Returns:
            缓存文件路径

        Raises:
            KnowledgeBaseError: 下载失败时抛出
        """
        # 验证输入参数
        self._validate_inputs(name, version, git_url)

        # 构建缓存文件名（确保路径安全）
        cache_file = self._build_cache_path(name, version, git_url)

        # 检查缓存
        if cache_file.exists() and not force:
            return cache_file

        # 构建下载URL
        download_url = self._build_download_url(git_url, name, version)

        try:
            # 下载文件
            response = requests.get(download_url, stream=True, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # 写入缓存
            with open(cache_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)

            return cache_file

        except requests.exceptions.Timeout as e:
            # 清理可能的部分下载文件
            if cache_file.exists():
                cache_file.unlink()
            raise KnowledgeBaseError(f"下载超时: {e}")
        except requests.exceptions.HTTPError as e:
            # 清理可能的部分下载文件
            if cache_file.exists():
                cache_file.unlink()
            raise KnowledgeBaseError(f"HTTP错误: {e}")
        except requests.exceptions.ConnectionError as e:
            # 清理可能的部分下载文件
            if cache_file.exists():
                cache_file.unlink()
            raise KnowledgeBaseError(f"连接错误: {e}")
        except requests.exceptions.RequestException as e:
            # 清理可能的部分下载文件
            if cache_file.exists():
                cache_file.unlink()
            raise KnowledgeBaseError(f"下载失败: {e}")

    def _build_download_url(self, git_url: str, name: str, version: str) -> str:
        """构建下载URL。

        Args:
            git_url: Git仓库URL
            name: 包名
            version: 版本号

        Returns:
            下载URL

        Raises:
            KnowledgeBaseError: 不支持的URL格式
        """
        if "github.com" in git_url:
            # GitHub 格式: https://github.com/owner/repo/releases/download/v1.0.0/package.tar.gz
            owner, repo = self._extract_owner_repo(git_url)
            return f"https://github.com/{owner}/{repo}/releases/download/v{version}/{name}.tar.gz"
        elif "gitlab.com" in git_url:
            # GitLab 格式: https://gitlab.com/owner/repo/-/archive/v1.0.0/repo-v1.0.0.tar.gz
            owner, repo = self._extract_owner_repo(git_url)
            return f"https://gitlab.com/{owner}/{repo}/-/archive/v{version}/{repo}-v{version}.tar.gz"
        else:
            raise KnowledgeBaseError(f"不支持的Git平台: {git_url}")

    def _extract_owner_repo(self, git_url: str) -> tuple[str, str]:
        """从Git URL提取owner和repo。

        Args:
            git_url: Git仓库URL

        Returns:
            (owner, repo) 元组

        Raises:
            KnowledgeBaseError: URL格式错误
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
                    raise KnowledgeBaseError(f"无效的Git URL格式: {git_url}")
                return parts[0], parts[1]
            else:
                raise KnowledgeBaseError(f"无效的Git URL格式: {git_url}")
        except (ValueError, IndexError) as e:
            raise KnowledgeBaseError(f"解析Git URL失败: {e}")

    def _validate_cache_dir(self, cache_dir: Path) -> None:
        """验证缓存目录的安全性。

        Args:
            cache_dir: 缓存目录路径

        Raises:
            KnowledgeBaseError: 目录不安全
        """
        # 确保路径是绝对路径
        if not cache_dir.is_absolute():
            raise KnowledgeBaseError("缓存目录必须是绝对路径")

        # 解析路径并检查遍历攻击
        try:
            resolved_path = cache_dir.resolve()
        except (OSError, RuntimeError):
            raise KnowledgeBaseError(f"无法解析缓存目录路径: {cache_dir}")

        # 检查路径是否包含遍历序列
        if ".." in str(cache_dir):
            raise KnowledgeBaseError(f"不安全的缓存目录路径: {cache_dir}")

        # 检查路径是否试图访问敏感目录
        sensitive_dirs = ['/etc', '/var', '/usr', '/bin', '/sbin', '/lib', '/sys', '/proc']
        for sensitive_dir in sensitive_dirs:
            if str(resolved_path).startswith(sensitive_dir):
                raise KnowledgeBaseError(f"不允许使用敏感目录作为缓存目录: {cache_dir}")

    def _build_cache_path(self, name: str, version: str, git_url: str) -> Path:
        """构建安全的缓存文件路径。

        Args:
            name: 包名
            version: 版本号
            git_url: Git仓库URL

        Returns:
            缓存文件路径
        """
        url_hash = hashlib.md5(git_url.encode()).hexdigest()
        # 确保文件名只包含安全字符
        safe_name = re.sub(r'[^\w\-_.]', '_', name)
        safe_version = re.sub(r'[^\w\-_.]', '_', version)
        return self.cache_dir / f"{safe_name}_{safe_version}_{url_hash}.tar.gz"

    def _validate_inputs(self, name: str, version: str, git_url: str) -> None:
        """验证输入参数的有效性。

        Args:
            name: 包名
            version: 版本号
            git_url: Git仓库URL

        Raises:
            KnowledgeBaseError: 参数无效
        """
        if not name or not name.strip():
            raise KnowledgeBaseError("包名不能为空")

        if not re.match(PACKAGE_NAME_PATTERN, name):
            raise KnowledgeBaseError(f"包名格式无效: {name}")

        if not version or not version.strip():
            raise KnowledgeBaseError("版本号不能为空")

        if not re.match(VERSION_PATTERN, version):
            raise KnowledgeBaseError(f"版本号格式无效: {version}")

        if not git_url or not git_url.strip():
            raise KnowledgeBaseError("Git URL不能为空")

        # 验证URL格式
        if not (git_url.startswith("https://") or git_url.startswith("http://")):
            raise KnowledgeBaseError(f"Git URL格式无效: {git_url}")

        # 确保URL包含GitHub或GitLab域名
        if "github.com" not in git_url and "gitlab.com" not in git_url:
            raise KnowledgeBaseError(f"只支持GitHub和GitLab: {git_url}")
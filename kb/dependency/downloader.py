"""知识库依赖下载器。"""

import hashlib
import os
from pathlib import Path
from typing import Optional

import requests

from kb.exceptions import KnowledgeBaseError


class PackageDownloader:
    """知识库发布包下载器。"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """初始化下载器。

        Args:
            cache_dir: 缓存目录，默认为 ~/.kb-cache
        """
        self.cache_dir = cache_dir or Path.home() / ".kb-cache"
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
        # 构建缓存文件名
        url_hash = hashlib.md5(git_url.encode()).hexdigest()
        cache_file = self.cache_dir / f"{name}_{version}_{url_hash}.tar.gz"

        # 检查缓存
        if cache_file.exists() and not force:
            return cache_file

        # 构建下载URL
        download_url = self._build_download_url(git_url, name, version)

        try:
            # 下载文件
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # 写入缓存
            with open(cache_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return cache_file

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
                return path.split("/", 1)
            else:
                raise KnowledgeBaseError(f"无效的Git URL格式: {git_url}")
        except Exception as e:
            raise KnowledgeBaseError(f"解析Git URL失败: {e}")
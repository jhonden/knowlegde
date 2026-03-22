"""知识库依赖下载器。"""

import hashlib
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
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
PUBLISH_DIR = "publish"


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
        """从Git仓库的publish/目录下载并解压发布包到版本目录。

        Args:
            name: 包名
            version: 版本号
            git_url: Git仓库URL
            force: 是否强制重新下载

        Returns:
            版本目录路径 (cache_dir/name/version/)

        Raises:
            KnowledgeBaseError: 下载或解压失败时抛出
        """
        # 验证输入参数
        self._validate_inputs(name, version, git_url)

        # 构建版本目录路径
        version_dir = self._build_version_dir_path(name, version)

        # 检查缓存（版本目录已存在）
        if version_dir.exists() and not force:
            return version_dir

        # 创建临时目录用于clone仓库
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_repo_path = Path(temp_dir) / "repo"
            try:
                # Clone Git 仓库到临时目录（只获取最新提交，不获取历史）
                subprocess.run(
                    ["git", "clone", "--depth", "1", git_url, str(temp_repo_path)],
                    check=True,
                    capture_output=True,
                    text=True
                )

                # 查找发布包文件
                package_file = self._find_package_file(temp_repo_path, name, version)

                # 解压到版本目录
                self._extract_downloaded_package(package_file, version_dir)

                return version_dir

            except subprocess.CalledProcessError as e:
                raise KnowledgeBaseError(f"克隆Git仓库失败: {e.stderr}")
            except FileNotFoundError:
                raise KnowledgeBaseError("未找到git命令，请先安装git")
            finally:
                # 临时目录会自动清理
                pass

    def _find_package_file(self, repo_path: Path, name: str, version: str) -> Path:
        """在仓库的publish/目录中查找发布包文件。

        Args:
            repo_path: Git仓库路径
            name: 包名
            version: 版本号

        Returns:
            发布包文件路径

        Raises:
            KnowledgeBaseError: 未找到发布包文件
        """
        publish_dir = repo_path / PUBLISH_DIR
        if not publish_dir.exists():
            raise KnowledgeBaseError(f"仓库中未找到publish/目录: {repo_path}")

        # 期望的文件名格式: <name>-<version>.tar.gz
        expected_filename = f"{name}-{version}.tar.gz"
        package_file = publish_dir / expected_filename

        if not package_file.exists():
            # 列出publish/目录中的所有文件，帮助调试
            available_files = [f.name for f in publish_dir.iterdir() if f.is_file()]
            raise KnowledgeBaseError(
                f"在publish/目录中未找到 {expected_filename}\n"
                f"可用的文件: {', '.join(available_files) if available_files else '无'}"
            )

        return package_file

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

    def _build_version_dir_path(self, name: str, version: str) -> Path:
        """构建版本目录路径。

        Args:
            name: 包名
            version: 版本号

        Returns:
            版本目录路径 (cache_dir/name/version/)
        """
        # 确保文件名只包含安全字符
        safe_name = re.sub(r'[^\w\-_.]', '_', name)
        safe_version = re.sub(r'[^\w\-_.]', '_', version)
        return self.cache_dir / safe_name / safe_version

    def _extract_downloaded_package(self, package_path: Path, version_dir: Path) -> None:
        """解压下载的包到版本目录。

        Args:
            package_path: 下载的tar.gz文件路径
            version_dir: 目标版本目录

        Raises:
            KnowledgeBaseError: 解压失败时抛出
        """
        import shutil

        # 验证包文件是否存在
        if not package_path.exists():
            raise KnowledgeBaseError(f"发布包文件不存在: {package_path}")

        # 验证包是否为文件
        if not package_path.is_file():
            raise KnowledgeBaseError(f"发布包路径必须是文件: {package_path}")

        # 创建版本目录（包括所有父目录）
        try:
            version_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise KnowledgeBaseError(f"无法创建版本目录 {version_dir}: {e}")

        # 验证文件是否为 tar.gz 格式
        if not package_path.name.endswith('.tar.gz'):
            raise KnowledgeBaseError(f"只支持 .tar.gz 格式的发布包: {package_path}")

        # 清空版本目录（如果是重新下载）
        if version_dir.exists() and any(version_dir.iterdir()):
            for item in version_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        # 解压发布包
        try:
            with tarfile.open(package_path, 'r:gz') as tar:
                # 安全验证：检查是否有路径遍历攻击
                members = tar.getmembers()
                for member in members:
                    # 检查成员路径是否包含遍历序列
                    if '..' in member.name or member.name.startswith('/'):
                        raise KnowledgeBaseError(f"发布包包含不安全路径: {member.name}")

                    # 检查目标路径是否会超出目标目录
                    target_member_path = version_dir / member.name
                    try:
                        target_member_path.resolve().relative_to(version_dir.resolve())
                    except ValueError:
                        raise KnowledgeBaseError(f"发布包包含试图逃逸目标目录的路径: {member.name}")

                # 解压文件
                tar.extractall(path=version_dir)

        except tarfile.ReadError as e:
            raise KnowledgeBaseError(f"无法读取tar.gz文件: {e}")
        except tarfile.ExtractError as e:
            raise KnowledgeBaseError(f"解压文件失败: {e}")
        except OSError as e:
            raise KnowledgeBaseError(f"文件操作失败: {e}")
        except Exception as e:
            raise KnowledgeBaseError(f"解压过程中发生未知错误: {e}")

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

        # 验证URL格式（支持 https://, http://, git@）
        valid_prefixes = ("https://", "http://", "git@")
        if not git_url.startswith(valid_prefixes):
            raise KnowledgeBaseError(f"Git URL格式无效: {git_url}")
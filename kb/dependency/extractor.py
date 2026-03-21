"""知识库发布包解压器。"""

import tarfile
from pathlib import Path
from typing import Optional

from kb.exceptions import KnowledgeBaseError


class PackageExtractor:
    """知识库发布包解压器。"""

    def extract(self, package_path: Path, target_dir: Path) -> None:
        """解压发布包。

        Args:
            package_path: 发布包文件路径
            target_dir: 解压目标目录

        Raises:
            KnowledgeBaseError: 解压失败时抛出
        """
        # 验证发布包文件是否存在
        if not package_path.exists():
            raise KnowledgeBaseError(f"发布包文件不存在: {package_path}")

        # 验证发布包是否为文件
        if not package_path.is_file():
            raise KnowledgeBaseError(f"发布包路径必须是文件: {package_path}")

        # 创建目标目录（包括所有父目录）
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise KnowledgeBaseError(f"无法创建目标目录 {target_dir}: {e}")

        # 验证文件是否为 tar.gz 格式
        if not package_path.name.endswith('.tar.gz'):
            raise KnowledgeBaseError(f"只支持 .tar.gz 格式的发布包: {package_path}")

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
                    target_member_path = target_dir / member.name
                    try:
                        target_member_path.resolve().relative_to(target_dir.resolve())
                    except ValueError:
                        raise KnowledgeBaseError(f"发布包包含试图逃逸目标目录的路径: {member.name}")

                # 解压文件
                tar.extractall(path=target_dir)

        except tarfile.ReadError as e:
            raise KnowledgeBaseError(f"无法读取tar.gz文件: {e}")
        except tarfile.ExtractError as e:
            raise KnowledgeBaseError(f"解压文件失败: {e}")
        except OSError as e:
            raise KnowledgeBaseError(f"文件操作失败: {e}")
        except Exception as e:
            raise KnowledgeBaseError(f"解压过程中发生未知错误: {e}")
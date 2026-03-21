# kb/core/validator.py
"""知识库验证器模块，用于验证知识库元数据的有效性。"""

from typing import Dict, List

from kb.core.models import KnowledgeMetadata
from kb.exceptions import DependencyConflictError


class KnowledgeValidator:
    """知识库验证器类。"""

    def __init__(self):
        """初始化验证器。"""
        pass

    def validate(self, metadata: KnowledgeMetadata) -> None:
        """
        验证知识库元数据的有效性。

        Args:
            metadata: 知识库元数据对象

        Raises:
            DependencyConflictError: 当检测到依赖版本冲突时抛出
        """
        # 验证排除依赖配置
        self._validate_excluded_dependencies(metadata)

        # 验证依赖版本冲突
        self._validate_version_conflicts(metadata)

    def _validate_version_conflicts(self, metadata: KnowledgeMetadata) -> None:
        """
        验证依赖项是否存在版本冲突。

        检查同一名称的依赖是否使用不同的版本号。

        Args:
            metadata: 知识库元数据对象

        Raises:
            DependencyConflictError: 当检测到版本冲突时抛出
        """
        # 按依赖名称分组
        version_map: Dict[str, List[str]] = {}

        for dep in metadata.dependencies:
            if dep.name not in version_map:
                version_map[dep.name] = []
            version_map[dep.name].append(dep.version)

        # 检查每个依赖是否存在多个版本
        for name, versions in version_map.items():
            if len(versions) > 1:
                # 移除重复版本号
                unique_versions = list(set(versions))
                if len(unique_versions) > 1:
                    sorted_versions = sorted(unique_versions)
                    raise DependencyConflictError(
                        f"依赖项 '{name}' 存在版本冲突: {', '.join(sorted_versions)}"
                    )

    def _validate_excluded_dependencies(self, metadata: KnowledgeMetadata) -> None:
        """
        验证排除依赖配置的有效性。

        Args:
            metadata: 知识库元数据对象

        Raises:
            DependencyConflictError: 当排除依赖配置无效时抛出
        """
        # 按排除依赖名称分组
        excluded_map: Dict[str, List[str]] = {}

        for excluded in metadata.excluded_dependencies:
            if excluded.name not in excluded_map:
                excluded_map[excluded.name] = []
            excluded_map[excluded.name].append(excluded.version)

        # 检查排除的依赖是否存在版本冲突
        for name, versions in excluded_map.items():
            if len(versions) > 1:
                # 移除重复版本号
                unique_versions = list(set(versions))
                if len(unique_versions) > 1:
                    sorted_versions = sorted(unique_versions)
                    raise DependencyConflictError(
                        f"排除依赖项 '{name}' 存在版本冲突: {', '.join(sorted_versions)}"
                    )

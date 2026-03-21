"""知识库依赖解析器。"""

from __future__ import annotations
from typing import List
from pathlib import Path

from kb.core.models import Dependency, KnowledgeMetadata, ExcludedDependency


class DependencyResolver:
    """依赖解析器类。"""

    def __init__(self, cache_dir: Path | None = None, deps_dir: Path | None = None):
        """
        初始化依赖解析器。

        Args:
            cache_dir: 缓存目录
            deps_dir: 依赖安装目录，默认为当前目录下的 deps/
        """
        self.cache_dir = cache_dir
        self.deps_dir = deps_dir or Path.cwd() / "deps"

        # 确保依赖目录存在
        self.deps_dir.mkdir(parents=True, exist_ok=True)

    def resolve(self, metadata: KnowledgeMetadata) -> List[Dependency]:
        """
        解析知识库元数据中的依赖项。

        Args:
            metadata: 知识库元数据

        Returns:
            解析后的依赖列表，过滤掉被排除的依赖
        """
        # 获取排除的依赖版本（使用字典存储，提高查找效率）
        excluded_deps = {}
        for excluded in metadata.excluded_dependencies:
            excluded_deps[excluded.name] = excluded.version

        # 过滤掉被排除的依赖
        resolved_dependencies = []
        for dependency in metadata.dependencies:
            if dependency.name in excluded_deps:
                # 比较版本号
                excluded_version = excluded_deps[dependency.name]
                if dependency.version == excluded_version:
                    continue  # 跳过被排除的依赖

            resolved_dependencies.append(dependency)

        return resolved_dependencies

    def get_install_path(self, dependency: Dependency) -> Path:
        """
        获取依赖的安装路径。

        Args:
            dependency: 依赖项

        Returns:
            安装路径
        """
        return self.deps_dir / f"{dependency.name}-{dependency.version}"
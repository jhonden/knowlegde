"""知识库依赖管理模块。"""

from .downloader import PackageDownloader
from .extractor import PackageExtractor
from .conflict import ConflictDetector
from .resolver import DependencyResolver

__all__ = ['PackageDownloader', 'PackageExtractor', 'ConflictDetector', 'DependencyResolver']
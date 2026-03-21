"""知识库核心模块。"""

from .models import Dependency, ExcludedDependency, KnowledgeMetadata
from .validator import KnowledgeValidator

__all__ = ["Dependency", "ExcludedDependency", "KnowledgeMetadata", "KnowledgeValidator"]

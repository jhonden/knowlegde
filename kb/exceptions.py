"""知识库系统自定义异常类。"""


class KnowledgeBaseError(Exception):
    """知识库基础异常。"""

    pass


class KnowledgeParseError(KnowledgeBaseError):
    """知识库解析错误。"""

    pass


class VersionFormatError(KnowledgeBaseError):
    """版本号格式错误。"""

    pass


class DependencyConflictError(KnowledgeBaseError):
    """依赖冲突错误。"""

    pass

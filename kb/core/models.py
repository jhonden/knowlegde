"""知识库核心数据模型。"""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Dependency(BaseModel):
    """知识库依赖项。

    Attributes:
        name: 依赖名称
        version: 依赖版本号（语义化版本：主版本.次版本.修订版本）
        git_url: Git仓库URL
    """

    name: str = Field(..., description="依赖名称")
    version: str = Field(..., description="依赖版本号")
    git_url: str = Field(..., description="Git仓库URL")

    @field_validator("version")
    @classmethod
    def validate_semantic_version(cls, v: str) -> str:
        """验证语义化版本号格式。

        Args:
            v: 版本号字符串

        Returns:
            验证通过的版本号

        Raises:
            ValueError: 如果版本号格式不符合语义化版本规范
        """
        # 语义化版本格式：主版本.次版本.修订版本
        # 每个部分必须是正整数
        pattern = r"^(\d+)\.(\d+)\.(\d+)$"
        if not re.match(pattern, v):
            raise ValueError(
                f"版本号格式错误，必须为语义化版本号格式（主版本.次版本.修订版本），例如：1.2.3，当前值：{v}"
            )
        return v


class ExcludedDependency(BaseModel):
    """排除的依赖项。

    Attributes:
        name: 依赖名称
        version: 依赖版本号
        reason: 排除原因
    """

    name: str = Field(..., description="依赖名称")
    version: str = Field(..., description="依赖版本号")
    reason: str = Field(..., description="排除原因")


class KnowledgeMetadata(BaseModel):
    """知识库元数据。

    Attributes:
        name: 知识库名称
        version: 知识库版本号
        type: 知识库类型（如：agent、tool、data等）
        description: 知识库描述
        dependencies: 依赖列表
        excluded_dependencies: 排除的依赖列表
        scenarios: 应用场景列表
        capabilities: 能力列表
        file_graph: 文件图结构
    """

    name: str = Field(..., description="知识库名称")
    version: str = Field(..., description="知识库版本号")
    type: str = Field(..., description="知识库类型")
    description: Optional[str] = Field(None, description="知识库描述")
    dependencies: list[Dependency] = Field(default_factory=list, description="依赖列表")
    excluded_dependencies: list[ExcludedDependency] = Field(
        default_factory=list, description="排除的依赖列表"
    )
    scenarios: list[str] = Field(default_factory=list, description="应用场景列表")
    capabilities: list[str] = Field(default_factory=list, description="能力列表")
    file_graph: Optional[dict] = Field(None, description="文件图结构")

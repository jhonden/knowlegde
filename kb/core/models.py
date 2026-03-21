# kb/core/models.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from kb.exceptions import VersionFormatError


class Dependency(BaseModel):
    """知识库依赖项"""
    name: str = Field(..., description="知识库名称")
    version: str = Field(..., description="版本号")
    git_url: str = Field(..., description="git仓库地址")

    @field_validator("version")
    @classmethod
    def validate_semantic_version(cls, v: str) -> str:
        """验证语义化版本号格式"""
        parts = v.split(".")
        if len(parts) != 3:
            raise VersionFormatError(f"版本号 '{v}' 必须为主版本.次版本.修订版本格式")
        try:
            int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            raise VersionFormatError(f"版本号 '{v}' 的各部分必须为数字")
        return v


class ExcludedDependency(BaseModel):
    """排除的依赖项"""
    name: str = Field(..., description="知识库名称")
    version: str = Field(..., description="版本号")
    reason: str = Field(..., description="排除原因")


class KnowledgeMetadata(BaseModel):
    """知识库元数据"""
    name: str = Field(..., description="知识库名称")
    version: str = Field(..., description="版本号")
    type: str = Field(..., description="知识库类型")
    description: str = Field(..., description="职责描述")
    dependencies: List[Dependency] = Field(default_factory=list, description="依赖列表")
    excluded_dependencies: List[ExcludedDependency] = Field(
        default_factory=list, description="排除依赖列表"
    )
    scenarios: str = Field(default="", description="适用场景")
    capabilities: List[str] = Field(default_factory=list, description="对外能力列表")
    file_graph: str = Field(default="", description="文件路径图谱")

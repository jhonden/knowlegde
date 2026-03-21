"""版本更新数据模型。"""

from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class VersionUpdate(BaseModel):
    """单个依赖的版本更新信息。"""
    name: str = Field(..., description="依赖名称")
    current_version: str = Field(..., description="当前版本")
    latest_version: str = Field(..., description="最新版本")
    git_url: str = Field(..., description="Git仓库地址")
    update_available: bool = Field(default=True, description="是否有可用更新")


class VersionUpdateList(BaseModel):
    """版本更新列表。"""
    updates: List[VersionUpdate] = Field(default_factory=list, description="更新列表")

    def add_update(self, update: VersionUpdate) -> None:
        """添加一个更新信息。"""
        self.updates.append(update)

    def has_updates(self) -> bool:
        """检查是否有可用更新。"""
        return len(self.updates) > 0

    def __len__(self) -> int:
        """返回更新数量。"""
        return len(self.updates)

    def __iter__(self):
        """支持迭代。"""
        return iter(self.updates)

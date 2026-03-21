from __future__ import annotations
import re
from pathlib import Path
from typing import List, Optional
from kb.core.models import KnowledgeMetadata, Dependency, ExcludedDependency
from kb.exceptions import KnowledgeParseError


class KnowledgeParser:
    """Knowledge.md 解析器"""

    def __init__(self):
        pass

    def parse(self, file_path: Path) -> KnowledgeMetadata:
        """解析Knowledge.md文件"""
        if not file_path.exists():
            raise FileNotFoundError(f"知识库文件不存在: {file_path}")

        # 跨平台：显式指定 newline='\n' 确保一致性
        with open(file_path, "r", encoding="utf-8", newline='\n') as f:
            content = f.read()

        # 提取基本信息
        name = self._extract_value(content, "名称")
        version = self._extract_value(content, "版本")
        kb_type = self._extract_value(content, "类型")
        description = self._extract_value(content, "职责描述")

        # 提取适用场景
        scenarios = self._extract_section_text(content, "适用场景")

        # 提取对外能力
        capabilities = self._extract_list_items(content, "对外能力")

        # 提取文件路径图谱
        file_graph = self._extract_code_block(content, "文件路径图谱")

        # 提取依赖
        dependencies = self._parse_dependency_table(content)

        # 提取排除依赖
        excluded_dependencies = self._parse_excluded_dependency_table(content)

        return KnowledgeMetadata(
            name=name,
            version=version,
            type=kb_type,
            description=description,
            dependencies=dependencies,
            excluded_dependencies=excluded_dependencies,
            scenarios=scenarios,
            capabilities=capabilities,
            file_graph=file_graph,
        )

    def _extract_value(self, content: str, field_name: str) -> str:
        """提取字段值"""
        pattern = rf"- \*\*{field_name}\*\*:\s*(.+)"
        match = re.search(pattern, content)
        if not match:
            raise KnowledgeParseError(f"未找到字段: {field_name}")
        return match.group(1).strip()

    def _extract_section_text(self, content: str, section_name: str) -> str:
        """提取章节文本"""
        pattern = rf"## {section_name}\n\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_list_items(self, content: str, section_name: str) -> List[str]:
        """提取列表项"""
        items = []
        pattern = rf"## {section_name}\n\n((?:- .+\n?)+)"
        match = re.search(pattern, content)
        if match:
            for line in match.group(1).split("\n"):
                if line.strip().startswith("-"):
                    item = line.strip()[1:].strip()
                    if item:
                        items.append(item)
        return items

    def _extract_code_block(self, content: str, section_name: str) -> str:
        """提取代码块"""
        pattern = rf"## {section_name}\n\n```(\w+)?\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(2).strip()
        return ""

    def _parse_dependency_table(self, content: str) -> List[Dependency]:
        """解析依赖表"""
        dependencies = []
        pattern = r"## 依赖\n\n\|.*?\n\|.*?\n((?:\|.*?\n)+)"
        match = re.search(pattern, content)
        if match:
            rows = match.group(1).strip().split("\n")
            for row in rows:  # 不需要跳过，因为pattern已经排除了表头
                if "|" in row:
                    cols = [col.strip() for col in row.split("|")[1:-1]]
                    if len(cols) >= 3 and cols[0]:
                        dependencies.append(
                            Dependency(name=cols[0], version=cols[1], git_url=cols[2])
                        )
        return dependencies

    def _parse_excluded_dependency_table(self, content: str) -> List[ExcludedDependency]:
        """解析排除依赖表"""
        excluded = []
        pattern = r"## 排除依赖\n\n\|.*?\n\|.*?\n((?:\|.*?\n)+)"
        match = re.search(pattern, content)
        if match:
            rows = match.group(1).strip().split("\n")
            for row in rows:  # 不需要跳过，因为pattern已经排除了表头
                if "|" in row:
                    cols = [col.strip() for col in row.split("|")[1:-1]]
                    if len(cols) >= 3 and cols[0]:
                        excluded.append(
                            ExcludedDependency(name=cols[0], version=cols[1], reason=cols[2])
                        )
        return excluded

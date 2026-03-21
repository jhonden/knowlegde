"""Knowledge.md解析器。"""

import json
import re
from pathlib import Path
from typing import Optional

from kb.core.models import Dependency, ExcludedDependency, KnowledgeMetadata


class KnowledgeParser:
    """Knowledge.md文件解析器。

    使用正则表达式解析Markdown格式的知识库文件，提取元数据信息。
    """

    def parse(self, file_path: str) -> KnowledgeMetadata:
        """解析Knowledge.md文件。

        Args:
            file_path: Knowledge.md文件的绝对路径

        Returns:
            KnowledgeMetadata对象，包含解析后的元数据

        Raises:
            FileNotFoundError: 如果文件不存在
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"知识库文件不存在：{file_path}")

        # 使用newline='\n'确保跨平台一致性
        with open(path, "r", encoding="utf-8", newline="\n") as f:
            content = f.read()

        # 提取各字段
        name = self._extract_value(content, "知识库名称")
        version = self._extract_value(content, "版本")
        kb_type = self._extract_value(content, "类型")
        description = self._extract_section_text(content, "描述")
        dependencies = self._parse_dependency_table(content)
        excluded_dependencies = self._parse_excluded_dependency_table(content)
        scenarios = self._extract_list_items(content, "应用场景")
        capabilities = self._extract_list_items(content, "能力")
        file_graph = self._extract_code_block(content, "文件图结构")

        # 解析文件图结构的JSON
        if file_graph:
            try:
                file_graph = json.loads(file_graph)
            except json.JSONDecodeError:
                file_graph = None

        # 构建并返回KnowledgeMetadata对象
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

    def _extract_value(self, content: str, section_name: str) -> str:
        """提取章节的值。

        Args:
            content: 文件内容
            section_name: 章节名称

        Returns:
            章节的值，如果不存在则返回空字符串
        """
        # 匹配**名称**: value格式
        pattern = rf"^##\s+{re.escape(section_name)}\s*$\n(?:\n)?\*\*{re.escape(section_name)}\*\*:\s*([^\n]+)"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_section_text(self, content: str, section_name: str) -> Optional[str]:
        """提取章节的文本内容。

        Args:
            content: 文件内容
            section_name: 章节名称

        Returns:
            章节的文本内容，如果不存在则返回None
        """
        # 匹配从章节标题到下一个标题或文件结束之间的所有文本
        pattern = rf"^##\s+{re.escape(section_name)}\s*$\n(?:\n)?(.+?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            return text if text else None
        return None

    def _extract_list_items(self, content: str, section_name: str) -> list[str]:
        """提取章节的列表项。

        Args:
            content: 文件内容
            section_name: 章节名称

        Returns:
            列表项列表
        """
        # 匹配从章节标题到下一个标题或文件结束之间的内容
        pattern = rf"^##\s+{re.escape(section_name)}\s*$\n(?:\n)?((?:[^\n]+\n)+?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            items_text = match.group(1)
            items = []
            for line in items_text.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    item = line[2:].strip()
                    if item:
                        items.append(item)
            return items
        return []

    def _extract_code_block(self, content: str, section_name: str) -> Optional[str]:
        """提取章节的代码块内容。

        Args:
            content: 文件内容
            section_name: 章节名称

        Returns:
            代码块内容，如果不存在则返回None
        """
        pattern = rf"^##\s+{re.escape(section_name)}\s*$\n(?:\n)?```(?:json)?\s*\n(.+?)\n```"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            code = match.group(1).strip()
            return code if code else None
        return None

    def _parse_dependency_table(self, content: str) -> list[Dependency]:
        """解析依赖表格。

        Args:
            content: 文件内容

        Returns:
            Dependency对象列表
        """
        # 匹配从"依赖"标题到下一个标题或文件结束之间的表格
        pattern = r"^##\s+依赖\s*$\n(?:\n)?((?:\|[^\n]+\n)+?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.MULTILINE)
        if not match:
            return []

        dependencies = []
        rows = match.group(1).strip().split("\n")
        # 跳过表头行（第一行）
        for row in rows[1:]:
            row = row.strip()
            if row.startswith("|") and row.endswith("|"):
                cells = [cell.strip() for cell in row.split("|")[1:-1]]
                if len(cells) >= 3:
                    dependencies.append(
                        Dependency(
                            name=cells[0],
                            version=cells[1],
                            git_url=cells[2],
                        )
                    )
        return dependencies

    def _parse_excluded_dependency_table(self, content: str) -> list[ExcludedDependency]:
        """解析排除依赖表格。

        Args:
            content: 文件内容

        Returns:
            ExcludedDependency对象列表
        """
        # 匹配从"排除的依赖"标题到下一个标题或文件结束之间的表格
        pattern = r"^##\s+排除的依赖\s*$\n(?:\n)?((?:\|[^\n]+\n)+?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.MULTILINE)
        if not match:
            return []

        excluded_dependencies = []
        rows = match.group(1).strip().split("\n")
        # 跳过表头行（第一行）
        for row in rows[1:]:
            row = row.strip()
            if row.startswith("|") and row.endswith("|"):
                cells = [cell.strip() for cell in row.split("|")[1:-1]]
                if len(cells) >= 3:
                    excluded_dependencies.append(
                        ExcludedDependency(
                            name=cells[0],
                            version=cells[1],
                            reason=cells[2],
                        )
                    )
        return excluded_dependencies

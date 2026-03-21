"""测试Knowledge.md解析器。"""

import pytest

from kb.core.models import Dependency, ExcludedDependency, KnowledgeMetadata


class TestKnowledgeParser:
    """测试KnowledgeParser类。"""

    def test_parse_valid_knowledge(self):
        """验证解析完整知识库。"""
        from kb.core.parser import KnowledgeParser

        parser = KnowledgeParser()
        metadata = parser.parse("/Users/gaowen/Code/knowlegde/tests/core/fixtures/valid_knowledge.md")

        # 验证基本信息
        assert metadata.name == "test-knowledge"
        assert metadata.version == "1.2.3"
        assert metadata.type == "agent"
        assert metadata.description == "这是一个测试知识库，用于验证解析器的功能。"

        # 验证依赖
        assert len(metadata.dependencies) == 2
        assert metadata.dependencies[0].name == "dep1"
        assert metadata.dependencies[0].version == "1.0.0"
        assert metadata.dependencies[0].git_url == "https://github.com/test/dep1.git"
        assert metadata.dependencies[1].name == "dep2"
        assert metadata.dependencies[1].version == "2.3.4"
        assert metadata.dependencies[1].git_url == "https://github.com/test/dep2.git"

        # 验证排除的依赖
        assert len(metadata.excluded_dependencies) == 1
        assert metadata.excluded_dependencies[0].name == "old-dep"
        assert metadata.excluded_dependencies[0].version == "0.5.0"
        assert metadata.excluded_dependencies[0].reason == "已弃用，不再维护"

        # 验证应用场景
        assert len(metadata.scenarios) == 3
        assert "场景一：自动化测试" in metadata.scenarios
        assert "场景二：代码生成" in metadata.scenarios
        assert "场景三：数据分析" in metadata.scenarios

        # 验证能力
        assert len(metadata.capabilities) == 3
        assert "自然语言处理" in metadata.capabilities
        assert "代码分析" in metadata.capabilities
        assert "自动化测试" in metadata.capabilities

        # 验证文件图结构
        assert metadata.file_graph is not None
        assert "nodes" in metadata.file_graph
        assert "edges" in metadata.file_graph

    def test_parse_minimal_knowledge(self):
        """验证解析最小知识库。"""
        from kb.core.parser import KnowledgeParser

        parser = KnowledgeParser()
        metadata = parser.parse("/Users/gaowen/Code/knowlegde/tests/core/fixtures/minimal_knowledge.md")

        # 验证基本信息
        assert metadata.name == "minimal-kb"
        assert metadata.version == "1.0.0"
        assert metadata.type == "tool"

        # 验证默认值
        assert metadata.description is None
        assert metadata.dependencies == []
        assert metadata.excluded_dependencies == []
        assert metadata.scenarios == []
        assert metadata.capabilities == []
        assert metadata.file_graph is None

    def test_parse_nonexistent_file(self):
        """验证文件不存在时抛出FileNotFoundError。"""
        from kb.core.parser import KnowledgeParser

        parser = KnowledgeParser()
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.md")

"""测试核心数据模型。"""

import pytest
from pydantic import ValidationError

from kb.core.models import Dependency, ExcludedDependency, KnowledgeMetadata
from kb.exceptions import VersionFormatError


class TestDependency:
    """测试Dependency模型。"""

    def test_dependency_valid(self):
        """验证有效依赖。"""
        dependency = Dependency(name="test-kb", version="1.2.3", git_url="https://github.com/test/test-kb.git")
        assert dependency.name == "test-kb"
        assert dependency.version == "1.2.3"
        assert dependency.git_url == "https://github.com/test/test-kb.git"

    def test_dependency_invalid_version_format(self):
        """验证版本号格式错误。"""
        with pytest.raises(ValidationError) as exc_info:
            Dependency(name="test-kb", version="1.2", git_url="https://github.com/test/test-kb.git")
        assert "version" in str(exc_info.value).lower()

    def test_dependency_invalid_version_non_numeric(self):
        """验证版本号非数字错误。"""
        with pytest.raises(ValidationError) as exc_info:
            Dependency(name="test-kb", version="a.b.c", git_url="https://github.com/test/test-kb.git")
        assert "version" in str(exc_info.value).lower()


class TestExcludedDependency:
    """测试ExcludedDependency模型。"""

    def test_excluded_dependency_valid(self):
        """验证有效排除依赖。"""
        excluded = ExcludedDependency(name="test-kb", version="1.2.3", reason="已弃用")
        assert excluded.name == "test-kb"
        assert excluded.version == "1.2.3"
        assert excluded.reason == "已弃用"


class TestKnowledgeMetadata:
    """测试KnowledgeMetadata模型。"""

    def test_knowledge_metadata_minimal(self):
        """验证最小元数据。"""
        metadata = KnowledgeMetadata(
            name="test-kb",
            version="1.0.0",
            type="agent"
        )
        assert metadata.name == "test-kb"
        assert metadata.version == "1.0.0"
        assert metadata.type == "agent"
        assert metadata.description is None
        assert metadata.dependencies == []
        assert metadata.excluded_dependencies == []
        assert metadata.scenarios == []
        assert metadata.capabilities == []
        assert metadata.file_graph is None

    def test_knowledge_metadata_with_dependencies(self):
        """验证带依赖的元数据。"""
        metadata = KnowledgeMetadata(
            name="test-kb",
            version="1.0.0",
            type="agent",
            description="测试知识库",
            dependencies=[
                Dependency(name="dep1", version="1.2.3", git_url="https://github.com/dep1.git"),
                Dependency(name="dep2", version="2.0.0", git_url="https://github.com/dep2.git")
            ],
            excluded_dependencies=[
                ExcludedDependency(name="old-dep", version="0.9.0", reason="不兼容")
            ],
            scenarios=["场景1", "场景2"],
            capabilities=["能力1"],
            file_graph={"nodes": [], "edges": []}
        )
        assert len(metadata.dependencies) == 2
        assert len(metadata.excluded_dependencies) == 1
        assert len(metadata.scenarios) == 2
        assert metadata.capabilities == ["能力1"]
        assert metadata.file_graph == {"nodes": [], "edges": []}

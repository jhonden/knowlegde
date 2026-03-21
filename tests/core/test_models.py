# tests/core/test_models.py
import pytest
from pydantic import ValidationError
from kb.core.models import Dependency, ExcludedDependency, KnowledgeMetadata
from kb.exceptions import VersionFormatError


def test_dependency_valid():
    dep = Dependency(name="TestLib", version="1.2.0", git_url="https://github.com/test/lib")
    assert dep.name == "TestLib"
    assert dep.version == "1.2.0"
    assert dep.git_url == "https://github.com/test/lib"


def test_dependency_invalid_version_format():
    with pytest.raises(VersionFormatError):
        Dependency(name="TestLib", version="1.2", git_url="https://github.com/test/lib")


def test_dependency_invalid_version_non_numeric():
    with pytest.raises(VersionFormatError):
        Dependency(name="TestLib", version="1.a.0", git_url="https://github.com/test/lib")


def test_excluded_dependency_valid():
    excluded = ExcludedDependency(
        name="TestLib", version="1.2.0", reason="与其他依赖冲突"
    )
    assert excluded.name == "TestLib"
    assert excluded.version == "1.2.0"
    assert excluded.reason == "与其他依赖冲突"


def test_knowledge_metadata_minimal():
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test-type",
        description="测试知识库"
    )
    assert metadata.name == "TestLib"
    assert metadata.version == "1.0.0"
    assert len(metadata.dependencies) == 0


def test_knowledge_metadata_with_dependencies():
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test-type",
        description="测试知识库",
        dependencies=[
            Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1")
        ]
    )
    assert len(metadata.dependencies) == 1
    assert metadata.dependencies[0].name == "Dep1"

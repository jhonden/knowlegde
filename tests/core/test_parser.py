# tests/core/test_parser.py
import pytest
from pathlib import Path
from kb.core.parser import KnowledgeParser
from kb.core.models import KnowledgeMetadata
from kb.exceptions import KnowledgeParseError


@pytest.fixture
def valid_knowledge_md():
    return Path(__file__).parent / "fixtures" / "valid_knowledge.md"


@pytest.fixture
def minimal_knowledge_md():
    return Path(__file__).parent / "fixtures" / "minimal_knowledge.md"


def test_parse_valid_knowledge(valid_knowledge_md):
    parser = KnowledgeParser()
    metadata = parser.parse(valid_knowledge_md)

    assert isinstance(metadata, KnowledgeMetadata)
    assert metadata.name == "FileFormatParser"
    assert metadata.version == "1.2.0"
    assert metadata.type == "structure-knowledge"
    assert metadata.description == "封装特定文件格式的解析知识"
    assert len(metadata.dependencies) == 1
    assert metadata.dependencies[0].name == "CommonDataTypes"
    assert len(metadata.excluded_dependencies) == 1
    assert "文件格式解析" in metadata.scenarios
    assert len(metadata.capabilities) == 2


def test_parse_minimal_knowledge(minimal_knowledge_md):
    parser = KnowledgeParser()
    metadata = parser.parse(minimal_knowledge_md)

    assert metadata.name == "MinimalLib"
    assert metadata.version == "1.0.0"
    assert len(metadata.dependencies) == 0
    assert len(metadata.capabilities) == 0


def test_parse_nonexistent_file():
    parser = KnowledgeParser()
    with pytest.raises(FileNotFoundError):
        parser.parse(Path("nonexistent.md"))

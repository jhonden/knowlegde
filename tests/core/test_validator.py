# tests/core/test_validator.py
import pytest
from kb.core.validator import KnowledgeValidator
from kb.core.models import KnowledgeMetadata, Dependency, ExcludedDependency
from kb.exceptions import DependencyConflictError


@pytest.fixture
def validator():
    """创建验证器实例"""
    return KnowledgeValidator()


def test_validate_no_conflicts(validator):
    """验证无冲突时通过"""
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试库",
        dependencies=[
            Dependency(name="LibA", version="1.0.0", git_url="https://github.com/liba"),
            Dependency(name="LibB", version="2.0.0", git_url="https://github.com/libb"),
        ],
        excluded_dependencies=[
            ExcludedDependency(name="LibC", version="1.0.0", reason="已废弃")
        ]
    )

    # 验证应该通过，不抛出异常
    validator.validate(metadata)


def test_validate_version_conflict(validator):
    """验证检测版本冲突"""
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试库",
        dependencies=[
            Dependency(name="LibA", version="1.0.0", git_url="https://github.com/liba"),
            Dependency(name="LibA", version="2.0.0", git_url="https://github.com/liba"),
        ]
    )

    # 验证应该检测到版本冲突
    with pytest.raises(DependencyConflictError) as exc_info:
        validator.validate(metadata)

    assert "LibA" in str(exc_info.value)
    assert "1.0.0" in str(exc_info.value)
    assert "2.0.0" in str(exc_info.value)


def test_validate_excluded_dependency(validator):
    """验证排除依赖配置"""
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试库",
        dependencies=[
            Dependency(name="LibA", version="1.0.0", git_url="https://github.com/liba"),
        ],
        excluded_dependencies=[
            ExcludedDependency(name="LibB", version="1.0.0", reason="测试排除"),
            ExcludedDependency(name="LibC", version="2.0.0", reason="不兼容")
        ]
    )

    # 验证应该通过
    validator.validate(metadata)


def test_validate_no_dependencies(validator):
    """验证无依赖时通过"""
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试库",
        dependencies=[],
        excluded_dependencies=[]
    )

    # 验证应该通过
    validator.validate(metadata)


def test_validate_excluded_not_in_dependencies(validator):
    """验证排除的依赖不在依赖列表中时仍然有效（这是允许的）"""
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试库",
        dependencies=[
            Dependency(name="LibA", version="1.0.0", git_url="https://github.com/liba"),
        ],
        excluded_dependencies=[
            ExcludedDependency(name="LibB", version="1.0.0", reason="将来可能添加，但先排除")
        ]
    )

    # 验证应该通过（排除的依赖不必在依赖列表中）
    validator.validate(metadata)

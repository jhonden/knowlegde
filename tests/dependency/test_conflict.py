"""知识库依赖冲突检测器测试。"""

import pytest
from kb.core.models import Dependency
from kb.dependency.conflict import ConflictDetector
from kb.exceptions import DependencyConflictError


def test_no_conflict():
    """测试无冲突情况"""
    detector = ConflictDetector()

    # 测试空列表
    detector.check_conflicts([])

    # 测试单条依赖
    dep1 = Dependency(name="test-kb", version="1.0.0", git_url="https://github.com/test/test-kb")
    detector.check_conflicts([dep1])

    # 测试不同知识库
    dep2 = Dependency(name="kb1", version="1.0.0", git_url="https://github.com/test/kb1")
    dep3 = Dependency(name="kb2", version="2.0.0", git_url="https://github.com/test/kb2")
    detector.check_conflicts([dep2, dep3])


def test_version_conflict():
    """测试同一知识库多个版本冲突"""
    detector = ConflictDetector()

    # 创建冲突的依赖
    deps = [
        Dependency(name="conflict-kb", version="1.0.0", git_url="https://github.com/test/conflict-kb"),
        Dependency(name="conflict-kb", version="1.1.0", git_url="https://github.com/test/conflict-kb"),
        Dependency(name="conflict-kb", version="2.0.0", git_url="https://github.com/test/conflict-kb"),
    ]

    # 应该抛出异常
    with pytest.raises(DependencyConflictError) as exc_info:
        detector.check_conflicts(deps)

    # 检查错误消息
    error_message = str(exc_info.value)
    assert "检测到依赖版本冲突：" in error_message
    assert "conflict-kb" in error_message
    assert "1.0.0" in error_message
    assert "1.1.0" in error_message
    assert "2.0.0" in error_message
    assert "共发现 1 个冲突" in error_message


def test_duplicate_same_version():
    """测试相同版本重复（不应报错）"""
    detector = ConflictDetector()

    # 创建相同版本重复的依赖
    deps = [
        Dependency(name="same-version-kb", version="1.0.0", git_url="https://github.com/test/same-version-kb"),
        Dependency(name="same-version-kb", version="1.0.0", git_url="https://github.com/test/same-version-kb"),
        Dependency(name="same-version-kb", version="1.0.0", git_url="https://github.com/test/same-version-kb"),
    ]

    # 应该通过检查，不抛出异常
    detector.check_conflicts(deps)


def test_multiple_conflicts():
    """测试多个冲突"""
    detector = ConflictDetector()

    # 创建多个冲突
    deps = [
        # 第一个冲突
        Dependency(name="conflict1", version="1.0.0", git_url="https://github.com/test/conflict1"),
        Dependency(name="conflict1", version="2.0.0", git_url="https://github.com/test/conflict1"),

        # 第二个冲突
        Dependency(name="conflict2", version="1.1.0", git_url="https://github.com/test/conflict2"),
        Dependency(name="conflict2", version="1.2.0", git_url="https://github.com/test/conflict2"),
        Dependency(name="conflict2", version="1.3.0", git_url="https://github.com/test/conflict2"),

        # 无冲突的依赖
        Dependency(name="no-conflict", version="1.0.0", git_url="https://github.com/test/no-conflict"),
    ]

    # 应该抛出异常
    with pytest.raises(DependencyConflictError) as exc_info:
        detector.check_conflicts(deps)

    # 检查错误消息
    error_message = str(exc_info.value)
    assert "共发现 2 个冲突" in error_message
    assert "conflict1" in error_message
    assert "conflict2" in error_message


def test_conflict_report_format():
    """测试冲突报告格式"""
    detector = ConflictDetector()

    deps = [
        Dependency(name="format-test", version="1.0.0", git_url="https://github.com/test/format-test"),
        Dependency(name="format-test", version="1.1.0", git_url="https://github.com/test/format-test"),
    ]

    with pytest.raises(DependencyConflictError) as exc_info:
        detector.check_conflicts(deps)

    error_message = str(exc_info.value)

    # 检查报告格式
    assert "检测到依赖版本冲突：" in error_message
    assert "\n1. 知识库 'format-test'" in error_message
    assert "   - 总请求数: 2" in error_message
    assert "   - 版本列表: 1.0.0, 1.1.0" in error_message
    assert "   - 冲突版本: 1.0.0, 1.1.0" in error_message
    assert "   - 冲突原因: 同一知识库有多个不同版本" in error_message
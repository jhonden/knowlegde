"""知识库依赖解析器测试。"""

import pytest
from pathlib import Path
from kb.core.models import Dependency, KnowledgeMetadata, ExcludedDependency
from kb.dependency.resolver import DependencyResolver


class TestDependencyResolver:
    """DependencyResolver 测试类。"""

    @pytest.fixture
    def resolver(self):
        """创建测试用的依赖解析器实例。"""
        with pytest.MonkeyPatch().context() as m:
            # 临时改变工作目录
            temp_dir = Path("/tmp/test-resolver")
            temp_dir.mkdir(parents=True, exist_ok=True)
            m.chdir(temp_dir)
            return DependencyResolver(cache_dir=Path("/tmp/cache"), deps_dir=Path("/tmp/deps"))

    @pytest.fixture
    def temp_deps_dir(self, tmp_path):
        """临时依赖目录。"""
        deps_dir = tmp_path / "deps"
        deps_dir.mkdir()
        return deps_dir

    def test_resolve_dependencies_empty(self, resolver):
        """测试空依赖列表。"""
        # 创建空的元数据
        metadata = KnowledgeMetadata(
            name="test",
            version="1.0.0",
            type="test",
            description="test",
            dependencies=[],
            excluded_dependencies=[]
        )

        # 解析依赖
        result = resolver.resolve(metadata)

        # 验证结果
        assert result == []

    def test_resolve_dependencies_single(self, resolver):
        """测试单个依赖。"""
        # 创建单个依赖
        dependency = Dependency(
            name="test-dependency",
            version="1.0.0",
            git_url="https://github.com/test/repo"
        )

        metadata = KnowledgeMetadata(
            name="test",
            version="1.0.0",
            type="test",
            description="test",
            dependencies=[dependency],
            excluded_dependencies=[]
        )

        # 解析依赖
        result = resolver.resolve(metadata)

        # 验证结果
        assert len(result) == 1
        assert result[0].name == "test-dependency"
        assert result[0].version == "1.0.0"

    def test_resolve_dependencies_with_exclusions(self, resolver):
        """测试排除依赖处理。"""
        # 创建依赖列表
        dependencies = [
            Dependency(name="dep1", version="1.0.0", git_url="https://github.com/test/repo1"),
            Dependency(name="dep2", version="2.0.0", git_url="https://github.com/test/repo2"),
            Dependency(name="dep3", version="3.0.0", git_url="https://github.com/test/repo3"),
        ]

        # 创建排除依赖列表
        excluded_dependencies = [
            ExcludedDependency(name="dep1", version="1.0.0", reason="版本冲突"),
            ExcludedDependency(name="dep2", version="1.0.0", reason="版本过旧"),  # 不匹配，不会被排除
        ]

        metadata = KnowledgeMetadata(
            name="test",
            version="1.0.0",
            type="test",
            description="test",
            dependencies=dependencies,
            excluded_dependencies=excluded_dependencies
        )

        # 解析依赖
        result = resolver.resolve(metadata)

        # 验证结果（dep1应该被排除，dep2应该保留，dep3应该保留）
        assert len(result) == 2
        assert result[0].name == "dep2"  # 版本2.0.0，没有被排除
        assert result[0].version == "2.0.0"
        assert result[1].name == "dep3"  # 没有被排除
        assert result[1].version == "3.0.0"

    def test_resolve_dependencies_exclusion_different_names(self, resolver):
        """测试不同名称的排除依赖。"""
        # 创建依赖列表
        dependencies = [
            Dependency(name="dep1", version="1.0.0", git_url="https://github.com/test/repo1"),
            Dependency(name="dep2", version="2.0.0", git_url="https://github.com/test/repo2"),
        ]

        # 创建排除不同名称的依赖（应该不会影响现有依赖）
        excluded_dependencies = [
            ExcludedDependency(name="dep3", version="1.0.0", reason="不需要"),
        ]

        metadata = KnowledgeMetadata(
            name="test",
            version="1.0.0",
            type="test",
            description="test",
            dependencies=dependencies,
            excluded_dependencies=excluded_dependencies
        )

        # 解析依赖
        result = resolver.resolve(metadata)

        # 验证结果（所有依赖都应该保留）
        assert len(result) == 2
        assert result[0].name == "dep1"
        assert result[0].version == "1.0.0"
        assert result[1].name == "dep2"
        assert result[1].version == "2.0.0"

    def test_get_install_path(self, resolver, temp_deps_dir):
        """测试安装路径计算。"""
        # 更新解析器的依赖目录
        resolver.deps_dir = temp_deps_dir

        # 创建依赖
        dependency = Dependency(
            name="test-dependency",
            version="1.0.0",
            git_url="https://github.com/test/repo"
        )

        # 获取安装路径
        install_path = resolver.get_install_path(dependency)

        # 验证路径
        expected_path = temp_deps_dir / "test-dependency-1.0.0"
        assert install_path == expected_path

    def test_get_install_path_with_special_characters(self, resolver, temp_deps_dir):
        """测试包含特殊字符的依赖名称。"""
        # 更新解析器的依赖目录
        resolver.deps_dir = temp_deps_dir

        # 创建包含特殊字符的依赖
        dependency = Dependency(
            name="test@#$%_dependency",
            version="1.0.0",
            git_url="https://github.com/test/repo"
        )

        # 获取安装路径
        install_path = resolver.get_install_path(dependency)

        # 验证路径（特殊字符应该被保留）
        expected_path = temp_deps_dir / "test@#$%_dependency-1.0.0"
        assert install_path == expected_path

    def test_deps_dir_default_creation(self):
        """测试默认依赖目录的创建。"""
        # 在临时目录中创建解析器，不指定 deps_dir
        with pytest.MonkeyPatch().context() as m:
            temp_dir = Path("/tmp/default-deps")
            temp_dir.mkdir(parents=True, exist_ok=True)
            m.chdir(temp_dir)

            resolver = DependencyResolver(cache_dir=Path("/tmp/cache"))

            # 验证 deps_dir 是默认值且目录已创建
            expected_deps_dir = Path.cwd() / "deps"
            assert resolver.deps_dir == expected_deps_dir
            assert expected_deps_dir.exists()

    def test_resolve_multiple_exclusions_same_name(self, resolver):
        """测试排除同一依赖的多个版本。"""
        # 创建依赖列表
        dependencies = [
            Dependency(name="dep1", version="1.0.0", git_url="https://github.com/test/repo1"),
            Dependency(name="dep1", version="2.0.0", git_url="https://github.com/test/repo2"),  # 同名不同版本
            Dependency(name="dep2", version="1.0.0", git_url="https://github.com/test/repo3"),
        ]

        # 创建排除依赖列表
        excluded_dependencies = [
            ExcludedDependency(name="dep1", version="1.0.0", reason="版本冲突"),
        ]

        metadata = KnowledgeMetadata(
            name="test",
            version="1.0.0",
            type="test",
            description="test",
            dependencies=dependencies,
            excluded_dependencies=excluded_dependencies
        )

        # 解析依赖
        result = resolver.resolve(metadata)

        # 验证结果（dep1的1.0.0版本被排除，2.0.0版本保留，dep2保留）
        assert len(result) == 2
        assert result[0].name == "dep1"  # 版本2.0.0，没有被排除
        assert result[0].version == "2.0.0"
        assert result[1].name == "dep2"
        assert result[1].version == "1.0.0"
# Knowledge Library Dependency Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现依赖管理功能，包括依赖解析、发布包下载、解压和版本冲突检测

**Architecture:** 模块化设计，依赖解析器负责构建依赖树，下载器负责获取发布包，解压器负责解压到目标目录，冲突检测器负责识别和报告版本冲突。清晰的责任边界，便于测试和维护。

**Tech Stack:** Python 3.11+, requests 2.x, pytest

**Cross-Platform Support:**
- 使用 `pathlib.Path` 处理跨平台文件路径
- tar.gz 格式在所有平台都能正常解压
- requests 库跨平台兼容

---

## File Structure

```
kb/
├── dependency/
│   ├── __init__.py
│   ├── resolver.py       # 依赖解析器
│   ├── downloader.py     # 发布包下载器
│   ├── extractor.py       # 解压工具
│   └── conflict.py       # 版本冲突检测
```

---

## Task 1: 实现依赖下载器

**Files:**
- Modify: `requirements.txt`
- Create: `kb/dependency/__init__.py`
- Create: `kb/dependency/downloader.py`
- Test: `tests/dependency/test_downloader.py`

- [ ] **Step 1: 更新requirements.txt**

```text
pydantic>=2.0.0
click>=8.0.0
requests>=2.28.0
```

- [ ] **Step 2: 创建下载器测试（失败测试优先）**

```python
# tests/dependency/test_downloader.py
from pathlib import Path
from kb.dependency.downloader import PackageDownloader
from kb.exceptions import KnowledgeBaseError


def test_download_package_success(tmp_path):
    # 这个测试需要一个真实的git仓库，使用mock代替
    pass


def test_download_package_invalid_url():
    downloader = PackageDownloader(cache_dir=tmp_path)
    with pytest.raises(KnowledgeBaseError):
        downloader.download("TestLib", "1.0.0", "https://invalid.url/package.tar.gz")


def test_download_already_cached(tmp_path):
    # 创建缓存文件
    cache_dir = tmp_path / "TestLib"
    cache_dir.mkdir(parents=True)
    (cache_dir / "1.0.0.tar.gz").write_bytes(b"test")

    downloader = PackageDownloader(cache_dir=tmp_path)
    # 不应该重复下载
    pass
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/dependency/test_downloader.py -v
```
Expected: FAIL with "PackageDownloader not defined"

- [ ] **Step 4: 实现下载器**

```python
# kb/dependency/downloader.py
from __future__ import annotations
from pathlib import Path
from urllib.parse import urljoin
import requests
from kb.exceptions import KnowledgeBaseError


class PackageDownloader:
    """知识库发布包下载器"""

    def __init__(self, cache_dir: Path | None = None):
        """
        初始化下载器

        Args:
            cache_dir: 缓存目录，默认为 ~/.kb-cache
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".kb-cache"
        self.cache_dir = Path(cache_dir)

    def download(
        self, name: str, version: str, git_url: str, force: bool = False
    ) -> Path:
        """
        下载知识库发布包

        Args:
            name: 知识库名称
            version: 版本号
            git_url: git仓库地址
            force: 强制重新下载，忽略缓存

        Returns:
            缓存中的发布包路径

        Raises:
            KnowledgeBaseError: 下载失败
        """
        # 构建缓存路径
        lib_cache_dir = self.cache_dir / name
        lib_cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = lib_cache_dir / f"{version}.tar.gz"

        # 检查缓存
        if cache_file.exists() and not force:
            return cache_file

        # 构建下载URL
        # git仓库地址格式: https://github.com/user/repo
        # 发布包URL: https://github.com/user/repo/raw/refs/heads/main/publish/{name}-{version}.tar.gz
        # 或者用户可以提供完整的发布包URL
        download_url = self._build_download_url(git_url, name, version)

        # 下载文件
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            # 写入缓存
            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return cache_file

        except requests.RequestException as e:
            raise KnowledgeBaseError(f"下载失败: {e}") from e

    def _build_download_url(self, git_url: str, name: str, version: str) -> str:
        """
        构建发布包下载URL

        Args:
            git_url: git仓库地址
            name: 知识库名称
            version: 版本号

        Returns:
            发布包URL
        """
        # 如果git_url已经是一个完整的URL（可能已经包含发布包路径），直接使用
        if git_url.endswith(".tar.gz"):
            return git_url

        # 否则，尝试从git仓库地址构建发布包URL
        # GitHub: https://github.com/user/repo -> https://github.com/user/repo/raw/refs/heads/main/publish/{name}-{version}.tar.gz
        # GitLab: https://gitlab.com/user/repo -> https://gitlab.com/user/repo/-/raw/main/publish/{name}-{version}.tar.gz

        if "github.com" in git_url:
            return f"{git_url}/raw/refs/heads/main/publish/{name}-{version}.tar.gz"
        elif "gitlab.com" in git_url:
            return f"{git_url}/-/raw/main/publish/{name}-{version}.tar.gz"
        else:
            # 默认假设GitHub格式
            return f"{git_url}/raw/refs/heads/main/publish/{name}-{version}.tar.gz"
```

- [ ] **Step 5: 更新测试并运行**

```python
# tests/dependency/test_downloader.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from kb.dependency.downloader import PackageDownloader
from kb.exceptions import KnowledgeBaseError


def test_download_package_invalid_url(tmp_path):
    downloader = PackageDownloader(cache_dir=tmp_path)
    with pytest.raises(KnowledgeBaseError):
        downloader.download("TestLib", "1.0.0", "https://invalid.url/package.tar.gz")


def test_build_download_url_github(tmp_path):
    downloader = PackageDownloader(cache_dir=tmp_path)
    url = downloader._build_download_url(
        "https://github.com/test/repo",
        "TestLib",
        "1.0.0"
    )
    assert url == "https://github.com/test/repo/raw/refs/heads/main/publish/TestLib-1.0.0.tar.gz"


def test_build_download_url_gitlab(tmp_path):
    downloader = PackageDownloader(cache_dir=tmp_path)
    url = downloader._build_download_url(
        "https://gitlab.com/test/repo",
        "TestLib",
        "1.0.0"
    )
    assert url == "https://gitlab.com/test/repo/-/raw/main/publish/TestLib-1.0.0.tar.gz"


@patch("requests.get")
def test_download_package_success(mock_get, tmp_path):
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"test content"]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    downloader = PackageDownloader(cache_dir=tmp_path)
    cache_file = downloader.download(
        "TestLib",
        "1.0.0",
        "https://github.com/test/repo"
    )

    assert cache_file.exists()
    assert cache_file.name == "1.0.0.tar.gz"
    assert cache_file.read_bytes() == b"test content"
```

```bash
pytest tests/dependency/test_downloader.py -v
```
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add requirements.txt kb/dependency/ tests/dependency/test_downloader.py
git commit -m "feat(dependency): 实现发布包下载器"
```

---

## Task 2: 实现解压工具

**Files:**
- Create: `kb/dependency/extractor.py`
- Test: `tests/dependency/test_extractor.py`

- [ ] **Step 1: 创建解压器测试（失败测试优先）**

```python
# tests/dependency/test_extractor.py
import tarfile
from pathlib import Path
from kb.dependency.extractor import PackageExtractor
from kb.exceptions import KnowledgeBaseError


def test_extract_package(tmp_path):
    # 创建一个测试的tar.gz包
    pkg_path = tmp_path / "test-1.0.0.tar.gz"
    with tarfile.open(pkg_path, "w:gz") as tar:
        # 创建虚拟文件
        import io
        content = b"test content"
        info = tarfile.TarInfo(name="test.txt")
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))

    # 解压
    extractor = PackageExtractor()
    target_dir = tmp_path / "extracted"
    extractor.extract(pkg_path, target_dir)

    assert (target_dir / "test.txt").exists()
    assert (target_dir / "test.txt").read_bytes() == b"test content"


def test_extract_nonexistent_package(tmp_path):
    extractor = PackageExtractor()
    with pytest.raises(KnowledgeBaseError):
        extractor.extract(tmp_path / "nonexistent.tar.gz", tmp_path / "target")
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/dependency/test_extractor.py -v
```
Expected: FAIL with "PackageExtractor not defined"

- [ ] **Step 3: 实现解压器**

```python
# kb/dependency/extractor.py
from __future__ import annotations
from pathlib import Path
import tarfile
import gzip
from kb.exceptions import KnowledgeBaseError


class PackageExtractor:
    """知识库发布包解压器"""

    def extract(self, package_path: Path, target_dir: Path) -> None:
        """
        解压发布包到目标目录

        Args:
            package_path: 发布包路径
            target_dir: 目标目录

        Raises:
            KnowledgeBaseError: 解压失败
        """
        if not package_path.exists():
            raise KnowledgeBaseError(f"发布包不存在: {package_path}")

        # 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            if package_path.suffix == ".gz":
                with tarfile.open(package_path, "r:gz") as tar:
                    tar.extractall(target_dir)
            else:
                raise KnowledgeBaseError(f"不支持的发布包格式: {package_path.suffix}")

        except (tarfile.TarError, gzip.BadGzipFile) as e:
            raise KnowledgeBaseError(f"解压失败: {e}") from e
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/dependency/test_extractor.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add kb/dependency/extractor.py tests/dependency/test_extractor.py
git commit -m "feat(dependency): 实现发布包解压器"
```

---

## Task 3: 实现版本冲突检测器

**Files:**
- Create: `kb/dependency/conflict.py`
- Test: `tests/dependency/test_conflict.py`

- [ ] **Step 1: 创建冲突检测器测试（失败测试优先）**

```python
# tests/dependency/test_conflict.py
from kb.dependency.conflict import ConflictDetector
from kb.core.models import Dependency
from kb.exceptions import DependencyConflictError


def test_no_conflict():
    detector = ConflictDetector()
    deps = [
        Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1"),
        Dependency(name="Dep2", version="1.0.0", git_url="https://github.com/test/dep2"),
    ]
    # 不应该抛出异常
    detector.check_conflicts(deps)


def test_version_conflict():
    detector = ConflictDetector()
    deps = [
        Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1"),
        Dependency(name="Dep1", version="1.3.0", git_url="https://github.com/test/dep1"),
    ]
    with pytest.raises(DependencyConflictError):
        detector.check_conflicts(deps)


def test_duplicate_same_version():
    detector = ConflictDetector()
    deps = [
        Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1"),
        Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1"),
    ]
    # 相同版本不应报冲突
    detector.check_conflicts(deps)
```

- [ ] **Step 2: 近行测试验证失败**

```bash
pytest tests/dependency/test_conflict.py -v
```
Expected: FAIL with "ConflictDetector not defined"

- [ ] **Step 3: 实现冲突检测器**

```python
# kb/dependency/conflict.py
from __future__ import annotations
from collections import defaultdict
from kb.core.models import Dependency
from kb.exceptions import DependencyConflictError


class ConflictDetector:
    """版本冲突检测器"""

    def __init__(self):
        pass

    def check_conflicts(self, dependencies: list[Dependency]) -> None:
        """
        检查依赖列表中的版本冲突

        Args:
            dependencies: 依赖列表

        Raises:
            DependencyConflictError: 检测到版本冲突
        """
        # 按名称分组
        deps_by_name: dict[str, list[Dependency]] = defaultdict(list)
        for dep in dependencies:
            deps_by_name[dep.name].append(dep)

        # 检查每个名称是否有多个版本
        conflicts = []
        for name, deps in deps_by_name.items():
            versions = set(dep.version for dep in deps)
            if len(versions) > 1:
                conflicts.append({
                    "name": name,
                    "versions": sorted(versions),
                    "count": len(deps),
                })

        if conflicts:
            # 构建错误消息
            error_lines = ["检测到依赖版本冲突:"]
            for conflict in conflicts:
                versions_str = ", ".join(conflict["versions"])
                error_lines.append(
                    f"  - {conflict['name']}: {versions_str} (出现{conflict['count']}次)"
                )
            raise DependencyConflictError("\n".join(error_lines))
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/dependency/test_conflict.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add kb/dependency/conflict.py tests/dependency/test_conflict.py
git commit -m "feat(dependency): 实现版本冲突检测器"
```

---

## Task 4: 实现依赖解析器

**Files:**
- Create: `kb/dependency/resolver.py`
- Test: `tests/dependency/test_resolver.py`

- [ ] **Step 1: 创建解析器测试（失败测试优先）**

```python
# tests/dependency/test_resolver.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from kb.dependency.resolver import DependencyResolver
from kb.core.models import KnowledgeMetadata, Dependency


def test_resolve_dependencies_empty():
    resolver = DependencyResolver()
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试"
    )
    deps = resolver.resolve(metadata)
    assert len(deps) == 0


def test_resolve_dependencies_single():
    resolver = DependencyResolver()
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试",
        dependencies=[
            Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1")
        ]
    )
    deps = resolver.resolve(metadata)
    assert len(deps) == 1
    assert deps[0].name == "Dep1"
    assert deps[0].version == "1.2.0"


def test_resolve_dependencies_with_exclusions():
    # 测试排除依赖的处理
    resolver = DependencyResolver()
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试",
        dependencies=[
            Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1")
        ],
        excluded_dependencies=[
            ExcludedDependency(name="Dep1", version="1.0.0", reason="测试")
        ]
    )
    # 排除的依赖版本不应该被解析（但这个版本本来就不在依赖列表中）
    deps = resolver.resolve(metadata)
    assert len(deps) == 1
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/dependency/test_resolver.py -v
```
Expected: FAIL with "DependencyResolver not defined"

- [ ] **Step 3: 实现解析器**

```python
# kb/dependency/resolver.py
from __future__ import annotations
from pathlib import Path
from kb.core.models import KnowledgeMetadata, Dependency, ExcludedDependency


class DependencyResolver:
    """依赖解析器"""

    def __init__(
        self,
        cache_dir: Path | None = None,
        deps_dir: Path | None = None,
    ):
        """
        初始化依赖解析器

        Args:
            cache_dir: 缓存目录
            deps_dir: 依赖解压目录
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".kb-cache"
        self.cache_dir = Path(cache_dir)

        if deps_dir is None:
            deps_dir = Path.cwd() / "deps"
        self.deps_dir = Path(deps_dir)

    def resolve(self, metadata: KnowledgeMetadata) -> list[Dependency]:
        """
        解析知识库的依赖列表

        Args:
            metadata: 知识库元数据

        Returns:
            依赖列表

        Note:
            当前版本只返回直接依赖，递归解析在后续版本实现
        """
        # 获取排除的依赖版本
        excluded_versions: dict[str, set[str]] = {}
        for excluded in metadata.excluded_dependencies:
            if excluded.name not in excluded_versions:
                excluded_versions[excluded.name] = set()
            excluded_versions[excluded.name].add(excluded.version)

        # 过滤掉被排除的依赖
        dependencies = []
        for dep in metadata.dependencies:
            # 检查是否被排除
            excluded_vers = excluded_versions.get(dep.name, set())
            if dep.version in excluded_vers:
                continue

            dependencies.append(dep)

        return dependencies

    def get_install_path(self, dependency: Dependency) -> Path:
        """
        获取依赖的安装路径

        Args:
            dependency: 依赖项

        Returns:
            安装路径
        """
        return self.deps_dir / f"{dependency.name}-{dependency.version}"
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/dependency/test_resolver.py -v
```
Expected: PASS

- [ ] **Step 5: 添加排除依赖测试**

```python
# tests/dependency/test_resolver.py
# 在文件末尾添加
from kb.core.models import ExcludedDependency


def test_resolve_dependencies_with_exclusions_filter():
    resolver = DependencyResolver()
    # 创建一个依赖，然后排除它
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试",
        dependencies=[
            Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1")
        ],
        excluded_dependencies=[
            ExcludedDependency(name="Dep1", version="1.2.0", reason="版本冲突")
        ]
    )
    deps = resolver.resolve(metadata)
    assert len(deps) == 0  # 应该被排除


def test_get_install_path(tmp_path):
    resolver = DependencyResolver(deps_dir=tmp_path)
    dep = Dependency(name="TestLib", version="1.0.0", git_url="https://github.com/test/repo")
    path = resolver.get_install_path(dep)
    assert path == tmp_path / "TestLib-1.0.0"
```

```bash
pytest tests/dependency/test_resolver.py -v
```
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add kb/dependency/resolver.py tests/dependency/test_resolver.py
git commit -m "feat(dependency): 实现依赖解析器"
```

---

## Task 5: 更新kb init命令集成依赖管理

**Files:**
- Modify: `kb/cli/init.py`
- Test: `tests/cli/test_init_integration.py`

- [ ] **Step 1: 修改kb init命令**

```python
# kb/cli/init.py
from pathlib import Path
import click
from kb.cli.main import cli
from kb.cli.utils import find_knowledge_file
from kb.core import KnowledgeParser
from kb.dependency import (
    DependencyResolver,
    PackageDownloader,
    PackageExtractor,
    ConflictDetector,
)
from kb.exceptions import DependencyConflictError, KnowledgeBaseError


@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=False),
    default=None,
    help="知识库文件路径"
)
def init(path: str | None):
    """初始化知识库，下载所有依赖"""
    if path:
        knowledge_file = Path(path)
    else:
        knowledge_file = find_knowledge_file()

    if not knowledge_file or not knowledge_file.exists():
        click.echo("未找到知识库文件")
        click.echo("请确保在知识库目录下运行此命令，或使用 --path 指定路径")
        return

    click.echo(f"正在初始化知识库...")

    try:
        # 解析Knowledge.md
        parser = KnowledgeParser()
        metadata = parser.parse(knowledge_file)

        click.echo(f"知识库: {metadata.name} v{metadata.version}")

        # 解析依赖
        resolver = DependencyResolver()
        dependencies = resolver.resolve(metadata)

        if not dependencies:
            click.echo("无依赖需要下载")
            return

        click.echo(f"发现 {len(dependencies)} 个依赖")

        # 检查版本冲突
        conflict_detector = ConflictDetector()
        conflict_detector.check_conflicts(dependencies)

        # 初始化下载器和解压器
        downloader = PackageDownloader()
        extractor = PackageExtractor()

        # 下载并解压依赖
        for dep in dependencies:
            click.echo(f"  正在下载: {dep.name} v{dep.version}")

            # 下载
            cache_file = downloader.download(dep.name, dep.version, dep.git_url)

            # 获取安装路径
            install_path = resolver.get_install_path(dep)

            # 解压
            click.echo(f"  正在解压到: {install_path}")
            extractor.extract(cache_file, install_path)

        click.echo("初始化完成")

    except DependencyConflictError as e:
        click.echo(f"错误: {e}")
        return 1
    except KnowledgeBaseError as e:
        click.echo(f"错误: {e}")
        return 1
    except Exception as e:
        click.echo(f"未知错误: {e}")
        return 1
```

- [ ] **Step 2: 创建集成测试**

```python
# tests/cli/test_init_integration.py
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from kb.cli.main import cli


@patch("kb.dependency.downloader.PackageDownloader.download")
@patch("kb.dependency.extractor.PackageExtractor.extract")
def test_init_with_dependencies(mock_extract, mock_download, tmp_path):
    runner = CliRunner()

    # Mock下载返回一个虚拟文件
    mock_cache_file = tmp_path / "cache" / "Dep1" / "1.0.0.tar.gz"
    mock_cache_file.parent.mkdir(parents=True)
    mock_cache_file.write_bytes(b"test")
    mock_download.return_value = mock_cache_file

    with runner.isolated_filesystem():
        # 创建有效的Knowledge.md，带依赖
        Path("src").mkdir()
        Path("src/Knowledge.md").write_text("""# TestLib

## 基本信息

- **名称**: TestLib
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| Dep1 | 1.0.0 | https://github.com/test/dep1 |
""")

        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "TestLib" in result.output
        assert "Dep1" in result.output
        assert "初始化完成" in result.output


@patch("kb.dependency.downloader.PackageDownloader.download")
def test_init_with_version_conflict(mock_download, tmp_path):
    runner = CliRunner()

    mock_cache_file = tmp_path / "cache" / "Dep1" / "1.0.0.tar.gz"
    mock_cache_file.parent.mkdir(parents=True)
    mock_cache_file.write_bytes(b"test")
    mock_download.return_value = mock_cache_file

    with runner.isolated_filesystem():
        # 创建有版本冲突的Knowledge.md
        Path("src").mkdir()
        Path("src/Knowledge.md").write_text("""# TestLib

## 基本信息

- **名称**: TestLib
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| Dep1 | 1.0.0 | https://github.com/test/dep1 |
| Dep1 | 1.2.0 | https://github.com/test/dep1 |
""")

        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 1
        assert "检测到依赖版本冲突" in result.output
```

- [ ] **Step 3: 运行集成测试**

```bash
pytest tests/cli/test_init_integration.py -v
```
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add kb/cli/init.py tests/cli/test_init_integration.py
git commit -m "feat(cli): 集成依赖管理到kb init命令"
```

---

## Task 6: 最终测试和文档更新

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新README.md**

```markdown
# Knowledge Base CLI Tool

知识库命令行工具，支持知识库的创建、打包、依赖管理和发布。

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 创建知识库

```bash
kb init
```

### 打包知识库

```bash
kb package
```

## 命令列表

| 命令 | 说明 |
|-----|------|
| `kb init` | 初始化知识库，下载所有依赖 |
| `kb package` | 打包当前知识库并生成发布包 |

## 依赖管理

知识库通过 `Knowledge.md` 中的依赖表声明依赖：

```markdown
## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.2.0 | https://github.com/example/common-data-types |
```

运行 `kb init` 时会自动下载依赖到 `deps/` 目录。

### 版本冲突

如果检测到版本冲突，`kb init` 会报错并提示冲突详情。你可以通过排除依赖表解决冲突：

```markdown
## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| OldParser | 1.0.0 | 与其他依赖冲突 |
```

## 开发

```bash
pytest tests/ -v
```
```

- [ ] **Step 2: 运行所有测试**

```bash
pytest tests/ -v --cov=kb --cov-report=html
```
Expected: PASS with coverage report

- [ ] **Step 3: 提交**

```bash
git add README.md
git commit -m "docs: 更新README添加依赖管理说明"
```

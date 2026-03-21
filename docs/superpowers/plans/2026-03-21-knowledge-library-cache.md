# Knowledge Library Cache Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现缓存管理功能，包括列出缓存、清理缓存

**Architecture:** 缓存管理器负责缓存目录的管理操作，CLI命令提供用户友好的交互界面。清晰的API设计，便于测试和复用。

**Tech Stack:** Python 3.11+, Click 8.x, pytest

**Cross-Platform Support:**
- `Path.home()` 在所有平台返回正确的用户主目录路径
- 文件操作使用 `pathlib.Path`，自动处理路径分隔符
- Click 命令行界面跨平台兼容

---

## File Structure

```
kb/
├── cache/
│   ├── __init__.py
│   └── manager.py         # 缓存管理器
kb/cli/
├── cache.py               # kb cache命令
```

---

## Task 1: 实现缓存管理器

**Files:**
- Create: `kb/cache/__init__.py`
- Create: `kb/cache/manager.py`
- Test: `tests/cache/test_manager.py`

- [ ] **Step 1: 创建缓存管理器测试（失败测试优先）**

```python
# tests/cache/test_manager.py
from pathlib import Path
from kb.cache.manager import CacheManager


def test_get_cache_info(tmp_path):
    # 创建缓存目录
    lib1_dir = tmp_path / "Lib1"
    lib1_dir.mkdir(parents=True)
    (lib1_dir / "1.0.0.tar.gz").write_bytes(b"test1")
    (lib1_dir / "1.2.0.tar.gz").write_bytes(b"test2")

    lib2_dir = tmp_path / "Lib2"
    lib2_dir.mkdir(parents=True)
    (lib2_dir / "2.0.0.tar.gz").write_bytes(b"test3")

    manager = CacheManager(cache_dir=tmp_path)
    info = manager.get_info()

    assert len(info["libraries"]) == 2
    assert info["total_size"] > 0


def test_list_cache(tmp_path):
    lib1_dir = tmp_path / "Lib1"
    lib1_dir.mkdir(parents=True)
    (lib1_dir / "1.0.0.tar.gz").write_bytes(b"test1")
    (lib1_dir / "1.2.0.tar.gz").write_bytes(b"test2")

    manager = CacheManager(cache_dir=tmp_path)
    libs = manager.list()

    assert len(libs) == 1
    assert libs[0]["name"] == "Lib1"
    assert len(libs[0]["versions"]) == 2


def test_clean_all(tmp_path):
    lib1_dir = tmp_path / "Lib1"
    lib1_dir.mkdir(parents=True)
    (lib1_dir / "1.0.0.tar.gz").write_bytes(b"test1")

    manager = CacheManager(cache_dir=tmp_path)
    manager.clean_all()

    assert not lib1_dir.exists()


def test_clean_library(tmp_path):
    lib1_dir = tmp_path / "Lib1"
    lib1_dir.mkdir(parents=True)
    (lib1_dir / "1.0.0.tar.gz").write_bytes(b"test1")

    lib2_dir = tmp_path / "Lib2"
    lib2_dir.mkdir(parents=True)
    (lib2_dir / "2.0.0.tar.gz").write_bytes(b"test2")

    manager = CacheManager(cache_dir=tmp_path)
    manager.clean_library("Lib1")

    assert not lib1_dir.exists()
    assert lib2_dir.exists()


def test_clean_version(tmp_path):
    lib1_dir = tmp_path / "Lib1"
    lib1_dir.mkdir(parents=True)
    (lib1_dir / "1.0.0.tar.gz").write_bytes(b"test1")
    (lib1_dir / "1.2.0.tar.gz").write_bytes(b"test2")

    manager = CacheManager(cache_dir=tmp_path)
    manager.clean_version("Lib1", "1.0.0")

    assert not (lib1_dir / "1.0.0.tar.gz").exists()
    assert (lib1_dir / "1.2.0.tar.gz").exists()


def test_clean_nonexistent_library(tmp_path):
    manager = CacheManager(cache_dir=tmp_path)
    # 不应该抛出异常
    manager.clean_library("NonExistent")


def test_clean_nonexistent_version(tmp_path):
    manager = CacheManager(cache_dir=tmp_path)
    # 不应该抛出异常
    manager.clean_version("Lib1", "1.0.0")
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/cache/test_manager.py -v
```
Expected: FAIL with "CacheManager not defined"

- [ ] **Step 3: 实现缓存管理器**

```python
# kb/cache/manager.py
from __future__ import annotations
from pathlib import Path
from typing import TypedDict


class LibraryInfo(TypedDict):
    """知识库信息"""
    name: str
    versions: list[str]
    total_size: int


class CacheInfo(TypedDict):
    """缓存信息"""
    libraries: list[LibraryInfo]
    total_size: int
    cache_dir: str


class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: Path | None = None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录，默认为 ~/.kb-cache
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".kb-cache"
        self.cache_dir = Path(cache_dir)

    def get_info(self) -> CacheInfo:
        """
        获取缓存信息

        Returns:
            缓存信息
        """
        libraries = self.list()
        total_size = sum(lib["total_size"] for lib in libraries)

        return {
            "libraries": libraries,
            "total_size": total_size,
            "cache_dir": str(self.cache_dir),
        }

    def list(self) -> list[LibraryInfo]:
        """
        列出所有缓存的库

        Returns:
            知识库信息列表
        """
        libraries = []

        if not self.cache_dir.exists():
            return libraries

        for lib_dir in sorted(self.cache_dir.iterdir()):
            if not lib_dir.is_dir():
                continue

            versions = []
            total_size = 0

            for package_file in sorted(lib_dir.iterdir()):
                if package_file.is_file() and package_file.suffix == ".gz":
                    version = package_file.stem
                    size = package_file.stat().st_size
                    versions.append(version)
                    total_size += size

            if versions:
                libraries.append({
                    "name": lib_dir.name,
                    "versions": versions,
                    "total_size": total_size,
                })

        return libraries

    def clean_all(self) -> None:
        """清理所有缓存"""
        if not self.cache_dir.exists():
            return

        for lib_dir in self.cache_dir.iterdir():
            if lib_dir.is_dir():
                self._remove_directory(lib_dir)

    def clean_library(self, library_name: str) -> None:
        """
        清理指定知识库的所有版本

        Args:
            library_name: 知识库名称
        """
        lib_dir = self.cache_dir / library_name
        if lib_dir.exists() and lib_dir.is_dir():
            self._remove_directory(lib_dir)

    def clean_version(self, library_name: str, version: str) -> None:
        """
        清理指定知识库的指定版本

        Args:
            library_name: 知识库名称
            version: 版本号
        """
        package_file = self.cache_dir / library_name / f"{version}.tar.gz"
        if package_file.exists():
            package_file.unlink()

        # 如果目录为空，删除目录
        lib_dir = package_file.parent
        if lib_dir.exists() and not any(lib_dir.iterdir()):
            lib_dir.rmdir()

    def _remove_directory(self, dir_path: Path) -> None:
        """
        删除目录及其内容

        Args:
            dir_path: 目录路径
        """
        import shutil
        shutil.rmtree(dir_path)
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/cache/test_manager.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add kb/cache/ tests/cache/test_manager.py
git commit -m "feat(cache): 实现缓存管理器"
```

---

## Task 2: 实现kb cache命令

**Files:**
- Create: `kb/cli/cache.py`
- Test: `tests/cli/test_cache.py`

- [ ] **Step 1: 创建cache命令测试（失败测试优先）**

```python
# tests/cli/test_cache.py
from click.testing import CliRunner
from kb.cli.main import cli


def test_cache_list():
    runner = CliRunner()
    result = runner.invoke(cli, ["cache", "list"])
    assert result.exit_code == 0


def test_cache_info():
    runner = CliRunner()
    result = runner.invoke(cli, ["cache", "info"])
    assert result.exit_code == 0


def test_cache_clean_all():
    runner = CliRunner()
    result = runner.invoke(cli, ["cache", "clean"])
    assert result.exit_code == 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/cli/test_cache.py -v
```
Expected: FAIL with "cache command not registered"

- [ ] **Step 3: 实现cache命令**

```python
# kb/cli/cache.py
from pathlib import Path
import click
from kb.cli.main import cli
from kb.cache.manager import CacheManager


@cli.group()
def cache():
    """缓存管理命令"""
    pass


@cache.command()
def info():
    """显示缓存信息"""
    manager = CacheManager()
    cache_info = manager.get_info()

    click.echo(f"缓存目录: {cache_info['cache_dir']}")
    click.echo(f"知识库数量: {len(cache_info['libraries'])}")
    click.echo(f"总大小: {_format_size(cache_info['total_size'])}")

    if cache_info['libraries']:
        click.echo("\n知识库列表:")
        for lib in cache_info['libraries']:
            versions_str = ", ".join(lib['versions'])
            click.echo(f"  {lib['name']}: {versions_str} ({_format_size(lib['total_size'])})")
    else:
        click.echo("\n缓存为空")


@cache.command()
def list():
    """列出所有缓存的知识库"""
    manager = CacheManager()
    libraries = manager.list()

    if not libraries:
        click.echo("缓存为空")
        return

    click.echo(f"共 {len(libraries)} 个知识库:")
    for lib in libraries:
        versions_str = ", ".join(lib['versions'])
        click.echo(f"  {lib['name']}: {versions_str}")


@cache.command()
@click.argument("name_version", required=False)
def clean(name_version: str | None):
    """清理缓存

    如果指定 <name> 或 <name:version>，清理指定知识库或版本
    否则清理所有缓存
    """
    manager = CacheManager()

    if not name_version:
        # 清理所有缓存
        libraries = manager.list()
        if not libraries:
            click.echo("缓存为空")
            return

        click.echo(f"将清理 {len(libraries)} 个知识库:")
        for lib in libraries:
            versions_str = ", ".join(lib['versions'])
            click.echo(f"  {lib['name']}: {versions_str}")

        if click.confirm("确认清理所有缓存？"):
            manager.clean_all()
            click.echo("缓存已清理")
        return

    # 解析参数
    if ":" in name_version:
        name, version = name_version.split(":", 1)
        manager.clean_version(name, version)
        click.echo(f"已清理: {name} {version}")
    else:
        name = name_version
        manager.clean_library(name)
        click.echo(f"已清理: {name}")


def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/cli/test_cache.py -v
```
Expected: PASS

- [ ] **Step 5: 手动测试**

```bash
python -m kb.cli.main cache --help
python -m kb.cli.main cache info
python -m kb.cli.main cache list
```
Expected: 显示帮助信息和缓存状态

- [ ] **Step 6: 提交**

```bash
git add kb/cli/cache.py tests/cli/test_cache.py
git commit -m "feat(cli): 实现kb cache命令"
```

---

## Task 3: 更新CLI主模块

**Files:**
- Modify: `kb/cli/main.py`

- [ ] **Step 1: 更新main.py**

```python
# kb/cli/main.py
import click

from kb.cli import cache  # noqa: F401


@click.group()
@click.version_option(version="0.1.0", prog_name="kb")
def cli():
    """Knowledge Base CLI Tool - 知识库命令行工具"""
    pass


if __name__ == "__main__":
    cli()
```

- [ ] **Step 2: 运行测试**

```bash
pytest tests/cli/ -v
```
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add kb/cli/main.py
git commit -m "refactor(cli): 注册cache命令组"
```

---

## Task 4: 最终测试和文档更新

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

### 初始化知识库

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
| `kb cache info` | 显示缓存信息 |
| `kb cache list` | 列出所有缓存的知识库 |
| `kb cache clean` | 清理所有缓存 |
| `kb cache clean <name>` | 清理指定知识库的所有版本 |
| `kb cache clean <name:version>` | 清理指定知识库的指定版本 |

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

## 缓存管理

知识库发布包会被缓存到 `~/.kb-cache/` 目录，避免重复下载。

### 查看缓存

```bash
kb cache info    # 显示缓存信息
kb cache list    # 列出所有缓存
```

### 清理缓存

```bash
kb cache clean              # 清理所有缓存
kb cache clean Lib1         # 清理指定知识库
kb cache clean Lib1:1.0.0   # 清理指定版本
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
git commit -m "docs: 更新README添加缓存管理说明"
```

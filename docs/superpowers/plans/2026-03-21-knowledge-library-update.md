# Knowledge Library Dependency Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现依赖更新功能，包括检查更新和更新依赖

**Architecture:** 版本检查器负责从git仓库获取可用版本，版本更新器负责下载新版本、更新Knowledge.md。清晰的错误处理和用户提示。

**Tech Stack:** Python 3.11+, requests 2.x, pytest

**Cross-Platform Support:**
- 使用 `pathlib.Path` 处理跨平台文件路径
- 文件写入时显式指定 `newline='\n'` 确保一致性
- 正则表达式匹配 HTML 时考虑不同平台的换行符

---

## File Structure

```
kb/
├── update/
│   ├── __init__.py
│   ├── checker.py        # 版本检查器
│   └── updater.py        # 版本更新器
kb/cli/
├── update.py             # kb update命令
```

---

## Task 1: 实现版本检查器

**Files:**
- Create: `kb/update/__init__.py`
- Create: `kb/update/checker.py`
- Test: `tests/update/test_checker.py`

- [ ] **Step 1: 创建版本检查器测试（失败测试优先）**

```python
# tests/update/test_checker.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from kb.update.checker import VersionChecker, VersionUpdate
from kb.core.models import Dependency


@patch("requests.get")
def test_check_updates_no_updates(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "test/repo", "default_branch": "main"}
    mock_get.return_value = mock_response

    checker = VersionChecker()
    deps = [
        Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/repo")
    ]

    # Mock没有新的发布包
    updates = checker.check_updates(deps)
    assert len(updates) == 0


@patch("requests.get")
def test_check_updates_has_updates(mock_get):
    # Mock GitHub API返回
    mock_api_response = MagicMock()
    mock_api_response.json.return_value = {"default_branch": "main"}

    # Mock发布包列表
    mock_list_response = MagicMock()
    mock_list_response.text = """
    <a href="/test/repo/publish/Dep1-1.3.0.tar.gz">Dep1-1.3.0.tar.gz</a>
    <a href="/test/repo/publish/Dep1-1.0.0.tar.gz">Dep1-1.0.0.tar.gz</a>
    """

    mock_get.side_effect = [mock_api_response, mock_list_response]

    checker = VersionChecker()
    deps = [
        Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/repo")
    ]

    updates = checker.check_updates(deps)
    assert len(updates) == 1
    assert updates[0].name == "Dep1"
    assert updates[0].current_version == "1.2.0"
    assert updates[0].new_version == "1.3.0"


@patch("requests.get")
def test_check_single_dependency(mock_get, tmp_path):
    # 创建测试Knowledge.md
    kb_file = tmp_path / "Knowledge.md"
    kb_file.write_text("""# Test

## 基本信息

- **名称**: Test
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| Dep1 | 1.2.0 | https://github.com/test/repo |
""")

    mock_api_response = MagicMock()
    mock_api_response.json.return_value = {"default_branch": "main"}

    mock_list_response = MagicMock()
    mock_list_response.text = """
    <a href="/test/repo/publish/Dep1-1.3.0.tar.gz">Dep1-1.3.0.tar.gz</a>
    """

    mock_get.side_effect = [mock_api_response, mock_list_response]

    checker = VersionChecker()
    updates = checker.check_single_dependency(kb_file, "Dep1")

    assert len(updates) == 1
    assert updates[0].name == "Dep1"
    assert updates[0].new_version == "1.3.0"
```

- [ ] **Step 2: 定义VersionUpdate数据结构**

```python
# kb/update/__init__.py
from __future__ import annotations
from typing import TypedDict


class VersionUpdate(TypedDict):
    """版本更新信息"""
    name: str
    current_version: str
    new_version: str
    git_url: str


__all__ = ["VersionUpdate"]
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/update/test_checker.py -v
```
Expected: FAIL with "VersionChecker not defined"

- [ ] **Step 4: 实现版本检查器**

```python
# kb/update/checker.py
from __future__ import annotations
from pathlib import Path
import re
import requests
from typing import TypeAlias
from kb.core import KnowledgeParser, Dependency
from kb.update import VersionUpdate


VersionUpdateList: TypeAlias = list[VersionUpdate]


class VersionChecker:
    """版本检查器"""

    def __init__(self):
        self.parser = KnowledgeParser()

    def check_updates(
        self, dependencies: list[Dependency]
    ) -> VersionUpdateList:
        """
        检查所有依赖是否有新版本

        Args:
            dependencies: 依赖列表

        Returns:
            可更新的依赖列表
        """
        updates = []

        for dep in dependencies:
            available_versions = self._fetch_available_versions(dep)
            if available_versions:
                latest_version = self._find_latest_version(available_versions)
                if self._is_newer(latest_version, dep.version):
                    updates.append({
                        "name": dep.name,
                        "current_version": dep.version,
                        "new_version": latest_version,
                        "git_url": dep.git_url,
                    })

        return updates

    def check_single_dependency(
        self, knowledge_file: Path, dependency_name: str
    ) -> VersionUpdateList:
        """
        检查指定依赖是否有新版本

        Args:
            knowledge_file: Knowledge.md文件路径
            dependency_name: 依赖名称

        Returns:
            可更新的依赖列表
        """
        metadata = self.parser.parse(knowledge_file)

        for dep in metadata.dependencies:
            if dep.name == dependency_name:
                return self.check_updates([dep])

        return []

    def _fetch_available_versions(self, dependency: Dependency) -> list[str]:
        """
        获取依赖的可用版本列表

        Args:
            dependency: 依赖项

        Returns:
            版本列表
        """
        try:
            # 构建publish目录的HTML页面URL
            # GitHub: https://github.com/user/repo/tree/main/publish
            # GitLab: https://gitlab.com/user/repo/-/tree/main/publish

            if "github.com" in dependency.git_url:
                publish_url = self._build_github_publish_url(dependency.git_url)
            elif "gitlab.com" in dependency.git_url:
                publish_url = self._build_gitlab_publish_url(dependency.git_url)
            else:
                # 默认GitHub格式
                publish_url = self._build_github_publish_url(dependency.git_url)

            # 获取HTML页面
            response = requests.get(publish_url, timeout=30)
            response.raise_for_status()

            # 从HTML中提取发布包文件名
            versions = self._extract_versions_from_html(
                response.text,
                dependency.name
            )

            return versions

        except requests.RequestException:
            return []

    def _build_github_publish_url(self, git_url: str) -> str:
        """构建GitHub publish目录URL"""
        return f"{git_url}/tree/main/publish"

    def _build_gitlab_publish_url(self, git_url: str) -> str:
        """构建GitLab publish目录URL"""
        return f"{git_url}/-/tree/main/publish"

    def _extract_versions_from_html(self, html: str, lib_name: str) -> list[str]:
        """从HTML中提取版本号"""
        pattern = rf"{lib_name}-(\d+\.\d+\.\d+)\.tar\.gz"
        matches = re.findall(pattern, html)
        return list(set(matches))  # 去重

    def _find_latest_version(self, versions: list[str]) -> str | None:
        """找出最新版本"""
        if not versions:
            return None

        # 解析版本号
        version_tuples = []
        for version in versions:
            try:
                major, minor, patch = map(int, version.split("."))
                version_tuples.append((major, minor, patch, version))
            except ValueError:
                pass

        # 排序并返回最新版本
        version_tuples.sort(reverse=True)
        return version_tuples[0][3] if version_tuples else None

    def _is_newer(self, version1: str, version2: str) -> bool:
        """判断version1是否比version2新"""
        try:
            v1 = tuple(map(int, version1.split(".")))
            v2 = tuple(map(int, version2.split(".")))
            return v1 > v2
        except ValueError:
            return False
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/update/test_checker.py -v
```
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add kb/update/ tests/update/test_checker.py
git commit -m "feat(update): 实现版本检查器"
```

---

## Task 2: 实现版本更新器

**Files:**
- Create: `kb/update/updater.py`
- Test: `tests/update/test_updater.py`

- [ ] **Step 1: 创建版本更新器测试（失败测试优先）**

```python
# tests/update/test_updater.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from kb.update.updater import DependencyUpdater
from kb.core.models import Dependency


@patch("kb.dependency.downloader.PackageDownloader.download")
@patch("kb.dependency.extractor.PackageExtractor.extract")
def test_update_dependency(mock_extract, mock_download, tmp_path):
    # Mock下载返回一个虚拟文件
    cache_file = tmp_path / "cache" / "Dep1" / "1.3.0.tar.gz"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_bytes(b"test content")
    mock_download.return_value = cache_file

    # 创建测试Knowledge.md
    kb_file = tmp_path / "Knowledge.md"
    kb_file.write_text("""# Test

## 基本信息

- **名称**: Test
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| Dep1 | 1.2.0 | https://github.com/test/repo |
""")

    updater = DependencyUpdater()
    result = updater.update_dependency(kb_file, "Dep1", "1.3.0")

    assert result.success
    assert result.updated_version == "1.3.0"

    # 验证Knowledge.md已更新
    content = kb_file.read_text()
    assert "1.3.0" in content


@patch("kb.dependency.downloader.PackageDownloader.download")
@patch("kb.dependency.extractor.PackageExtractor.extract")
def test_update_dependency_not_found(mock_extract, mock_download, tmp_path):
    kb_file = tmp_path / "Knowledge.md"
    kb_file.write_text("""# Test

## 基本信息

- **名称**: Test
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| Dep1 | 1.2.0 | https://github.com/test/repo |
""")

    updater = DependencyUpdater()
    result = updater.update_dependency(kb_file, "NonExistent", "1.3.0")

    assert not result.success
    assert not result.updated_version
```

- [ ] **Step 2: 定义UpdateResult数据结构**

```python
# kb/update/__init__.py
from __future__ import annotations
from typing import TypedDict


class VersionUpdate(TypedDict):
    """版本更新信息"""
    name: str
    current_version: str
    new_version: str
    git_url: str


class UpdateResult(TypedDict):
    """更新结果"""
    success: bool
    updated_version: str | None
    error: str | None


__all__ = ["VersionUpdate", "UpdateResult"]
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/update/test_updater.py -v
```
Expected: FAIL with "DependencyUpdater not defined"

- [ ] **Step 4: 实现版本更新器**

```python
# kb/update/updater.py
from __future__ import annotations
from pathlib import Path
import re
from kb.core import KnowledgeParser
from kb.dependency import PackageDownloader, PackageExtractor
from kb.update import UpdateResult


class DependencyUpdater:
    """依赖更新器"""

    def __init__(self):
        self.parser = KnowledgeParser()
        self.downloader = PackageDownloader()
        self.extractor = PackageExtractor()

    def update_dependency(
        self,
        knowledge_file: Path,
        dependency_name: str,
        new_version: str,
    ) -> UpdateResult:
        """
        更新指定依赖到新版本

        Args:
            knowledge_file: Knowledge.md文件路径
            dependency_name: 依赖名称
            new_version: 新版本号

        Returns:
            更新结果
        """
        try:
            # 解析Knowledge.md
            metadata = self.parser.parse(knowledge_file)

            # 查找依赖
            dep_to_update = None
            for dep in metadata.dependencies:
                if dep.name == dependency_name:
                    dep_to_update = dep
                    break

            if not dep_to_update:
                return {
                    "success": False,
                    "updated_version": None,
                    "error": f"未找到依赖: {dependency_name}",
                }

            # 下载新版本
            click.echo(f"正在下载: {dependency_name} {new_version}")
            cache_file = self.downloader.download(
                dependency_name,
                new_version,
                dep_to_update.git_url,
                force=True
            )

            # 解压新版本
            from kb.dependency import DependencyResolver
            resolver = DependencyResolver()
            install_path = resolver.get_install_path(dep_to_update)
            install_path.parent.mkdir(parents=True, exist_ok=True)

            click.echo(f"正在解压到: {install_path}")
            self.extractor.extract(cache_file, install_path.parent)

            # 更新Knowledge.md中的版本号
            self._update_knowledge_file(knowledge_file, dependency_name, new_version)

            return {
                "success": True,
                "updated_version": new_version,
                "error": None,
            }

        except Exception as e:
            return {
                "success": False,
                "updated_version": None,
                "error": str(e),
            }

    def _update_knowledge_file(
        self,
        knowledge_file: Path,
        dependency_name: str,
        new_version: str
    ) -> None:
        """
        更新Knowledge.md中的依赖版本号

        Args:
            knowledge_file: Knowledge.md文件路径
            dependency_name: 依赖名称
            new_version: 新版本号
        """
        # 跨平台：显式指定 newline='\n' 确保一致性
        content = knowledge_file.read_text(encoding="utf-8", newline='\n')

        # 使用正则表达式替换依赖表中的版本号
        # 匹配: | Dep1 | 1.2.0 | ... |
        pattern = rf"(\|\s*{re.escape(dependency_name)}\s*\|\s*)\d+\.\d+\.\d+(\s*\|)"
        content = re.sub(pattern, rf"\g<1>{new_version}\g<2>", content)

        # 跨平台：显式指定 newline='\n' 确保一致性
        knowledge_file.write_text(content, encoding="utf-8", newline='\n')
```

- [ ] **Step 5: 添加导入**

```python
# kb/update/updater.py
# 在文件顶部添加
import click
```

- [ ] **Step 6: 运行测试验证通过**

```bash
pytest tests/update/test_updater.py -v
```
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add kb/update/updater.py kb/update/__init__.py tests/update/test_updater.py
git commit -m "feat(update): 实现依赖更新器"
```

---

## Task 3: 实现kb update命令

**Files:**
- Create: `kb/cli/update.py`
- Test: `tests/cli/test_update.py`

- [ ] **Step 1: 创建update命令测试（失败测试优先）**

```python
# tests/cli/test_update.py
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from kb.cli.main import cli


def test_check_updates():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # 创建测试Knowledge.md
        Path("src").mkdir()
        Path("src/Knowledge.md").write_text("""# Test

## 基本信息

- **名称**: Test
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| Dep1 | 1.2.0 | https://github.com/test/repo |
""")

        result = runner.invoke(cli, ["check-updates"])
        assert result.exit_code == 0


def test_update_dependency():
    runner = CliRunner()

    with runner.isolated_filesystem():
        Path("src").mkdir()
        Path("src/Knowledge.md").write_text("""# Test

## 基本信息

- **名称**: Test
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| Dep1 | 1.2.0 | https://github.com/test/repo |
""")

        # Mock更新
        with patch("kb.update.updater.DependencyUpdater.update_dependency") as mock_update:
            mock_update.return_value = {
                "success": True,
                "updated_version": "1.3.0",
                "error": None,
            }

            result = runner.invoke(cli, ["update", "Dep1"])
            assert result.exit_code == 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/cli/test_update.py -v
```
Expected: FAIL with "update command not registered"

- [ ] **Step 3: 实现update命令**

```python
# kb/cli/update.py
from pathlib import Path
import click
from kb.cli.main import cli
from kb.cli.utils import find_knowledge_file
from kb.update import VersionChecker, DependencyUpdater
from kb.dependency import ConflictDetector


@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=False),
    default=None,
    help="知识库文件路径"
)
def check_updates(path: str | None):
    """检查依赖是否有新版本"""
    if path:
        knowledge_file = Path(path)
    else:
        knowledge_file = find_knowledge_file()

    if not knowledge_file or not knowledge_file.exists():
        click.echo("未找到知识库文件")
        return

    try:
        checker = VersionChecker()
        metadata = checker.parser.parse(knowledge_file)

        if not metadata.dependencies:
            click.echo("无依赖需要检查")
            return

        updates = checker.check_updates(metadata.dependencies)

        if not updates:
            click.echo("所有依赖都是最新版本")
            return

        click.echo(f"发现 {len(updates)} 个可用更新:")
        for update in updates:
            click.echo(
                f"  {update['name']}: "
                f"{update['current_version']} → {update['new_version']}"
            )

    except Exception as e:
        click.echo(f"错误: {e}")


@cli.command()
@click.argument("name", required=False)
@click.option(
    "--path",
    type=click.Path(exists=False),
    default=None,
    help="知识库文件路径"
)
def update(name: str | None, path: str | None):
    """更新依赖到新版本"""
    if path:
        knowledge_file = Path(path)
    else:
        knowledge_file = find_knowledge_file()

    if not knowledge_file or not knowledge_file.exists():
        click.echo("未找到知识库文件")
        return

    try:
        checker = VersionChecker()

        if not name:
            # 更新所有依赖
            metadata = checker.parser.parse(knowledge_file)

            if not metadata.dependencies:
                click.echo("无依赖需要更新")
                return

            updates = checker.check_updates(metadata.dependencies)

            if not updates:
                click.echo("所有依赖都是最新版本")
                return

            click.echo(f"发现 {len(updates)} 个可用更新:")
            for update in updates:
                click.echo(
                    f"  {update['name']}: "
                    f"{update['current_version']} → {update['new_version']}"
                )

            if not click.confirm("确认更新以上依赖？"):
                click.echo("取消更新")
                return

            # 逐个更新
            updater = DependencyUpdater()
            for update_item in updates:
                result = updater.update_dependency(
                    knowledge_file,
                    update_item["name"],
                    update_item["new_version"]
                )

                if result["success"]:
                    click.echo(f"  {update_item['name']} 已更新到 {result['updated_version']}")
                else:
                    click.echo(f"  {update_item['name']} 更新失败: {result['error']}")

            # 检查版本冲突
            metadata = checker.parser.parse(knowledge_file)
            conflict_detector = ConflictDetector()
            conflict_detector.check_conflicts(metadata.dependencies)

            click.echo("更新完成")

        else:
            # 更新指定依赖
            updater = DependencyUpdater()
            result = updater.update_dependency(knowledge_file, name, "latest")

            if not result["success"]:
                click.echo(f"更新失败: {result['error']}")
                return

            click.echo(f"{name} 已更新到 {result['updated_version']}")

    except Exception as e:
        click.echo(f"错误: {e}")
```

- [ ] **Step 4: 修复check_updates逻辑**

```python
# kb/cli/update.py
# 修改check_updates函数中检查依赖的逻辑
@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=False),
    default=None,
    help="知识库文件路径"
)
def check_updates(path: str | None):
    """检查依赖是否有新版本"""
    if path:
        knowledge_file = Path(path)
    else:
        knowledge_file = find_knowledge_file()

    if not knowledge_file or not knowledge_file.exists():
        click.echo("未找到知识库文件")
        return

    try:
        checker = VersionChecker()
        metadata = checker.parser.parse(knowledge_file)

        if not metadata.dependencies:
            click.echo("无依赖需要检查")
            return

        updates = checker.check_updates(metadata.dependencies)

        if not updates:
            click.echo("所有依赖都是最新版本")
            return

        click.echo(f"发现 {len(updates)} 个可用更新:")
        for update in updates:
            click.echo(
                f"  {update['name']}: "
                f"{update['current_version']} → {update['new_version']}"
            )

    except Exception as e:
        click.echo(f"错误: {e}")
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/cli/test_update.py -v
```
Expected: PASS

- [ ] **Step 6: 手动测试**

```bash
python -m kb.cli.main check-updates --help
python -m kb.cli.main update --help
```
Expected: 显示帮助信息

- [ ] **Step 7: 提交**

```bash
git add kb/cli/update.py tests/cli/test_update.py
git commit -m "feat(cli): 实现kb update命令"
```

---

## Task 4: 更新CLI主模块

**Files:**
- Modify: `kb/cli/main.py`

- [ ] **Step 1: 更新main.py**

```python
# kb/cli/main.py
import click

from kb.cli import cache  # noqa: F401
from kb.cli import update  # noqa: F401


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
git commit -m "refactor(cli): 注册update命令"
```

---

## Task 5: 最终测试和文档更新

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
| `kb check-updates` | 检查依赖是否有新版本 |
| `kb update` | 更新依赖到新版本 |
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

### 依赖更新

检查依赖更新：

```bash
kb check-updates                 # 检查所有依赖
kb check-updates --path src/Knowledge.md    # 指定知识库文件
```

更新依赖：

```bash
kb update                       # 更新所有可更新的依赖
kb update CommonDataTypes        # 更新指定依赖
```

更新后会自动修改 `Knowledge.md` 中的版本号，并重新下载新版本的依赖。

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
git commit -m "docs: 更新README添加依赖更新说明"
```

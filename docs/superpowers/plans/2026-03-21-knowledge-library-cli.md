# Knowledge Library CLI Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现命令行工具基础框架，提供kb init和kb package命令

**Architecture:** 使用Click框架构建CLI，采用命令子命令结构。每个命令独立模块，清晰的错误处理和用户提示。复用核心模块的解析和验证功能。

**Tech Stack:** Python 3.11+, Click 8.x, pytest

**Cross-Platform Support:**
- Click 框架支持 Windows、macOS、Linux
- 文件路径使用 `pathlib.Path`，自动处理路径分隔符
- tar.gz 格式在所有平台都能正常打包和解压

---

## File Structure

```
kb/
├── cli/
│   ├── __init__.py
│   ├── main.py           # CLI入口，命令路由
│   ├── init.py           # kb init命令实现
│   ├── package.py        # kb package命令实现
│   └── utils.py          # CLI工具函数
```

---

## Task 1: 设置Click依赖和CLI入口

**Files:**
- Modify: `requirements.txt`
- Create: `kb/cli/__init__.py`
- Create: `kb/cli/main.py`
- Test: `tests/cli/test_main.py`

- [ ] **Step 1: 更新requirements.txt**

```text
pydantic>=2.0.0
click>=8.0.0
```

- [ ] **Step 2: 创建CLI入口测试（失败测试优先）**

```python
# tests/cli/test_main.py
from click.testing import CliRunner
from kb.cli.main import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "package" in result.output
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/cli/test_main.py -v
```
Expected: FAIL with "cli not defined"

- [ ] **Step 4: 实现最小化的CLI入口**

```python
# kb/cli/__init__.py
"""Knowledge Base CLI Module"""
```

```python
# kb/cli/main.py
import click


@click.group()
@click.version_option(version="0.1.0", prog_name="kb")
def cli():
    """Knowledge Base CLI Tool - 知识库命令行工具"""
    pass


if __name__ == "__main__":
    cli()
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/cli/test_main.py -v
```
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add requirements.txt kb/cli/ tests/cli/test_main.py
git commit -m "feat(cli): 创建CLI入口框架"
```

---

## Task 2: 实现kb init命令（骨架版本）

**Files:**
- Create: `kb/cli/init.py`
- Test: `tests/cli/test_init.py`

- [ ] **Step 1: 创建init命令测试（失败测试优先）**

```python
# tests/cli/test_init.py
from click.testing import CliRunner
from kb.cli.main import cli


def test_init_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "初始化完成" in result.output


def test_init_without_knowledge_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        # 当没有Knowledge.md文件时，应该提示
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/cli/test_init.py -v
```
Expected: FAIL with "init command not registered"

- [ ] **Step 3: 实现最小化的init命令**

```python
# kb/cli/init.py
from pathlib import Path
import click
from kb.cli.main import cli


@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=False),
    default="src/Knowledge.md",
    help="知识库文件路径"
)
def init(path: str):
    """初始化知识库，下载所有依赖"""
    knowledge_file = Path(path)

    if not knowledge_file.exists():
        click.echo(f"未找到知识库文件: {knowledge_file}")
        click.echo("请确保在知识库目录下运行此命令，或指定正确的路径")
        return

    click.echo(f"正在初始化知识库...")
    click.echo(f"读取知识库文件: {knowledge_file}")

    # TODO: 解析Knowledge.md
    # TODO: 检查缓存
    # TODO: 下载依赖
    # TODO: 解压到deps目录

    click.echo("初始化完成")
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/cli/test_init.py -v
```
Expected: PASS

- [ ] **Step 5: 手动测试**

```bash
python -m kb.cli.main init --help
```
Expected: 显示帮助信息

- [ ] **Step 6: 提交**

```bash
git add kb/cli/init.py tests/cli/test_init.py
git commit -m "feat(cli): 实现kb init命令（骨架版本）"
```

---

## Task 3: 实现kb package命令（骨架版本）

**Files:**
- Create: `kb/cli/package.py`
- Test: `tests/cli/test_package.py`

- [ ] **Step 1: 创建package命令测试（失败测试优先）**

```python
# tests/cli/test_package.py
from click.testing import CliRunner
from kb.cli.main import cli


def test_package_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # 创建最小化的目录结构
        Path("src").mkdir()
        Path("src/Knowledge.md").write_text("# Test\n\n## 基本信息\n- **名称**: Test\n- **版本**: 1.0.0\n- **类型**: test\n- **职责描述**: 测试\n")

        result = runner.invoke(cli, ["package"])
        assert result.exit_code == 0
        assert "打包完成" in result.output


def test_package_without_src():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["package"])
        assert result.exit_code == 1
        assert "错误" in result.output
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/cli/test_package.py -v
```
Expected: FAIL with "package command not registered"

- [ ] **Step 3: 实现最小化的package命令**

```python
# kb/cli/package.py
from pathlib import Path
import click
import tarfile
from kb.cli.main import cli


@cli.command()
def package():
    """打包当前知识库并生成发布包"""
    src_dir = Path("src")
    publish_dir = Path("publish")

    if not src_dir.exists():
        click.echo("错误: 未找到 src/ 目录")
        click.echo("请确保在知识库根目录下运行此命令")
        return 1

    # 读取Knowledge.md获取名称和版本
    knowledge_file = src_dir / "Knowledge.md"
    if not knowledge_file.exists():
        click.echo("错误: 未找到 src/Knowledge.md")
        return 1

    # TODO: 解析Knowledge.md获取名称和版本
    name = "Test"
    version = "1.0.0"

    # 确保publish目录存在
    publish_dir.mkdir(exist_ok=True)

    # TODO: 读取.kb-package.yml配置
    # TODO: 根据配置确定要打包的文件列表

    # 创建发布包
    package_name = f"{name}-{version}.tar.gz"
    package_path = publish_dir / package_name

    click.echo(f"正在打包: {package_name}")

    # TODO: 实际打包逻辑
    # 这里先创建一个空的tar.gz作为占位
    with tarfile.open(package_path, "w:gz") as tar:
        pass

    click.echo(f"打包完成: {package_path}")

    return 0
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/cli/test_package.py -v
```
Expected: PASS

- [ ] **Step 5: 手动测试**

```bash
python -m kb.cli.main package --help
```
Expected: 显示帮助信息

- [ ] **Step 6: 提交**

```bash
git add kb/cli/package.py tests/cli/test_package.py
git commit -m "feat(cli): 实现kb package命令（骨架版本）"
```

---

## Task 4: 创建CLI工具函数模块

**Files:**
- Create: `kb/cli/utils.py`
- Test: `tests/cli/test_utils.py`

- [ ] **Step 1: 创建工具函数模块（带测试）**

```python
# kb/cli/utils.py
from pathlib import Path


def find_knowledge_file(start_dir: Path = None) -> Path | None:
    """查找Knowledge.md文件"""
    if start_dir is None:
        start_dir = Path.cwd()

    # 常见路径
    candidates = [
        start_dir / "Knowledge.md",
        start_dir / "src" / "Knowledge.md",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def ensure_directory(path: Path) -> None:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
```

```python
# tests/cli/test_utils.py
from pathlib import Path
from kb.cli.utils import find_knowledge_file, ensure_directory


def test_find_knowledge_file_in_current_dir():
    with Path("test_find").mkdir(exist_ok=True) as test_dir:
        (test_dir / "Knowledge.md").write_text("# Test")
        result = find_knowledge_file(test_dir)
        assert result is not None
        assert result.name == "Knowledge.md"
        Path("test_find").rmdir()


def test_find_knowledge_file_in_src():
    with Path("test_find").mkdir(exist_ok=True) as test_dir:
        (test_dir / "src").mkdir()
        (test_dir / "src" / "Knowledge.md").write_text("# Test")
        result = find_knowledge_file(test_dir)
        assert result is not None
        from shutil import rmtree
        rmtree("test_find")


def test_find_knowledge_file_not_found():
    with Path("test_find").mkdir(exist_ok=True) as test_dir:
        result = find_knowledge_file(test_dir)
        assert result is None
        Path("test_find").rmdir()


def test_ensure_directory():
    test_dir = Path("test_ensure")
    test_dir2 = test_dir / "sub" / "dir"
    ensure_directory(test_dir2)
    assert test_dir2.exists()

    from shutil import rmtree
    rmtree(test_dir)
```

- [ ] **Step 2: 运行测试**

```bash
pytest tests/cli/test_utils.py -v
```
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add kb/cli/utils.py tests/cli/test_utils.py
git commit -m "feat(cli): 添加CLI工具函数"
```

---

## Task 5: 集成核心模块到CLI

**Files:**
- Modify: `kb/cli/init.py`
- Modify: `kb/cli/package.py`
- Test: `tests/cli/test_integration.py`

- [ ] **Step 1: 修改init命令使用核心模块**

```python
# kb/cli/init.py
from pathlib import Path
import click
from kb.cli.main import cli
from kb.cli.utils import find_knowledge_file
from kb.core import KnowledgeParser


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
    click.echo(f"读取知识库文件: {knowledge_file}")

    try:
        # 使用核心模块解析Knowledge.md
        parser = KnowledgeParser()
        metadata = parser.parse(knowledge_file)

        click.echo(f"知识库: {metadata.name} v{metadata.version}")

        # TODO: 检查缓存
        # TODO: 下载依赖
        # TODO: 解压到deps目录

        click.echo("初始化完成")
    except Exception as e:
        click.echo(f"错误: {e}")
        return 1
```

- [ ] **Step 2: 修改package命令使用核心模块**

```python
# kb/cli/package.py
from pathlib import Path
import click
import tarfile
from kb.cli.main import cli
from kb.core import KnowledgeParser
from kb.cli.utils import find_knowledge_file


@cli.command()
def package():
    """打包当前知识库并生成发布包"""
    knowledge_file = find_knowledge_file()

    if not knowledge_file:
        click.echo("错误: 未找到 Knowledge.md")
        click.echo("请确保在知识库根目录下运行此命令")
        return 1

    click.echo(f"正在读取知识库文件: {knowledge_file}")

    try:
        parser = KnowledgeParser()
        metadata = parser.parse(knowledge_file)

        name = metadata.name
        version = metadata.version

        click.echo(f"知识库: {name} v{version}")

        src_dir = knowledge_file.parent
        publish_dir = Path("publish")

        # 确保publish目录存在
        publish_dir.mkdir(exist_ok=True)

        # 创建发布包
        package_name = f"{name}-{version}.tar.gz"
        package_path = publish_dir / package_name

        click.echo(f"正在打包: {package_name}")

        # TODO: 读取.kb-package.yml配置
        # TODO: 根据配置确定要打包的文件列表
        # 暂时打包整个src目录
        with tarfile.open(package_path, "w:gz") as tar:
            for item in src_dir.iterdir():
                tar.add(item, arcname=item.name)

        click.echo(f"打包完成: {package_path}")

        return 0
    except Exception as e:
        click.echo(f"错误: {e}")
        return 1
```

- [ ] **Step 3: 创建集成测试**

```python
# tests/cli/test_integration.py
from click.testing import CliRunner
from pathlib import Path
from kb.cli.main import cli


def test_init_with_valid_knowledge():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # 创建有效的Knowledge.md
        Path("src").mkdir()
        Path("src/Knowledge.md").write_text("""# TestLib

## 基本信息

- **名称**: TestLib
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试库
""")

        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "TestLib" in result.output
        assert "1.0.0" in result.output


def test_package_with_valid_knowledge():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # 创建有效的Knowledge.md
        Path("src").mkdir()
        Path("src/Knowledge.md").write_text("""# TestLib

## 基本信息

- **名称**: TestLib
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试库
""")

        result = runner.invoke(cli, ["package"])
        assert result.exit_code == 0
        assert "打包完成" in result.output
        assert Path("publish/TestLib-1.0.0.tar.gz").exists()
```

- [ ] **Step 4: 运行集成测试**

```bash
pytest tests/cli/test_integration.py -v
```
Expected: PASS

- [ ] **Step 5: 运行所有测试**

```bash
pytest tests/ -v
```
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add kb/cli/ tests/cli/test_integration.py
git commit -m "feat(cli): 集成核心模块到CLI命令"
```

---

## Task 6: 最终测试和文档

**Files:**
- Create: `README.md`
- Modify: `kb/__init__.py`

- [ ] **Step 1: 创建README.md**

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

## 开发

```bash
pytest tests/ -v
```
```

- [ ] **Step 2: 更新__init__.py**

```python
# kb/__init__.py
"""Knowledge Base CLI Tool"""

__version__ = "0.1.0"

from kb.cli.main import cli

__all__ = ["cli"]
```

- [ ] **Step 3: 运行最终测试**

```bash
pytest tests/ -v --cov=kb --cov-report=html
```
Expected: PASS with coverage report

- [ ] **Step 4: 提交**

```bash
git add README.md kb/__init__.py
git commit -m "docs: 添加README和最终测试"
```

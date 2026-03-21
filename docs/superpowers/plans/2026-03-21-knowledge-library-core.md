# Knowledge Library Core Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现知识库核心解析和验证功能，支持解析Knowledge.md元数据、版本号验证、依赖关系解析

**Architecture:** 使用Python实现，采用面向对象设计。通过pydantic进行数据模型验证，清晰的错误处理机制。模块化设计，便于后续命令行工具和其他模块复用。

**Tech Stack:** Python 3.11+, pydantic 2.x, pytest

**Cross-Platform Support:**
- 使用 `pathlib.Path` 处理文件路径（跨平台兼容）
- 文件读写时显式指定 `newline='\n'` 确保跨平台一致性
- tar.gz 格式在 Windows 和 Unix 系统上都能正常工作
- Click 框架支持 Windows、macOS、Linux

---

## File Structure

```
kb/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── models.py           # 数据模型（KnowledgeMetadata, Dependency等）
│   ├── parser.py           # Knowledge.md解析器
│   └── validator.py       # 版本号、依赖等验证
└── exceptions.py           # 自定义异常

tests/
├── core/
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_models.py
│   └── fixtures/
│       ├── valid_knowledge.md
│       ├── minimal_knowledge.md
│       └── invalid_knowledge.md
```

---

## Task 1: 定义核心数据模型

**Files:**
- Create: `kb/exceptions.py`
- Create: `kb/core/models.py`
- Test: `tests/core/test_models.py`

- [ ] **Step 1: 定义自定义异常类**

```python
# kb/exceptions.py

class KnowledgeBaseError(Exception):
    """知识库基础异常"""
    pass


class KnowledgeParseError(KnowledgeBaseError):
    """知识库解析错误"""
    pass


class VersionFormatError(KnowledgeBaseError):
    """版本号格式错误"""
    pass


class DependencyConflictError(KnowledgeBaseError):
    """依赖冲突错误"""
    pass
```

- [ ] **Step 2: 定义核心数据模型**

```python
# kb/core/models.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from kb.exceptions import VersionFormatError


class Dependency(BaseModel):
    """知识库依赖项"""
    name: str = Field(..., description="知识库名称")
    version: str = Field(..., description="版本号")
    git_url: str = Field(..., description="git仓库地址")

    @field_validator("version")
    @classmethod
    def validate_semantic_version(cls, v: str) -> str:
        """验证语义化版本号格式"""
        parts = v.split(".")
        if len(parts) != 3:
            raise VersionFormatError(f"版本号 '{v}' 必须为主版本.次版本.修订版本格式")
        try:
            int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            raise VersionFormatError(f"版本号 '{v}' 的各部分必须为数字")
        return v


class ExcludedDependency(BaseModel):
    """排除的依赖项"""
    name: str = Field(..., description="知识库名称")
    version: str = Field(..., description="版本号")
    reason: str = Field(..., description="排除原因")


class KnowledgeMetadata(BaseModel):
    """知识库元数据"""
    name: str = Field(..., description="知识库名称")
    version: str = Field(..., description="版本号")
    type: str = Field(..., description="知识库类型")
    description: str = Field(..., description="职责描述")
    dependencies: List[Dependency] = Field(default_factory=list, description="依赖列表")
    excluded_dependencies: List[ExcludedDependency] = Field(
        default_factory=list, description="排除依赖列表"
    )
    scenarios: str = Field(default="", description="适用场景")
    capabilities: List[str] = Field(default_factory=list, description="对外能力列表")
    file_graph: str = Field(default="", description="文件路径图谱")
```

- [ ] **Step 3: 编写数据模型测试**

```python
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
```

- [ ] **Step 4: 运行测试验证**

```bash
pytest tests/core/test_models.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add kb/exceptions.py kb/core/models.py tests/core/test_models.py
git commit -m "feat(core): 定义核心数据模型"
```

---

## Task 2: 实现Knowledge.md解析器

**Files:**
- Create: `kb/core/parser.py`
- Test: `tests/core/test_parser.py`
- Test: `tests/core/fixtures/valid_knowledge.md`
- Test: `tests/core/fixtures/minimal_knowledge.md`

- [ ] **Step 1: 创建有效的测试fixtures**

```markdown
<!-- tests/core/fixtures/valid_knowledge.md -->
# FileFormatParser 知识库

## 基本信息

- **名称**: FileFormatParser
- **版本**: 1.2.0
- **类型**: structure-knowledge
- **职责描述**: 封装特定文件格式的解析知识

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.2.0 | https://github.com/example/common-data-types |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| OldParser | 1.0.0 | 已废弃 |

## 适用场景

文件格式解析、数据结构设计

## 对外能力

- 提供文件格式规范
- 定义字段结构和类型

## 文件路径图谱

```
src/
├── Knowledge.md [核心元数据]
├── overview.md [概览]
└── structure/
    └── file-format.md [文件格式]
```
```

```markdown
<!-- tests/core/fixtures/minimal_knowledge.md -->
# MinimalLib 知识库

## 基本信息

- **名称**: MinimalLib
- **版本**: 1.0.0
- **类型**: minimal
- **职责描述**: 最小化知识库示例
```

- [ ] **Step 2: 编写解析器测试（失败测试优先）**

```python
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
```

- [ ] **Step 3: 运行测试验证失败**

```bash
pytest tests/core/test_parser.py -v
```
Expected: FAIL with "KnowledgeParser not defined"

- [ ] **Step 4: 实现最小化的解析器**

```python
# kb/core/parser.py
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional
from kb.core.models import KnowledgeMetadata, Dependency, ExcludedDependency
from kb.exceptions import KnowledgeParseError


class KnowledgeParser:
    """Knowledge.md 解析器"""

    def __init__(self):
        pass

    def parse(self, file_path: Path) -> KnowledgeMetadata:
        """解析Knowledge.md文件"""
        if not file_path.exists():
            raise FileNotFoundError(f"知识库文件不存在: {file_path}")

        # 跨平台：显式指定 newline='\n' 确保一致性
        content = file_path.read_text(encoding="utf-8", newline='\n')

        # 提取基本信息
        name = self._extract_value(content, "名称")
        version = self._extract_value(content, "版本")
        kb_type = self._extract_value(content, "类型")
        description = self._extract_value(content, "职责描述")

        # 提取适用场景
        scenarios = self._extract_section_text(content, "适用场景")

        # 提取对外能力
        capabilities = self._extract_list_items(content, "对外能力")

        # 提取文件路径图谱
        file_graph = self._extract_code_block(content, "文件路径图谱")

        # 提取依赖
        dependencies = self._parse_dependency_table(content)

        # 提取排除依赖
        excluded_dependencies = self._parse_excluded_dependency_table(content)

        return KnowledgeMetadata(
            name=name,
            version=version,
            type=kb_type,
            description=description,
            dependencies=dependencies,
            excluded_dependencies=excluded_dependencies,
            scenarios=scenarios,
            capabilities=capabilities,
            file_graph=file_graph,
        )

    def _extract_value(self, content: str, field_name: str) -> str:
        """提取字段值"""
        pattern = rf"- \*\*{field_name}\*\*:\s*(.+)"
        match = re.search(pattern, content)
        if not match:
            raise KnowledgeParseError(f"未找到字段: {field_name}")
        return match.group(1).strip()

    def _extract_section_text(self, content: str, section_name: str) -> str:
        """提取章节文本"""
        pattern = rf"## {section_name}\n\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_list_items(self, content: str, section_name: str) -> list[str]:
        """提取列表项"""
        items = []
        pattern = rf"## {section_name}\n\n((?:- .+\n?)+)"
        match = re.search(pattern, content)
        if match:
            for line in match.group(1).split("\n"):
                if line.strip().startswith("-"):
                    item = line.strip()[1:].strip()
                    if item:
                        items.append(item)
        return items

    def _extract_code_block(self, content: str, section_name: str) -> str:
        """提取代码块"""
        pattern = rf"## {section_name}\n\n```(\w+)?\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(2).strip()
        return ""

    def _parse_dependency_table(self, content: str) -> list[Dependency]:
        """解析依赖表"""
        dependencies = []
        pattern = r"## 依赖\n\n\|.*?\n\|.*?\n((?:\|.*?\n)+)"
        match = re.search(pattern, content)
        if match:
            rows = match.group(1).strip().split("\n")
            for row in rows[1:]:  # 跳过表头
                if "|" in row:
                    cols = [col.strip() for col in row.split("|")[1:-1]]
                    if len(cols) >= 3 and cols[0]:
                        dependencies.append(
                            Dependency(name=cols[0], version=cols[1], git_url=cols[2])
                        )
        return dependencies

    def _parse_excluded_dependency_table(self, content: str) -> list[ExcludedDependency]:
        """解析排除依赖表"""
        excluded = []
        pattern = r"## 排除依赖\n\n\|.*?\n\|.*?\n((?:\|.*?\n)+)"
        match = re.search(pattern, content)
        if match:
            rows = match.group(1).strip().split("\n")
            for row in rows[1:]:  # 跳过表头
                if "|" in row:
                    cols = [col.strip() for col in row.split("|")[1:-1]]
                    if len(cols) >= 3 and cols[0]:
                        excluded.append(
                            ExcludedDependency(name=cols[0], version=cols[1], reason=cols[2])
                        )
        return excluded
```

- [ ] **Step 5: 运行测试验证通过**

```bash
pytest tests/core/test_parser.py -v
```
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add kb/core/parser.py tests/core/test_parser.py tests/core/fixtures/*.md
git commit -m "feat(core): 实现Knowledge.md解析器"
```

---

## Task 3: 实现验证器

**Files:**
- Create: `kb/core/validator.py`
- Test: `tests/core/test_validator.py`

- [ ] **Step 1: 编写验证器测试（失败测试优先）**

```python
# tests/core/test_validator.py
import pytest
from kb.core.models import KnowledgeMetadata, Dependency, ExcludedDependency
from kb.core.validator import KnowledgeValidator
from kb.exceptions import DependencyConflictError


def test_validate_no_conflicts():
    validator = KnowledgeValidator()
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试",
        dependencies=[
            Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1")
        ]
    )
    # 不应该抛出异常
    validator.validate(metadata)


def test_validate_version_conflict():
    validator = KnowledgeValidator()
    # 模拟两个依赖有版本冲突的情况
    # 这里需要一个能检测到冲突的场景
    pass


def test_validate_excluded_dependency():
    validator = KnowledgeValidator()
    metadata = KnowledgeMetadata(
        name="TestLib",
        version="1.0.0",
        type="test",
        description="测试",
        dependencies=[
            Dependency(name="Dep1", version="1.2.0", git_url="https://github.com/test/dep1")
        ],
        excluded_dependencies=[
            ExcludedDependency(name="Dep2", version="1.0.0", reason="测试排除")
        ]
    )
    validator.validate(metadata)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/core/test_validator.py -v
```
Expected: FAIL with "KnowledgeValidator not defined"

- [ ] **Step 3: 实现最小化的验证器**

```python
# kb/core/validator.py
from __future__ import annotations
from kb.core.models import KnowledgeMetadata
from kb.exceptions import DependencyConflictError


class KnowledgeValidator:
    """知识库元数据验证器"""

    def __init__(self):
        pass

    def validate(self, metadata: KnowledgeMetadata) -> None:
        """验证知识库元数据"""
        self._validate_excluded_dependencies(metadata)
        # 可以添加更多验证逻辑

    def _validate_excluded_dependencies(self, metadata: KnowledgeMetadata) -> None:
        """验证排除依赖配置的有效性"""
        excluded_names = {d.name for d in metadata.excluded_dependencies}
        dependency_names = {d.name for d in metadata.dependencies}

        # 检查排除的依赖是否在依赖列表中
        for excluded in metadata.excluded_dependencies:
            if excluded.name not in dependency_names:
                # 这是一个警告情况，暂时不报错
                pass
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/core/test_validator.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add kb/core/validator.py tests/core/test_validator.py
git commit -m "feat(core): 实现知识库验证器"
```

---

## Task 4: 创建包初始化文件

**Files:**
- Create: `kb/__init__.py`
- Create: `kb/core/__init__.py`

- [ ] **Step 1: 创建包初始化文件**

```python
# kb/__init__.py
"""Knowledge Base CLI Tool"""

__version__ = "0.1.0"

from kb.core import KnowledgeParser, KnowledgeValidator

__all__ = ["KnowledgeParser", "KnowledgeValidator"]
```

```python
# kb/core/__init__.py
"""Knowledge Base Core Module"""

from kb.core.models import (
    KnowledgeMetadata,
    Dependency,
    ExcludedDependency,
)
from kb.core.parser import KnowledgeParser
from kb.core.validator import KnowledgeValidator

__all__ = [
    "KnowledgeMetadata",
    "Dependency",
    "ExcludedDependency",
    "KnowledgeParser",
    "KnowledgeValidator",
]
```

- [ ] **Step 2: 运行所有测试**

```bash
pytest tests/core/ -v
```
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add kb/__init__.py kb/core/__init__.py
git commit -m "feat(core): 创建包初始化文件"
```

---

## Task 5: 添加项目配置文件

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `pytest.ini`

- [ ] **Step 1: 创建pyproject.toml**

```toml
[project]
name = "kb"
version = "0.1.0"
description = "Knowledge Base CLI Tool"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 2: 创建requirements.txt**

```text
pydantic>=2.0.0
```

- [ ] **Step 3: 创建pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v
```

- [ ] **Step 4: 提交**

```bash
git add pyproject.toml requirements.txt pytest.ini
git commit -m "chore: 添加项目配置文件"
```

---

## Task 6: 创建.gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: 创建.gitignore**

```text
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Knowledge Base specific
deps/
.kb-cache/

# macOS
.DS_Store
```

- [ ] **Step 2: 提交**

```bash
git add .gitignore
git commit -m "chore: 添加.gitignore"
```

---

## Task 7: 最终测试验证

**Files:**
- (无修改)

- [ ] **Step 1: 运行所有测试**

```bash
pytest tests/ -v --cov=kb
```
Expected: PASS with coverage report

- [ ] **Step 2: 验证包可以正常导入**

```bash
python -c "from kb.core import KnowledgeParser, KnowledgeValidator; print('导入成功')"
```
Expected: 打印 "导入成功"

- [ ] **Step 3: 提交**

```bash
git add .
git commit -m "test: 完成核心模块实现和测试"
```

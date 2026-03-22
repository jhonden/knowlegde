# 版本检查器使用指南

## 概述

版本检查器 (`VersionChecker`) 是一个用于检查知识库依赖项最新版本的工具。它支持从 GitHub 和 GitLab 获取最新版本信息，并比较版本号以确定是否有可用更新。

## 功能特性

- 支持 GitHub 和 GitLab 仓库
- 自动从 API 获取最新版本
- 智能版本比较（支持语义化版本）
- 批量检查多个依赖
- 单个依赖检查
- 完善的错误处理

## 基本用法

### 1. 检查多个依赖的更新

```python
from pathlib import Path
from kb.update.checker import VersionChecker
from kb.core.parser import KnowledgeParser

# 初始化检查器
checker = VersionChecker()

# 解析知识库文件
parser = KnowledgeParser()
metadata = parser.parse(Path("Knowledge.md"))

# 检查所有依赖的更新
update_list = checker.check_updates(metadata.dependencies)

# 显示结果
if update_list.has_updates():
    print(f"发现 {len(update_list)} 个可用更新:")
    for update in update_list:
        print(f"  - {update.name}: {update.current_version} -> {update.latest_version}")
else:
    print("所有依赖都是最新版本")
```

### 2. 检查单个依赖的更新

```python
from pathlib import Path
from kb.update.checker import VersionChecker

checker = VersionChecker()

# 从知识库文件中检查单个依赖
update_list = checker.check_single_dependency(
    Path("Knowledge.md"),
    "CommonDataTypes"
)

for update in update_list:
    if update.update_available:
        print(f"{update.name} 有新版本: {update.latest_version}")
    else:
        print(f"{update.name} 已是最新版本: {update.current_version}")
```

### 3. 手动创建依赖并检查

```python
from kb.update.checker import VersionChecker
from kb.core.models import Dependency

checker = VersionChecker()

# 创建依赖对象
dependency = Dependency(
    name="my-library",
    version="1.0.0",
    git_url="https://github.com/example/my-library"
)

# 检查更新
update = checker._check_single_dependency(dependency)

if update.update_available:
    print(f"发现新版本: {update.latest_version}")
```

## API 参考

### VersionChecker 类

#### `__init__(self)`
初始化版本检查器。

#### `check_updates(self, dependencies: List[Dependency]) -> VersionUpdateList`
检查多个依赖的更新情况。

**参数:**
- `dependencies`: 依赖列表

**返回:**
- `VersionUpdateList`: 版本更新列表

#### `check_single_dependency(self, knowledge_file: Path, dependency_name: str) -> VersionUpdateList`
从知识库文件中检查单个依赖的更新情况。

**参数:**
- `knowledge_file`: Knowledge.md 文件路径
- `dependency_name`: 要检查的依赖名称

**返回:**
- `VersionUpdateList`: 版本更新列表（只包含一个更新）

### VersionUpdate 类

版本更新信息模型。

**属性:**
- `name`: 依赖名称
- `current_version`: 当前版本
- `latest_version`: 最新版本
- `git_url`: Git 仓库地址
- `update_available`: 是否有可用更新

### VersionUpdateList 类

版本更新列表模型。

**方法:**
- `add_update(self, update: VersionUpdate)`: 添加一个更新信息
- `has_updates(self) -> bool`: 检查是否有可用更新
- `__len__(self) -> int`: 返回更新数量
- `__iter__(self)`: 支持迭代

## 版本比较规则

版本检查器支持语义化版本 (Semantic Versioning) 比较：

- `1.0.0` vs `1.0.1` → 有更新（修订版本）
- `1.0.0` vs `1.1.0` → 有更新（次版本）
- `1.0.0` vs `2.0.0` → 有更新（主版本）
- `2.0.0` vs `1.0.0` → 无更新（降级）
- `1.0.0` vs `1.0.0` → 无更新（相同）

版本比较自动处理：
- `v` 前缀（如 `v1.0.0`）
- 预发布标签（如 `1.0.0-alpha.1`）

## 支持的平台

### GitHub
```
https://github.com/owner/repo
```

### GitLab
```
https://gitlab.com/owner/repo
```

其他平台会抛出 `KnowledgeBaseError` 异常。

## 错误处理

版本检查器会捕获并处理各种错误情况：

```python
from kb.exceptions import KnowledgeBaseError

try:
    update_list = checker.check_updates(dependencies)
except KnowledgeBaseError as e:
    print(f"检查更新失败: {e}")
except FileNotFoundError:
    print("知识库文件不存在")
```

常见错误：
- `KnowledgeBaseError`: 通用错误（网络错误、API 错误、解析错误等）
- `FileNotFoundError`: 知识库文件不存在
- `ValueError`: 版本号格式错误

## 性能考虑

- API 请求超时设置为 30 秒
- 检查失败会继续处理其他依赖
- 建议批量检查多个依赖以提高效率

## 示例输出

```
发现 2 个可用更新:
  - CommonDataTypes: 1.0.0 -> 2.0.0
  - UtilsLib: 2.1.0 -> 2.2.0
```

## 测试

运行版本检查器测试：

```bash
pytest tests/update/ -v
```

运行测试并查看覆盖率：

```bash
pytest tests/update/ -v --cov=kb/update --cov-report=html
```

## 注意事项

1. 需要网络连接访问 GitHub/GitLab API
2. API 可能有速率限制（GitHub: 60 次/小时未认证）
3. 私有仓库需要认证（当前版本不支持）
4. 版本号必须符合语义化版本规范

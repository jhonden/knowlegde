# Knowledge Base Development Skill Design

## Skill 概述

**Skill 名称：** `knowledge-base-development`

**适用场景：**
- 创建新的知识库项目
- 开发和维护知识库（添加功能、修改代码、更新依赖）
- 打包和发布知识库
- 管理知识库依赖和缓存

**核心职责：**
- 指导智能体理解知识库系统的概念和工作流程
- 根据用户需求选择合适的开发阶段或具体任务
- 优先通过 kb CLI 命令执行操作
- 当 CLI 无法满足需求时，提供指导让智能体自主决策

**使用优先级：**
- 1%+ 可能性 → 必须使用此 Skill
- 涉及知识库项目的任何工作 → 使用此 Skill

**Skill 结构：**
1. 概述和适用场景
2. 知识库系统概念
3. 工作流程（按阶段和任务划分）
4. 技术规范（目录结构、文件格式、CLI 命令）
5. 最佳实践和常见陷阱

## 知识库系统概念

### 核心概念

#### 1. 知识库（Knowledge Base）

封装模块/领域核心背景知识的可复用单元。

**特性：**
- 包含元数据、源代码、依赖关系
- 支持版本管理、依赖管理、打包发布
- 可被其他知识库依赖

**用途：**
- 封装特定领域的核心背景知识
- 提供可复用的数据模型和工具函数
- 建立知识库生态系统

#### 2. Knowledge.md

知识库的元数据文件，位于 `src/` 目录下。

**内容：**
- 基本信息（名称、版本、类型、职责描述）
- 依赖表（声明依赖的知识库）
- 排除依赖表（明确排除的依赖）
- 其他文档内容（API 说明、使用示例等）

**格式：**
- 使用 Markdown 格式
- 依赖和排除依赖使用 Markdown 表格

#### 3. 语义化版本号

**格式：** 主版本.次版本.修订版本（如 1.0.0）

**规则：**
- 主版本号（MAJOR）：不兼容的 API 变更
- 次版本号（MINOR）：向后兼容的功能新增
- 修订版本号（PATCH）：向后兼容的 bug 修复

**版本范围：**
- 精确版本：`1.0.0`（只匹配此版本）
- 兼容版本：`^1.0.0`（匹配 >= 1.0.0 且 < 2.0.0）
- 补丁版本：`~2.1.0`（匹配 >= 2.1.0 且 < 2.2.0）
- 预发布版本：`1.0.0-alpha.1`（预发布标识）

#### 4. 依赖管理

**声明依赖：**
- 在 Knowledge.md 的依赖表中声明
- 指定知识库名称、版本号、Git 地址

**自动下载：**
- 运行 `kb init` 时自动下载
- 下载到 `deps/` 目录并解压
- 使用缓存避免重复下载

**版本冲突检测：**
- 自动检测同一依赖的不同版本冲突
- 提供详细的冲突报告
- 支持通过排除依赖表解决冲突

#### 5. 缓存机制

**缓存目录：** `~/.kb-cache/`

**结构：**
```
.kb-cache/
├── LibraryName/
│   ├── 1.0.0.tar.gz
│   └── 1.2.0.tar.gz
└── AnotherLib/
    └── 2.0.0.tar.gz
```

**操作：**
- 查看缓存信息：`kb cache info`
- 列出缓存：`kb cache list`
- 清理缓存：`kb cache clean [target]`

#### 6. 打包和发布

**打包格式：** tar.gz

**发布目录：** `publish/`

**内容：**
- 知识库源代码（`src/` 目录）
- Knowledge.md 元数据文件
- 可选的其他文件（根据 `.kb-package.yml` 配置）

**发布方式：**
- 上传到 Git 仓库 releases
- 提供下载 URL 供其他项目使用

## 工作流程

### 阶段工作流程

#### 阶段 1：创建知识库项目

**使用场景：** 开始一个新的知识库项目

**工作步骤：**
1. 询问用户项目基本信息
   - 知识库名称
   - 初始版本号（建议 0.1.0）
   - 知识库类型
   - 职责描述

2. 询问是否添加依赖
   - 如是，收集依赖信息（名称、版本、Git 地址）

3. 选择模板
   - 空模板：只生成目录结构
   - 最小模板：生成目录结构 + 最小 Knowledge.md
   - 完整模板：生成目录结构 + 完整 Knowledge.md + README.md

4. 生成目录结构
   - 创建 `src/` 目录
   - 创建 `Knowledge.md` 文件
   - 可选：创建 `tests/`、`README.md` 等

5. 询问是否初始化依赖
   - 如是，调用 `kb init` 下载依赖

**CLI 命令：**
- 如果实现了 `kb create --interactive`：调用交互式创建命令
- 如果实现了 `kb create --template [type]`：调用模板创建命令
- 否则：手动生成文件，然后调用 `kb init`

---

#### 阶段 2：开发知识库

**使用场景：** 添加功能、修改代码、更新依赖

**工作步骤：**
1. 根据具体任务选择子流程
2. 修改源代码
3. 如有依赖变化，更新 Knowledge.md
4. 运行测试验证功能
5. 如需要，调用 `kb init` 重新初始化依赖

**CLI 命令：**
- 检查依赖更新：`kb check-updates`
- 更新依赖：`kb update [name]`
- 缓存管理：`kb cache info/list/clean`

---

#### 阶段 3：打包知识库

**使用场景：** 准备发布知识库版本

**工作步骤：**
1. 验证 Knowledge.md 的完整性和正确性
2. 更新版本号（如需要）
3. 运行所有测试
4. 调用 `kb package` 打包

**CLI 命令：**
- 打包：`kb package --output [path]`

---

#### 阶段 4：发布知识库

**使用场景：** 发布知识库供其他项目使用

**工作步骤：**
1. 确认包文件已生成（在 `publish/` 目录）
2. 将包文件上传到仓库
   - GitHub Releases
   - GitLab Packages
   - 或其他托管平台
3. 更新 README 或文档说明如何使用
4. 通知依赖此知识库的项目

**注意：** 此步骤目前无 CLI 支持，需要智能体指导用户手动操作

---

### 常见任务工作流程

#### 任务 A：添加新依赖

**使用场景：** 知识库需要依赖另一个知识库

**工作步骤：**
1. 询问依赖信息
   - 知识库名称
   - 版本号（建议使用精确版本）
   - Git 仓库地址

2. 更新 Knowledge.md 的依赖表
   - 添加一行到依赖表格

3. 检查是否存在版本冲突
   - 如有冲突，询问解决方案：
     - 更新依赖版本
     - 使用排除依赖表
     - 修改依赖的依赖

4. 调用 `kb init` 下载依赖
   - 等待下载完成
   - 查看是否有错误

5. 验证依赖已正确安装
   - 检查 `deps/` 目录结构
   - 确认依赖的代码存在

---

#### 任务 B：更新知识库版本

**使用场景：** 发布新版本的知识库

**工作步骤：**
1. 确定新版本号
   - 根据变更类型选择：
     - 不兼容变更：主版本 + 1
     - 新功能：次版本 + 1
     - bug 修复：修订版本 + 1

2. 更新 Knowledge.md 中的版本号
   - 修改基本信息章节的版本字段

3. 更新 CHANGELOG 或相关文档
   - 记录本次变更的内容

4. 运行测试验证
   - 执行所有测试用例
   - 确保测试通过

5. 调用 `kb package` 打包
   - 生成新的发布包

---

#### 任务 C：修复依赖冲突

**使用场景：** 依赖之间存在版本冲突

**工作步骤：**
1. 识别冲突的依赖和版本
   - 查看 `kb init` 的错误消息
   - 或使用 `kb check-updates` 分析

2. 评估解决方案
   - 更新依赖版本到兼容版本
   - 使用排除依赖表排除冲突版本
   - 修改依赖的依赖声明

3. 更新 Knowledge.md
   - 修改依赖表或排除依赖表

4. 调用 `kb init` 重新初始化
   - 查看冲突是否已解决

5. 验证冲突已解决
   - 检查 `deps/` 目录
   - 确认依赖版本正确

---

#### 任务 D：清理缓存

**使用场景：** 清理不需要的缓存文件

**工作步骤：**
1. 询问清理范围
   - 全部缓存
   - 特定库
   - 特定版本

2. 如清理特定库或版本，先查看缓存
   - 调用 `kb cache list`
   - 确认要清理的目标

3. 调用 `kb cache clean [target]`
   - 全部：`kb cache clean all`
   - 特定库：`kb cache clean library-name`
   - 特定版本：`kb cache clean library-name:version`

4. 验证缓存已清理
   - 调用 `kb cache info` 查看

---

## 技术规范

### 目录结构

**标准知识库项目结构：**

```
knowledge-base/
├── src/                    # 源代码目录（必需）
│   ├── Knowledge.md         # 知识库元数据（必需）
│   ├── ...                 # 其他源代码文件
├── deps/                   # 依赖目录（由 kb init 创建）
│   ├── DependencyName/
│   │   └── ...            # 依赖的源代码
├── tests/                  # 测试目录（推荐）
│   └── ...
├── publish/                # 发布包目录（由 kb package 创建）
│   ├── Name-Version.tar.gz  # 发布包文件
├── README.md               # 项目说明（推荐）
└── .kb-package.yml         # 打包配置（可选）
```

**目录说明：**
- `src/`：存放知识库源代码，包含 Knowledge.md
- `deps/`：存放依赖的知识库，由 kb init 自动创建
- `tests/`：存放测试代码
- `publish/`：存放发布包，由 kb package 自动创建
- `README.md`：项目说明文档
- `.kb-package.yml`：可选的打包配置文件

---

### Knowledge.md 文件格式

**完整示例：**

```markdown
# 知识库名称

## 基本信息

- **名称**: ExampleLib
- **版本**: 1.2.0
- **类型**: library/domain/...
- **职责描述**: 此知识库封装了示例领域的核心背景知识，提供基础数据模型和工具函数

## 功能概述

（可选）简要描述知识库提供的功能和特性

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.2.0 | https://github.com/example/common-data-types |
| UtilsLib | ^2.1.0 | https://github.com/example/utils-lib |
| SpecificModule | ~3.0.5 | https://github.com/example/specific-module |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| OldParser | 1.0.0 | 与其他依赖冲突 |

## 其他内容

（可选）其他文档内容，如 API 说明、使用示例等
```

**格式规则：**
1. 必须包含 `基本信息` 章节
2. `基本信息` 章节必须包含：
   - 名称：知识库的名称
   - 版本：语义化版本号
   - 类型：知识库类型（如 library、domain 等）
   - 职责描述：简要说明知识库的用途
3. `依赖` 和 `排除依赖` 使用 Markdown 表格格式
4. 依赖表头固定：知识库名称、版本号、Git地址
5. 排除依赖表头固定：知识库名称、版本号、原因

**注意事项：**
- 使用 UTF-8 编码
- 表格必须使用标准 Markdown 语法
- 表头必须与示例完全一致（中文）

---

### CLI 命令参考

#### kb init [目录名]

**用途：** 初始化知识库项目，自动下载所有依赖

**选项：**
- `--path`：指定知识库文件路径（默认 src/Knowledge.md）

**行为：**
1. 解析 Knowledge.md 文件
2. 检测版本冲突
3. 下载指定的依赖包
4. 解压到 `deps/` 目录

**示例：**
```bash
kb init
kb init --path custom/path/Knowledge.md
```

---

#### kb package

**用途：** 打包知识库为发布格式

**选项：**
- `--output`：指定输出路径（默认 publish/）

**行为：**
1. 验证知识库文件存在
2. 读取 Knowledge.md 获取名称和版本
3. 创建 tar.gz 格式的发布包
4. 保存到 publish/ 目录或指定路径

**示例：**
```bash
kb package
kb package --output /path/to/output
```

---

#### kb check-updates

**用途：** 检查依赖项是否有可用更新

**行为：**
1. 扫描当前知识库的所有依赖项
2. 查询远程仓库的最新版本
3. 显示有更新可用的依赖项列表
4. 显示当前版本和最新版本

**示例：**
```bash
kb check-updates
```

---

#### kb update [依赖名称]

**用途：** 更新依赖项到最新版本

**参数：**
- `[依赖名称]`：可选，指定要更新的依赖名称

**行为：**
1. 如指定依赖名称，只更新该依赖
2. 如未指定，更新所有依赖
3. 下载最新版本的依赖项
4. 更新 `deps/` 目录中的依赖项
5. 自动处理版本冲突

**示例：**
```bash
kb update                # 更新所有依赖
kb update CommonLib     # 更新特定依赖
```

---

#### kb cache info

**用途：** 显示缓存信息

**行为：**
- 显示缓存目录路径
- 显示总大小
- 显示库数量
- 显示版本数量

**示例：**
```bash
kb cache info
```

---

#### kb cache list

**用途：** 列出所有缓存的库

**行为：**
- 显示所有缓存的库的名称
- 显示每个库的版本
- 显示每个版本的大小

**示例：**
```bash
kb cache list
```

---

#### kb cache clean [TARGET]

**用途：** 清理缓存

**参数：**
- `all`：清理所有缓存
- `library-name`：清理指定库的所有版本
- `library-name:version`：清理指定库的指定版本

**行为：**
- 执行前会要求确认
- 删除对应的缓存文件
- 如目录为空，自动删除目录

**示例：**
```bash
kb cache clean all                  # 清理所有缓存
kb cache clean CommonLib            # 清理 CommonLib 的所有版本
kb cache clean CommonLib:1.0.0      # 清理 CommonLib 的 1.0.0 版本
```

---

### Python API 参考

**注意：** 智能体优先使用 CLI 命令，仅在 CLI 无法满足需求时使用 Python API。

#### 核心模块

```python
from kb.core import KnowledgeParser, KnowledgeValidator

# 解析 Knowledge.md
parser = KnowledgeParser()
metadata = parser.parse(Path("src/Knowledge.md"))

# 获取元数据
name = metadata.name
version = metadata.version
kb_type = metadata.type
description = metadata.description
dependencies = metadata.dependencies
excluded = metadata.excluded_dependencies

# 验证版本号
validator = KnowledgeValidator()
is_valid = validator.validate_version("1.2.0")
```

#### 依赖管理

```python
from kb.dependency import DependencyDownloader, DependencyResolver, ConflictDetector

# 下载依赖
downloader = DependencyDownloader()
downloader.download(Path("src/Knowledge.md"), Path("deps"))

# 解析依赖
resolver = DependencyResolver()
deps = resolver.resolve(Path("src/Knowledge.md"))

# 检测冲突
detector = ConflictDetector()
conflicts = detector.detect(Path("src/Knowledge.md"))
```

#### 缓存管理

```python
from kb.cache import CacheManager

# 获取缓存信息
cache = CacheManager()
info = cache.get_info()

# 列出缓存
libraries = cache.list()

# 清理缓存
cache.clean_all()
cache.clean_library("CommonLib")
cache.clean_version("CommonLib", "1.0.0")
```

#### 更新检查

```python
from kb.update import VersionChecker, DependencyUpdater

# 检查更新
checker = VersionChecker()
updates = checker.check_updates(Path("src/Knowledge.md"))

# 更新依赖
updater = DependencyUpdater()
updater.update(Path("src/Knowledge.md"), "CommonLib")
```

---

## 最佳实践

### 版本管理

1. **遵循语义化版本规范**
   - 主版本号变更表示不兼容的 API 变更
   - 次版本号变更表示向后兼容的功能新增
   - 修订版本号变更表示向后兼容的 bug 修复

2. **发布前测试**
   - 确保所有测试通过
   - 测试依赖兼容性
   - 验证版本号正确

3. **保留发布历史**
   - 保留每个版本的发布包
   - 记录版本变更日志
   - 便于回滚和问题追踪

---

### 依赖管理

1. **使用精确版本号**
   - 尽量使用精确版本（`1.2.0`）而非范围（`^1.2.0`）
   - 避免意外的依赖更新
   - 提高可复现性

2. **定期检查更新**
   - 定期使用 `kb check-updates` 检查依赖更新
   - 评估更新的影响和兼容性
   - 及时更新以获取安全修复和新功能

3. **谨慎处理冲突**
   - 使用排除依赖表明确排除冲突版本
   - 文档化排除原因
   - 寻找长期解决方案而非临时排除

---

### 项目结构

1. **保持目录清晰**
   - 将业务逻辑放在 `src/` 目录下
   - 使用 `tests/` 目录存放测试
   - 使用 `docs/` 目录存放文档

2. **维护 Knowledge.md**
   - 保持 `Knowledge.md` 的简洁和准确
   - 及时更新版本号和依赖信息
   - 定期审查依赖表

3. **编写文档**
   - 为知识库编写 README.md
   - 说明如何使用此知识库
   - 提供示例代码

4. **编写测试**
   - 为知识库编写测试（`tests/` 目录）
   - 确保测试覆盖核心功能
   - 运行 `kb package` 前先运行测试

---

### 开发流程

1. **规划优先**
   - 开发新功能前先规划设计
   - 确定依赖需求
   - 考虑版本兼容性

2. **小步迭代**
   - 修改依赖后立即测试
   - 定期运行完整测试套件
   - 使用 `kb init` 验证依赖配置

3. **版本控制**
   - 使用 Git 跟踪变更
   - 为重要功能创建分支
   - 发布前打 tag

4. **打包前验证**
   - 运行完整测试套件
   - 验证 Knowledge.md 完整性
   - 检查依赖是否正确

---

### 缓存管理

1. **定期清理**
   - 定期清理不需要的缓存
   - 使用 `kb cache clean library-name` 清理特定库
   - 避免缓存占用过多磁盘空间

2. **故障排查**
   - 遇到下载问题时尝试清理缓存
   - 使用 `kb cache info` 查看缓存状态
   - 检查缓存目录权限

3. **监控缓存**
   - 使用 `kb cache info` 监控缓存大小
   - 查看缓存的库和版本数量
   - 及时清理过期的缓存

---

## 常见陷阱

### 陷阱 1：Knowledge.md 格式错误

**症状：**
- `kb init` 报错无法解析
- 依赖未正确识别

**原因：**
- 表头格式不正确（缺少列名、列名顺序错误）
- 表格语法错误（缺少分隔符）
- 字符编码问题（非 UTF-8）

**解决方案：**
- 参考 Knowledge.md 模板检查格式
- 确保使用标准 Markdown 表格语法
- 使用 UTF-8 编码保存文件

---

### 陷阱 2：版本冲突

**症状：**
- `kb init` 报错提示版本冲突
- `deps/` 目录中的依赖版本不正确

**原因：**
- 不同依赖声明了同一库的不同版本
- 依赖的依赖之间存在冲突

**解决方案：**
- 使用 `kb check-updates` 查看依赖关系
- 在 `排除依赖` 表中排除冲突的版本
- 升级或降级依赖到兼容版本
- 使用版本范围约束（`^1.2.0`）允许自动选择兼容版本

---

### 陷阱 3：缓存问题

**症状：**
- 依赖下载失败但网络正常
- 新版本未生效

**原因：**
- 缓存文件损坏
- 缓存目录权限问题
- 旧版本缓存阻止新版本下载

**解决方案：**
- 运行 `kb cache clean all` 清理全部缓存
- 检查 `~/.kb-cache/` 目录权限
- 使用 `kb cache list` 查看缓存的库和版本
- 手动删除特定库的缓存：`kb cache clean library-name`

---

### 陷阱 4：打包失败

**症状：**
- `kb package` 报错
- 生成的包文件不完整

**原因：**
- `src/` 目录不存在
- `Knowledge.md` 缺失或格式错误
- 缺少必要文件（如 `.kb-package.yml`）

**解决方案：**
- 确保在知识库根目录运行 `kb package`
- 验证 `src/Knowledge.md` 存在且格式正确
- 如使用打包配置，确保 `.kb-package.yml` 存在
- 运行 `kb --help` 查看命令详情

---

### 陷阱 5：依赖路径问题

**症状：**
- 代码中无法导入依赖
- 运行时提示模块未找到

**原因：**
- `deps/` 目录未正确创建
- Python 路径未包含 `deps/` 目录
- 依赖的目录结构与预期不符

**解决方案：**
- 确保运行 `kb init` 初始化依赖
- 在代码中添加 `deps/` 到 Python 路径
- 检查 `deps/` 目录结构是否正确

---

## 故障排除清单

遇到问题时按以下顺序检查：

### 1. 检查命令语法
- 运行 `kb --help` 和 `kb <command> --help`
- 确认选项和参数格式正确

### 2. 检查文件结构
- 确保在正确的目录运行命令
- 验证 `src/Knowledge.md` 存在
- 检查 `deps/`、`publish/` 目录权限

### 3. 检查依赖状态
- 运行 `kb check-updates` 查看依赖
- 使用 `kb cache info` 检查缓存
- 查看是否有版本冲突

### 4. 清理缓存
- 运行 `kb cache clean all`
- 重新运行 `kb init`

### 5. 查看详细日志
- 使用 `-v` 或 `--verbose` 选项获取更多信息
- 检查错误消息的具体内容

### 6. 查阅文档
- 阅读项目 README.md
- 查看相关测试代码了解用法

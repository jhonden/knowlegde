# Knowledge Base Development

帮助用户创建、开发、打包和发布知识库项目的完整工作流程。

## 适用场景

当涉及知识库项目的以下操作时使用此Skill：
- 创建新的知识库项目
- 开发和维护知识库（添加功能、修改代码、更新依赖）
- 打包和发布知识库
- 管理知识库依赖和缓存

## 触发条件

- 1%+ 的可能性 → 必须使用此Skill
- 提及"知识库"、"Knowledge.md"、"kb命令"、"依赖管理"、"打包发布"等关键词时使用

## Skill内容

1. 概念说明 - 知识库系统的核心概念
2. 工作流程 - 阶段流程和任务流程
3. 技术规范 - 目录结构、文件格式、命令参考
4. 最佳实践 - 版本管理、依赖管理等
5. 常见陷阱 - 故障排除指南

## 使用优先级

**必须使用此Skill的场景：**
- 创建知识库项目
- 开发知识库功能
- 打包发布知识库
- 管理知识库依赖

**优先通过CLI操作：**
- 尽量使用kb CLI命令执行操作
- CLI无法满足需求时，使用Python API或自主决策

## 概念说明

### 知识库（Knowledge Base）

封装模块/领域核心背景知识的可复用单元。

**特性：**
- 包含元数据、源代码、依赖关系
- 支持版本管理、依赖管理、打包发布
- 可被其他知识库依赖

### Knowledge.md

知识库的元数据文件，位于src/目录下，使用Markdown格式。

### 语义化版本号

格式：主版本.次版本.修订版本（如1.0.0）
- 主版本（MAJOR）：不兼容的API变更
- 次版本（MINOR）：向后兼容的功能新增
- 修订版本（PATCH）：向后兼容的bug修复

版本范围支持：
- 精确版本：`1.0.0`
- 兼容版本：`^1.0.0`（>= 1.0.0 且 < 2.0.0）
- 补丁版本：`~2.1.0`（>= 2.1.0 且 < 2.2.0）

### 依赖管理

通过Knowledge.md声明依赖，kb init自动下载到deps/目录。

### 缓存机制

缓存目录：`~/.kb-cache/`
- kb cache info - 查看缓存信息
- kb cache list - 列出缓存
- kb cache clean - 清理缓存

### 打包和发布

打包格式：tar.gz
- kb package - 打包知识库
- 发布到publish/目录或指定路径

## 工作流程

### 阶段1：创建知识库项目

**适用场景：** 开始新的知识库项目

**步骤：**
1. 询问项目基本信息（名称、版本、类型、职责描述）
2. 询问是否添加依赖（如需添加，收集名称、版本、Git地址）
3. 选择模板（空模板/最小模板/完整模板）
4. 生成目录结构（src/和Knowledge.md）
5. 询问是否初始化依赖（调用kb init）

**CLI命令：**
```bash
kb init                    # 初始化依赖
kb create --interactive     # 交互式创建（如实现）
kb create --template [type]  # 模板创建（如实现）
```

### 阶段2：开发知识库

**适用场景：** 添加功能、修改代码、更新依赖

**步骤：**
1. 根据任务选择子流程
2. 修改源代码
3. 更新Knowledge.md（如依赖变化）
4. 运行测试验证
5. 调用kb init重新初始化（如需要）

**CLI命令：**
```bash
kb check-updates     # 检查依赖更新
kb update [name]      # 更新依赖
kb cache info/list/clean  # 缓存管理
```

### 阶段3：打包知识库

**适用场景：** 准备发布知识库版本

**步骤：**
1. 验证Knowledge.md完整性和正确性
2. 更新版本号（如需要）
3. 运行所有测试
4. 调用kb package打包

**CLI命令：**
```bash
kb package --output [path]  # 打包知识库
```

### 阶段4：发布知识库

**适用场景：** 发布知识库供其他项目使用

**步骤：**
1. 确认包文件已生成（publish/目录）
2. 上传到仓库（GitHub/GitLab releases等）
3. 更新README或文档
4. 通知依赖此知识库的项目

**注意：** 此步骤无CLI支持，需手动操作

### 任务A：添加新依赖

**步骤：**
1. 询问依赖信息（名称、版本、Git地址）
2. 更新Knowledge.md的依赖表
3. 检查版本冲突
4. 调用kb init下载依赖
5. 验证deps/目录

### 任务B：更新知识库版本

**步骤：**
1. 确定新版本号（遵循语义化版本）
2. 更新Knowledge.md中的版本号
3. 更新CHANGELOG
4. 运行测试
5. 调用kb package打包

### 任务C：修复依赖冲突

**步骤：**
1. 识别冲突的依赖和版本
2. 评估解决方案（更新版本、排除依赖、修改依赖）
3. 更新Knowledge.md
4. 调用kb init重新初始化
5. 验证冲突已解决

### 任务D：清理缓存

**步骤：**
1. 询问清理范围（全部/特定库/特定版本）
2. 调用kb cache clean [target]
3. 验证缓存已清理

## 技术规范

### 目录结构

```
knowledge-base/
├── src/                    # 源代码目录（必需）
│   ├── Knowledge.md         # 知识库元数据（必需）
│   └── ...
├── deps/                   # 依赖目录（kb init创建）
│   └── DependencyName/
├── tests/                  # 测试目录（推荐）
├── publish/                # 发布包目录（kb package创建）
│   └── Name-Version.tar.gz
└── README.md               # 项目说明（推荐）
```

### Knowledge.md格式

```markdown
# 知识库名称

## 基本信息

- **名称**: ExampleLib
- **版本**: 1.2.0
- **类型**: library/domain/...
- **职责描述**: 描述知识库的用途

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.2.0 | https://github.com/example/common-data-types |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| OldParser | 1.0.0 | 与其他依赖冲突 |
```

**格式规则：**
- 必须包含基本信息章节（名称、版本、类型、职责描述）
- 依赖和排除依赖使用Markdown表格
- 表头必须与示例一致

### CLI命令参考

#### kb init [目录名]
初始化知识库项目，自动下载所有依赖。

**选项：**
- `--path` 指定知识库文件路径

```bash
kb init
kb init --path custom/path/Knowledge.md
```

#### kb package
打包知识库为发布格式。

**选项：**
- `--output` 指定输出路径

```bash
kb package
kb package --output /path/to/output
```

#### kb check-updates
检查依赖项是否有可用更新。

```bash
kb check-updates
```

#### kb update [依赖名称]
更新依赖项到最新版本。

```bash
kb update                # 更新所有依赖
kb update CommonLib     # 更新特定依赖
```

#### kb cache info
显示缓存信息（目录、大小、库数量）。

```bash
kb cache info
```

#### kb cache list
列出所有缓存的库。

```bash
kb cache list
```

#### kb cache clean [TARGET]
清理缓存。

```bash
kb cache clean all                  # 清理所有
kb cache clean library-name            # 清理特定库
kb cache clean library-name:version      # 清理特定版本
```

### Python API参考

**注意：** 优先使用CLI命令，CLI无法满足时使用Python API。

```python
from kb.core import KnowledgeParser
from kb.dependency import DependencyDownloader
from kb.cache import CacheManager

# 解析Knowledge.md
parser = KnowledgeParser()
metadata = parser.parse(Path("src/Knowledge.md"))

# 下载依赖
downloader = DependencyDownloader()
downloader.download(Path("src/Knowledge.md"), Path("deps"))

# 缓存管理
cache = CacheManager()
info = cache.get_info()
cache.clean_all()
```

# 知识库命令行工具 (Knowledge Base CLI Tool)

一个基于Python的强大命令行工具，用于管理和组织您的知识库。

## 安装 (Installation)

### 环境要求
- Python 3.8+
- pip

### 安装步骤

1. 克隆仓库：
```bash
git clone <repository-url>
cd knowlegde
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 快速开始 (Quick Start)

### 初始化知识库

创建一个新的知识库项目：

```bash
kb init my-knowledge-base
```

这将创建一个包含标准目录结构的知识库项目，并自动下载所有依赖项。

#### 依赖管理

知识库系统支持完整的依赖管理功能：

##### 依赖表格式示例

在 `Knowledge.md` 文件中声明依赖：

```markdown
## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonLib | 1.0.0 | https://github.com/example/common-lib |
| UtilsLib | ^2.1.0 | https://github.com/example/utils-lib |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| OldLib | 1.0.0 | 已过时 |
```

##### 自动下载依赖

`kb init` 命令会自动：
- 解析 `Knowledge.md` 中的依赖声明
- 检测并解决版本冲突
- 下载指定的知识库包
- 解压到 `deps/` 目录

##### 版本冲突处理

系统会自动检测同一依赖的不同版本冲突，并提供详细的冲突报告。如果检测到冲突，会显示冲突的依赖名称、版本列表和冲突原因。

##### 排除依赖功能

可以在 `Knowledge.md` 中使用"排除依赖"表格来明确排除某些依赖项，避免版本冲突。

##### 版本号格式支持

- **精确版本**: `1.0.0`
- **版本范围**: `^1.0.0` (兼容版本), `~2.1.0` (补丁版本)
- **预发布版本**: `1.0.0-alpha.1`

##### 自动依赖更新

知识库系统支持自动检测和更新依赖项：

- 使用 `kb check-updates` 命令检查所有依赖项是否有新版本可用
- 使用 `kb update` 命令更新依赖项到最新版本
- 系统会自动处理版本冲突和依赖关系
- 支持批量更新和单个依赖更新

### 检查依赖更新

检查知识库依赖项是否有可用更新：

```bash
kb check-updates
```

这将扫描当前知识库的所有依赖项，并显示哪些依赖项有新版本可用。

### 更新依赖

更新知识库的依赖项到最新版本：

```bash
kb update [依赖名称]
```

不带参数时，更新所有依赖项到最新版本。指定依赖名称时，只更新指定的依赖项。

### 打包知识库

将知识库打包为发布格式：

```bash
kb package
```

这将验证知识库并生成最终的包文件。

## 命令列表 (Command List)

| 命令 | 描述 | 选项 |
|------|------|------|
| `kb init [目录名]` | 初始化知识库项目，自动下载所有依赖 | `--path` 指定知识库文件路径 |
| `kb package` | 打包知识库为发布格式 | `--output` 指定输出路径 |
| `kb check-updates` | 检查依赖项是否有可用更新 | - |
| `kb update [依赖名称]` | 更新依赖项到最新版本 | - |
| `kb cache info` | 显示缓存信息 | - |
| `kb cache list` | 列出所有缓存的库 | - |
| `kb cache clean [TARGET]` | 清理缓存，TARGET 可为 'all'、'library:name' 或 'library:version' | - |
| `kb --version` | 显示版本信息 | - |
| `kb --help` | 显示帮助信息 | - |

## 开发和测试 (Development and Testing)

### 运行测试

执行所有测试：

```bash
pytest tests/ -v
```

### 运行带覆盖率的测试

执行测试并生成覆盖率报告：

```bash
pytest tests/ -v --cov=kb --cov-report=html
```

覆盖率报告将生成在 `htmlcov/` 目录中。

### 缓存管理 (Cache Management)

知识库工具提供完整的缓存管理功能，可以查看、列出和清理缓存的库。

#### 缓存命令使用说明

1. **查看缓存信息**

   ```bash
   kb cache info
   ```

   显示缓存目录路径、总大小、库数量和版本数量等信息。

2. **列出所有缓存的库**

   ```bash
   kb cache list
   ```

   显示所有缓存的库的名称、版本和大小信息。

3. **清理缓存**

   ```bash
   # 清理所有缓存
   kb cache clean all

   # 清理特定库的所有版本
   kb cache clean library-name

   # 清理特定库的特定版本
   kb cache clean library-name:version
   ```

   执行清理操作时会要求确认，避免误删。

### 依赖更新功能 (Dependency Updates)

知识库工具提供完整的依赖管理功能，包括检查和更新依赖项。

#### 检查依赖更新

使用 `kb check-updates` 命令检查所有依赖项是否有新版本可用：

```bash
kb check-updates
```

该命令会：
- 扫描当前知识库的所有依赖项
- 查询远程仓库的最新版本
- 显示有更新可用的依赖项列表
- 显示当前版本和最新版本

#### 更新依赖项

使用 `kb update` 命令更新依赖项：

```bash
# 更新所有依赖项
kb update

# 更新特定依赖项
kb update CommonLib
```

该命令会：
- 下载最新版本的依赖项
- 自动处理版本冲突
- 更新 `deps/` 目录中的依赖项
- 保留版本缓存以便将来使用

#### 更新工作流程

推荐的依赖更新工作流程：

1. 使用 `kb check-updates` 查看可用的更新
2. 评估更新的影响和兼容性
3. 使用 `kb update` 更新依赖项
4. 运行测试确保功能正常
5. 使用 `kb package` 打包发布

### 测试结构

```
tests/
├── __init__.py
├── cli/
│   ├── test_init.py      # init命令测试
│   ├── test_package.py    # package命令测试
│   ├── test_main.py       # 主CLI测试
│   ├── test_cache.py     # cache命令测试
│   ├── test_update.py    # update命令测试
│   └── test_integration.py # 集成测试
└── core/
    ├── test_parser.py     # 解析器测试
    ├── test_validator.py  # 验证器测试
    └── test_models.py     # 模型测试
```

## 项目结构 (Project Structure)

```
knowlegde/
├── kb/
│   ├── __init__.py          # 包初始化
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py          # 主CLI入口
│   │   ├── init.py          # init命令
│   │   ├── package.py       # package命令
│   │   ├── cache.py         # cache命令
│   │   ├── update.py        # update命令
│   │   └── utils.py         # CLI工具函数
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py        # 数据模型
│   │   ├── parser.py        # 解析器
│   │   └── validator.py     # 验证器
│   ├── update/
│   │   ├── __init__.py
│   │   ├── checker.py       # 依赖检查器
│   │   ├── updater.py       # 依赖更新器
│   │   └── models.py        # 更新数据模型
│   ├── cache/
│   │   ├── __init__.py
│   │   └── manager.py       # 缓存管理器
│   └── exceptions.py        # 自定义异常
├── tests/                   # 测试文件
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明
```

## 贡献指南 (Contributing)

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证 (License)

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 版本历史 (Version History)

- 0.1.0 - 初始版本
  - 实现 init 和 package 命令
  - 基础验证和解析功能
  - 完整的测试套件

## Claude Code Skill

项目包含知识库开发Skill，用于辅助Claude智能体进行知识库项目的全流程开发。

### 使用方式

```bash
# 将Skill文件复制到Claude Code的Skills目录
cp .skills/knowledge-base-development.md ~/.claude/skills/

# 或在Claude Code中启用自定义Skills目录
# 设置 -> Skills -> Add Skills Directory
# 选择项目根目录
```

### Skill功能

- 指导创建知识库项目
- 指导开发知识库功能
- 指导打包和发布知识库
- 提供故障排除指南

### Skill内容概览

该Skill包含以下内容：

1. **概念说明** - 知识库系统的6个核心概念
   - 知识库（Knowledge Base）
   - Knowledge.md
   - 语义化版本号
   - 依赖管理
   - 缓存机制
   - 打包和发布

2. **工作流程** - 完整的开发流程
   - 4个阶段：创建、开发、打包、发布
   - 4个任务：添加依赖、更新版本、修复冲突、清理缓存

3. **技术规范** - 详细的技术文档
   - 目录结构说明
   - Knowledge.md文件格式
   - CLI命令参考
   - Python API参考

4. **最佳实践** - 开发建议
   - 版本管理
   - 依赖管理
   - 项目结构
   - 开发流程
   - 缓存管理

5. **常见陷阱** - 故障排除指南
   - 5个常见陷阱及解决方案
   - 完整的故障排除清单
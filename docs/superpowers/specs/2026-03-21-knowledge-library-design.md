# 知识库系统设计文档

## 1. 概述

### 1.1 设计目标

知识库系统旨在解决AI Agent在需求分析设计领域缺乏背景知识的问题。通过封装领域核心知识，支持版本管理和发布机制，让AI能够快速获取所需背景知识，提升协作效率。

### 1.2 核心概念

**知识库**：封装某个模块或领域的核心背景知识和业务知识的单元，可按版本管理、发布、被依赖。

**设计空间**：基于知识库构建的协作工作环境，包含本空间背景知识、依赖知识库、记忆知识、AI角色认知等。

**渐进式披露**：AI先加载知识库的核心元数据（Knowledge.md），根据用户意图按需加载详细内容，避免上下文撑爆。

## 2. 知识库结构

### 2.1 仓库目录结构

```
my-knowledge-lib/
├── src/                           # 知识库源码目录（发布内容）
│   ├── Knowledge.md               # 核心元数据文件
│   ├── overview.md                # 概览文档
│   ├── structure/                 # 结构化知识
│   │   ├── file-format.md
│   │   └── field-specs.md
│   └── examples/                  # 示例文档
│       ├── basic.md
│       └── advanced.md
├── publish/                       # 发布目录（约定）
│   └── my-knowledge-lib-1.2.0.tar.gz   # 发布包
├── deps/                          # 依赖目录（不提交到git）
│   ├── knowledge-lib-b-1.2.0/
│   └── knowledge-lib-c-2.0.0/
├── .kb-package.yml                # 打包配置文件（不发布）
└── .gitignore                     # 包含 deps/
```

### 2.2 目录说明

- **src/**：知识库的所有源文件，会被打包发布
- **publish/**：发布包存放目录，约定名称
- **deps/**：依赖知识库的解压目录，不提交到git
- **.kb-package.yml**：打包策略配置，不发布
- **.gitignore**：必须包含 `deps/`，避免提交依赖

## 3. Knowledge.md 元数据规范

### 3.1 格式

采用 **Markdown标题+列表格式**，易于阅读和解析。

### 3.2 内容结构

```markdown
# [知识库名称] 知识库

## 基本信息

- **名称**: [库名称]
- **版本**: [主版本.次版本.修订版本]
- **类型**: [用户自定义类型]
- **职责描述**: [一句话概括知识库的核心职责]

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| [知识库名称] | [版本号] | [git仓库地址] |
| [知识库名称] | [版本号] | [git仓库地址] |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| [知识库名称] | [版本号] | [排除原因] |

## 适用场景

[使用场景关键词列表，或具体场景描述]

## 对外能力

- [能力描述1]
- [能力描述2]

## 文件路径图谱

```
[树状目录结构]
├── [文件路径] [功能职责]
├── [目录路径]
│   ├── [文件路径] [功能职责]
│   └── [文件路径] [功能职责]
└── ...
```
```

### 3.3 示例

```markdown
# FileFormatParser 知识库

## 基本信息

- **名称**: FileFormatParser
- **版本**: 1.2.0
- **类型**: structure-knowledge
- **职责描述**: 封装特定文件格式的解析知识，包括文件结构、字段定义和解析规则

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.2.0 | https://github.com/example/common-data-types |

## 适用场景

- 文件格式解析
- 数据结构设计
- 字段定义参考

## 对外能力

- 提供文件格式规范
- 定义字段结构和类型
- 解析规则说明
- 示例代码参考

## 文件路径图谱

```
src/
├── Knowledge.md [核心元数据，AI首先加载]
├── overview.md [整体架构概览，首次加载时参考]
├── structure/ [结构定义，解析数据时参考]
│   ├── file-format.md [文件格式规范]
│   └── field-specs.md [字段详细规范]
└── examples/ [使用示例，具体实现时参考]
    ├── basic.md [基础示例]
    └── advanced.md [高级示例]
```
```

## 4. 打包配置规范

### 4.1 配置文件位置

`.kb-package.yml`，位于仓库根目录。

### 4.2 配置文件格式（YAML）

```yaml
# 默认包含 src/ 目录下所有文件
# 通过 include_extra 和 exclude 进行调整

# 额外包含的路径（相对于仓库根目录）
include_extra:
  - "docs/examples/**"           # 包含文档示例
  - "templates/**"                # 包含模板

# 排除的路径（相对于仓库根目录）
exclude:
  - "src/draft/**"                # 排除草稿目录
  - "**/*-draft.md"               # 排除草稿文件
  - "**/*-test.md"                # 排除测试文件
  - "**/.gitignore"
  - "**/.DS_Store"
```

### 4.3 打包规则

1. **默认行为**：包含 `src/` 目录下所有文件
2. **include_extra**：额外添加其他路径下的文件
3. **exclude**：排除指定的文件或目录
4. **exclude 优先级**：即使文件通过默认或 include_extra 包含，也会被 exclude 排除
5. **匹配规则**：支持 glob 模式（`**`、`*`、`?`）

### 4.4 示例

```yaml
# 文件格式解析知识库打包配置
include_extra:
  - "docs/examples/**"           # 包含文档示例

exclude:
  - "src/draft/**"                # 排除草稿目录
  - "**/*-draft.md"               # 排除草稿文件
```

## 5. 版本管理

### 5.1 版本号格式

采用 **语义化版本**：`主版本.次版本.修订版本`，如 `1.2.3`

- **主版本**：不兼容的 API 修改
- **次版本**：向下兼容的功能性新增
- **修订版本**：向下兼容的问题修正

### 5.2 版本声明

在 `Knowledge.md` 中声明当前版本：

```markdown
## 基本信息

- **名称**: FileFormatParser
- **版本**: 1.2.0
```

### 5.3 依赖版本声明

在依赖表中声明依赖的固定版本：

```markdown
## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.2.0 | https://github.com/example/common-data-types |
```

### 5.4 排除依赖

当需要排除某个依赖时（如解决版本冲突），在排除依赖表中声明：

```markdown
## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| CommonDataTypes | 1.2.0 | 与其他依赖冲突，使用ValidationRules依赖的1.3.0版本 |
```

### 5.5 版本冲突处理

当多个知识库依赖同一知识库的不同版本时：

- **检测到冲突**：报错，提示版本冲突
- **用户解决**：用户手动调整依赖版本，确保兼容

```bash
kb init
> 错误：版本冲突
>   - A 依赖 CommonDataTypes@1.2.0
>   - B 依赖 CommonDataTypes@1.3.0
> 请检查并调整依赖版本
```

## 6. 依赖管理

### 6.1 依赖存储

所有依赖知识库统一存储在当前知识库的 `deps/` 目录下：

```
my-knowledge-lib/
└── deps/
    ├── knowledge-lib-b-1.2.0/
    └── knowledge-lib-c-2.0.0/
```

### 6.2 依赖下载时机

初始化时一次性下载所有依赖：

```bash
kb init
```

### 6.3 依赖下载流程

```
1. 解析 Knowledge.md 中的依赖表

2. 检查全局缓存 ~/.kb-cache/
   - 如果缓存中存在对应版本，直接使用

3. 如果缓存不存在，从依赖知识库的 git 仓库下载
   - 下载地址：<git-repo>/publish/<name>-<version>.tar.gz
   - 保存到全局缓存

4. 从缓存解压到当前知识库的 deps/ 目录

5. 递归处理依赖的依赖

6. 完成初始化
```

### 6.4 依赖版本冲突

- 检测到多个知识库依赖同一知识库的不同版本时，报错
- 用户通过 `排除依赖` 表段手动排除冲突版本

## 7. 打包发布机制

### 7.1 打包命令

```bash
kb package
```

### 7.2 打包流程

```
1. 读取 .kb-package.yml 配置

2. 根据配置确定要打包的文件列表
   - 默认包含 src/ 下所有文件
   - 额外包含 include_extra 指定的路径
   - 排除 exclude 指定的路径

3. 创建发布包文件
   - 文件名：<知识库名称>-<版本号>.tar.gz
   - 例如：FileFormatParser-1.2.0.tar.gz

4. 将发布包保存到 publish/ 目录
   - publish/FileFormatParser-1.2.0.tar.gz
```

### 7.3 发布

发布包生成后，需要提交到 git 仓库：

```bash
git add publish/
git commit -m "发布版本 1.2.0"
git push
```

其他知识库即可通过 git 地址下载该发布包。

### 7.4 发布包内容

发布包内保持 src/ 目录结构：

```
FileFormatParser-1.2.0.tar.gz
├── Knowledge.md
├── overview.md
├── structure/
│   ├── file-format.md
│   └── field-specs.md
└── examples/
    ├── basic.md
    └── advanced.md
```

## 8. 初始化和加载流程

### 8.1 初始化命令

```bash
kb init
```

### 8.2 完整流程

```
1. 读取当前知识库的 Knowledge.md

2. 解析依赖表和排除依赖表，获取最终依赖列表

3. 检查全局缓存 ~/.kb-cache/
   对于每个依赖：

   a. 如果缓存中存在对应版本：
      - 直接使用缓存

   b. 如果缓存不存在：
      - 从依赖知识库的 git 仓库下载
      - 下载地址：<git-repo>/publish/<name>-<version>.tar.gz
      - 保存到全局缓存 ~/.kb-cache/<name>/<version>.tar.gz

4. 从缓存解压到当前知识库的 deps/ 目录
   - deps/<name>-<version>/

5. 递归处理依赖的依赖
   - 确保完整加载整个依赖树

6. 初始化完成
```

### 8.3 AI 加载流程

```
1. AI 首先读取 Knowledge.md（核心元数据）
   - 了解知识库的职责、能力、适用场景
   - 获取依赖列表和文件路径图谱

2. AI 根据用户意图判断是否需要加载详细内容
   - 如果需要，按文件路径图谱导航到相应文件
   - 采用渐进式披露策略，避免一次性加载过多内容

3. AI 在工作过程中可以随时访问已加载的依赖知识库
   - 通过 deps/ 目录访问依赖的知识库
```

## 9. 全局缓存机制

### 9.1 缓存目录结构

```
~/.kb-cache/
├── FileFormatParser/
│   ├── 1.0.0.tar.gz
│   ├── 1.1.0.tar.gz
│   └── 1.2.0.tar.gz
├── CommonDataTypes/
│   ├── 1.2.0.tar.gz
│   └── 1.3.0.tar.gz
└── ValidationRules/
    └── 2.0.0.tar.gz
```

### 9.2 缓存使用流程

```
1. 检查缓存：~/.kb-cache/<name>/<version>.tar.gz

2. 如果缓存存在：
   - 直接从缓存解压到 deps/

3. 如果缓存不存在：
   - 从 git 仓库下载
   - 保存到缓存
   - 然后从缓存解压到 deps/
```

### 9.3 缓存清理命令

```bash
kb cache clean              # 清理所有缓存
kb cache clean FileFormatParser     # 清理指定知识库的所有版本缓存
kb cache clean FileFormatParser:1.0.0    # 清理指定版本缓存
```

### 9.4 缓存优势

- **节省下载时间**：多个知识库共享同一个缓存的包文件
- **节省磁盘空间**：同一版本的发布包只存储一份
- **快速初始化**：已缓存的知识库可以立即使用

## 10. 依赖更新机制

### 10.1 检查更新

```bash
kb check-updates             # 检查所有依赖是否有新版本
kb check-updates CommonDataTypes      # 检查指定依赖
```

执行后显示可用更新：

```bash
kb check-updates
> 依赖更新检查完成：
>   CommonDataTypes: 1.2.0 → 1.3.0 (有新版本)
>   ValidationRules: 2.0.0 → 2.1.0 (有新版本)
```

### 10.2 更新依赖

```bash
kb update                    # 更新所有依赖
kb update CommonDataTypes    # 更新指定依赖
```

### 10.3 更新流程

```
1. 从依赖知识库的 git 仓库获取最新发布包列表
   - 读取 publish/ 目录下的文件列表

2. 对比当前版本和可用版本

3. 下载新版本发布包到缓存

4. 从缓存解压新版本到 deps/ 目录（覆盖旧版本）

5. 自动更新 Knowledge.md 中的依赖版本号

6. 完成更新
```

### 10.4 版本冲突处理

更新后如果检测到版本冲突，报错提示用户处理：

```bash
kb update CommonDataTypes
> 警告：更新后检测到版本冲突
>   - A 依赖 CommonDataTypes@1.3.0
>   - B 依赖 CommonDataTypes@1.2.0
> 请检查并调整依赖版本
```

## 11. 命令行工具设计

### 11.1 命令列表

| 命令 | 说明 |
|-----|------|
| `kb init` | 初始化知识库，下载所有依赖 |
| `kb package` | 打包当前知识库并生成发布包 |
| `kb check-updates [name]` | 检查依赖是否有新版本 |
| `kb update [name]` | 更新依赖到新版本 |
| `kb cache clean [name:version]` | 清理缓存 |

### 11.2 命令详细说明

#### 11.2.1 kb init

初始化知识库，下载所有依赖。

```bash
kb init
```

**流程**：
1. 解析 Knowledge.md 中的依赖表
2. 检查全局缓存
3. 下载缺失的依赖
4. 解压到 deps/ 目录
5. 递归处理依赖的依赖

#### 11.2.2 kb package

打包当前知识库并生成发布包。

```bash
kb package
```

**流程**：
1. 读取 .kb-package.yml 配置
2. 根据配置确定文件列表
3. 创建 tar.gz 发布包
4. 保存到 publish/ 目录

#### 11.2.3 kb check-updates

检查依赖是否有新版本。

```bash
kb check-updates                    # 检查所有依赖
kb check-updates CommonDataTypes    # 检查指定依赖
```

**流程**：
1. 从 git 仓库获取发布包列表
2. 对比当前版本
3. 显示可用更新

#### 11.2.4 kb update

更新依赖到新版本。

```bash
kb update                        # 更新所有依赖
kb update CommonDataTypes        # 更新指定依赖
```

**流程**：
1. 检查可用更新
2. 下载新版本
3. 解压到 deps/ 目录
4. 更新 Knowledge.md 中的版本号

#### 11.2.5 kb cache clean

清理缓存。

```bash
kb cache clean                                    # 清理所有缓存
kb cache clean FileFormatParser                   # 清理指定知识库
kb cache clean FileFormatParser:1.0.0            # 清理指定版本
```

# Knowledge Base Development Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个Claude Code Skill文件，指导智能体进行知识库项目的全流程开发（创建、开发、打包、发布）。

**Architecture:** 单一Markdown文件，包含Skill概述、概念说明、工作流程、技术规范、最佳实践和故障排除。使用清晰的章节结构和示例代码，便于智能体理解和执行。优先通过kb CLI命令操作，CLI无法满足时提供指导。

**Tech Stack:** Markdown

---

## File Structure

```
.skills/                           # Claude Code Skills目录
└── knowledge-base-development.md     # 主Skill文件
```

---

## Task 1: 创建Skill文件基础结构

**Files:**
- Create: `.skills/knowledge-base-development.md`

- [ ] **Step 1: 创建Skill文件头（包含概述和触发条件）**

```markdown
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
```

- [ ] **Step 2: 添加Skill结构和章节大纲**

在概述后添加以下章节标题：

```markdown
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
```

- [ ] **Step 3: 提交**

```bash
git add .skills/knowledge-base-development.md
git commit -m "feat(skill): 创建知识库开发Skill基础结构"
```

---

## Task 2: 添加概念说明章节

**Files:**
- Modify: `.skills/knowledge-base-development.md`

- [ ] **Step 1: 添加核心概念小节**

在"概念说明"章节下添加6个核心概念：

```markdown
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
```

- [ ] **Step 2: 提交**

```bash
git add .skills/knowledge-base-development.md
git commit -m "feat(skill): 添加概念说明章节"
```

---

## Task 3: 添加工作流程章节

**Files:**
- Modify: `.skills/knowledge-base-development.md`

- [ ] **Step 1: 添加阶段工作流程（创建、开发、打包、发布）**

```markdown
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
```

- [ ] **Step 2: 添加常见任务工作流程**

```markdown
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
```

- [ ] **Step 3: 提交**

```bash
git add .skills/knowledge-base-development.md
git commit -m "feat(skill): 添加工作流程章节"
```

---

## Task 4: 添加技术规范章节

**Files:**
- Modify: `.skills/knowledge-base-development.md`

- [ ] **Step 1: 添加目录结构和Knowledge.md格式**

```markdown
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
```

- [ ] **Step 2: 添加CLI命令参考**

```markdown
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
```

- [ ] **Step 3: 添加Python API参考**

```markdown
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
```

- [ ] **Step 4: 提交**

```bash
git add .skills/knowledge-base-development.md
git commit -m "feat(skill): 添加技术规范章节"
```

---

## Task 5: 添加最佳实践章节

**Files:**
- Modify: `.skills/knowledge-base-development.md`

- [ ] **Step 1: 添加版本管理和依赖管理最佳实践**

```markdown
## 最佳实践

### 版本管理

1. **遵循语义化版本规范**
   - 主版本：不兼容的API变更
   - 次版本：向后兼容的功能新增
   - 修订版本：向后兼容的bug修复

2. **发布前测试**
   - 确保所有测试通过
   - 测试依赖兼容性
   - 验证版本号正确

3. **保留发布历史**
   - 保留每个版本的发布包
   - 记录版本变更日志
   - 便于回滚和问题追踪

### 依赖管理

1. **使用精确版本号**
   - 尽量使用精确版本（1.2.0）而非范围（^1.2.0）
   - 避免意外的依赖更新
   - 提高可复现性

2. **定期检查更新**
   - 定期使用kb check-updates检查
   - 评估更新的影响和兼容性
   - 及时更新以获取安全修复

3. **谨慎处理冲突**
   - 使用排除依赖表明确排除冲突版本
   - 文档化排除原因
   - 寻找长期解决方案

### 项目结构

1. **保持目录清晰**
   - 业务逻辑放在src/目录
   - 测试放在tests/目录
   - 文档放在docs/目录

2. **维护Knowledge.md**
   - 保持简洁和准确
   - 及时更新版本号和依赖信息
   - 定期审查依赖表

3. **编写文档**
   - 编写README.md
   - 说明如何使用此知识库
   - 提供示例代码

4. **编写测试**
   - 为知识库编写测试
   - 确保测试覆盖核心功能
   - kb package前先运行测试
```

- [ ] **Step 2: 添加开发流程和缓存管理最佳实践**

```markdown
### 开发流程

1. **规划优先**
   - 开发新功能前先规划设计
   - 确定依赖需求
   - 考虑版本兼容性

2. **小步迭代**
   - 修改依赖后立即测试
   - 定期运行完整测试套件
   - 使用kb init验证依赖配置

3. **版本控制**
   - 使用Git跟踪变更
   - 为重要功能创建分支
   - 发布前打tag

4. **打包前验证**
   - 运行完整测试套件
   - 验证Knowledge.md完整性
   - 检查依赖是否正确

### 缓存管理

1. **定期清理**
   - 定期清理不需要的缓存
   - 使用kb cache clean library-name清理特定库
   - 避免缓存占用过多磁盘空间

2. **故障排查**
   - 遇到下载问题时尝试清理缓存
   - 使用kb cache info查看缓存状态
   - 检查缓存目录权限

3. **监控缓存**
   - 使用kb cache info监控缓存大小
   - 查看缓存的库和版本数量
   - 及时清理过期的缓存
```

- [ ] **Step 3: 提交**

```bash
git add .skills/knowledge-base-development.md
git commit -m "feat(skill): 添加最佳实践章节"
```

---

## Task 6: 添加常见陷阱和故障排除章节

**Files:**
- Modify: `.skills/knowledge-base-development.md`

- [ ] **Step 1: 添加5个常见陷阱**

```markdown
## 常见陷阱

### 陷阱1：Knowledge.md格式错误

**症状：**
- kb init报错无法解析
- 依赖未正确识别

**原因：**
- 表头格式不正确
- 表格语法错误
- 字符编码问题（非UTF-8）

**解决方案：**
- 参考Knowledge.md模板检查格式
- 确保使用标准Markdown表格语法
- 使用UTF-8编码保存文件

### 陷阱2：版本冲突

**症状：**
- kb init报错提示版本冲突
- deps/目录中的依赖版本不正确

**原因：**
- 不同依赖声明了同一库的不同版本
- 依赖的依赖之间存在冲突

**解决方案：**
- 使用kb check-updates查看依赖关系
- 在排除依赖表中排除冲突的版本
- 升级或降级依赖到兼容版本

### 陷阱3：缓存问题

**症状：**
- 依赖下载失败但网络正常
- 新版本未生效

**原因：**
- 缓存文件损坏
- 缓存目录权限问题
- 旧版本缓存阻止新版本下载

**解决方案：**
- 运行kb cache clean all清理全部缓存
- 检查~/.kb-cache/目录权限
- 使用kb cache list查看缓存的库和版本

### 陷阱4：打包失败

**症状：**
- kb package报错
- 生成的包文件不完整

**原因：**
- src/目录不存在
- Knowledge.md缺失或格式错误
- 缺少必要文件

**解决方案：**
- 确保在知识库根目录运行kb package
- 验证src/Knowledge.md存在且格式正确
- 运行kb --help查看命令详情

### 陷阱5：依赖路径问题

**症状：**
- 代码中无法导入依赖
- 运行时提示模块未找到

**原因：**
- deps/目录未正确创建
- Python路径未包含deps/目录
- 依赖的目录结构与预期不符

**解决方案：**
- 确保运行kb init初始化依赖
- 在代码中添加deps/到Python路径
- 检查deps/目录结构是否正确
```

- [ ] **Step 2: 添加故障排除清单**

```markdown
## 故障排除清单

遇到问题时按以下顺序检查：

### 1. 检查命令语法
```bash
kb --help
kb <command> --help
```

### 2. 检查文件结构
- 确保在正确的目录运行命令
- 验证src/Knowledge.md存在
- 检查deps/、publish/目录权限

### 3. 检查依赖状态
```bash
kb check-updates
kb cache info
```

### 4. 清理缓存
```bash
kb cache clean all
kb init
```

### 5. 查看详细日志
```bash
kb <command> --verbose
```

### 6. 查阅文档
- 阅读项目README.md
- 查看相关测试代码
```

- [ ] **Step 3: 提交**

```bash
git add .skills/knowledge-base-development.md
git commit -m "feat(skill): 添加常见陷阱和故障排除章节"
```

---

## Task 7: 最终验证和文档更新

**Files:**
- Modify: `.skills/knowledge-base-development.md`

- [ ] **Step 1: 验证Skill文件完整性**

检查清单：
- [ ] 概述章节完整（适用场景、触发条件）
- [ ] 概念说明包含6个核心概念
- [ ] 工作流程包含4个阶段和4个任务
- [ ] 技术规范包含目录结构、文件格式、CLI命令、Python API
- [ ] 最佳实践包含版本管理、依赖管理、项目结构、开发流程、缓存管理
- [ ] 常见陷阱包含5个陷阱
- [ ] 故障排除清单完整

- [ ] **Step 2: 更新README.md**

在项目README.md中添加Skill使用说明：

```markdown
## Claude Code Skill

项目包含知识库开发Skill，用于辅助Claude智能体进行知识库项目的全流程开发。

**使用方式：**
```bash
# 将Skill文件复制到Claude Code的Skills目录
cp .skills/knowledge-base-development.md ~/.claude/skills/

# 或在Claude Code中启用自定义Skills目录
# 设置 -> Skills -> Add Skills Directory
# 选择项目根目录
```

**Skill功能：**
- 指导创建知识库项目
- 指导开发知识库功能
- 指导打包和发布知识库
- 提供故障排除指南
```

- [ ] **Step 3: 运行最终测试**

检查Skill文件格式：
```bash
# 验证Markdown格式
head .skills/knowledge-base-development.md

# 检查文件大小和结构
wc -l .skills/knowledge-base-development.md
ls -lh .skills/knowledge-base-development.md
```

Expected: 文件格式正确，内容完整

- [ ] **Step 4: 提交**

```bash
git add .skills/knowledge-base-development.md README.md
git commit -m "feat(skill): 完成知识库开发Skill，更新文档"
```

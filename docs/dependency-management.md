# 依赖管理系统

## 概述

知识库系统实现了完整的依赖管理功能，支持自动下载、解压和管理知识库依赖项。

## 功能特性

### 1. 依赖解析
- 自动解析 Knowledge.md 文件中的依赖声明
- 支持版本范围和精确版本控制
- 处理排除依赖配置

### 2. 版本冲突检测
- 自动检测同一依赖的不同版本冲突
- 提供详细的冲突报告
- 支持多种冲突类型检测

### 3. 包下载
- 支持 GitHub 和 GitLab 仓库
- 自动缓存下载的包
- 支持强制重新下载

### 4. 包解压
- 支持 .tar.gz 格式
- 安全的路径验证
- 自动创建目标目录

## 使用方法

### 在 kb init 命令中自动使用

依赖管理功能已集成到 `kb init` 命令中：

```bash
# 初始化知识库（自动处理依赖）
kb init --path Knowledge.md

# 在当前目录初始化
kb init
```

### 依赖声明格式

在 Knowledge.md 文件中声明依赖：

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

### 版本号格式

- **精确版本**: `1.0.0`
- **版本范围**: `^1.0.0` (兼容版本), `~2.1.0` (补丁版本)
- **预发布版本**: `1.0.0-alpha.1`

## 缓存管理

下载的包会缓存在 `~/.kb-cache` 目录中：

```bash
# 查看缓存目录
ls ~/.kb-cache/

# 清理缓存
rm -rf ~/.kb-cache/
```

## 错误处理

系统提供详细的错误信息：

### 版本冲突错误
```
检测到依赖版本冲突：

1. 知识库 'ExampleLib'
   - 总请求数: 2
   - 版本列表: 1.0.0, 2.0.0
   - 冲突版本: 1.0.0, 2.0.0
   - 冲突原因: 同一知识库有多个不同版本
```

### 网络错误
```
知识库错误: 下载失败 - 网络连接超时
请检查网络连接或稍后重试
```

### 路径错误
```
知识库错误: 不安全的缓存目录路径
缓存目录必须是绝对路径
```

## 开发接口

### 依赖解析器

```python
from kb.dependency import DependencyResolver

resolver = DependencyResolver()
dependencies = resolver.resolve(metadata.dependencies)
```

### 版本冲突检测器

```python
from kb.dependency import ConflictDetector

detector = ConflictDetector()
detector.check_conflicts(dependencies)
```

### 包下载器

```python
from kb.dependency import PackageDownloader

downloader = PackageDownloader()
package_file = downloader.download(
    name="ExampleLib",
    version="1.0.0",
    git_url="https://github.com/example/example-lib"
)
```

### 包解压器

```python
from kb.dependency import PackageExtractor

extractor = PackageExtractor()
extractor.extract(package_file, target_dir)
```

## 最佳实践

1. **版本管理**: 使用语义化版本号，避免使用通配符
2. **依赖隔离**: 每个知识库应有明确的依赖版本要求
3. **缓存利用**: 利用缓存机制减少重复下载
4. **错误处理**: 妥善处理网络错误和版本冲突

## 故障排除

### 常见问题

1. **下载失败**
   - 检查网络连接
   - 验证 Git URL 是否正确
   - 确认仓库存在且公开访问

2. **版本冲突**
   - 检查 Knowledge.md 中的依赖声明
   - 使用排除依赖解决冲突
   - 确保版本号格式正确

3. **权限错误**
   - 确保对缓存目录有写权限
   - 检查目标目录访问权限
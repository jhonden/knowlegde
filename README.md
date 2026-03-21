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

这将创建一个包含标准目录结构的知识库项目。

### 打包知识库

将知识库打包为发布格式：

```bash
kb package
```

这将验证知识库并生成最终的包文件。

## 命令列表 (Command List)

| 命令 | 描述 | 选项 |
|------|------|------|
| `kb init [目录名]` | 初始化知识库项目 | `--template` 指定模板类型 |
| `kb package` | 打包知识库为发布格式 | `--output` 指定输出路径 |
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

### 测试结构

```
tests/
├── __init__.py
├── cli/
│   ├── test_init.py      # init命令测试
│   ├── test_package.py    # package命令测试
│   ├── test_main.py       # 主CLI测试
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
│   │   └── utils.py         # CLI工具函数
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py        # 数据模型
│   │   ├── parser.py        # 解析器
│   │   └── validator.py     # 验证器
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
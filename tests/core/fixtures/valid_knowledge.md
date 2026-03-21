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

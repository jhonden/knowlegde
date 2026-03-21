# FileFormatParser

## 基本信息

- **名称**: FileFormatParser
- **版本**: 1.2.0
- **类型**: structure-knowledge
- **职责描述**: 封装特定文件格式的解析知识

## 适用场景

文件格式解析，数据结构转换

## 对外能力

- 解析JSON文件
- 转换为内部数据结构

## 文件路径图谱

```
src/
├── parser.py
└── utils.py
```

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| OldParserLib | 1.0.0 | 已过时 |

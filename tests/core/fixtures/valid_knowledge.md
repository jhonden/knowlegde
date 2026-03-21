# 知识库名称

test-knowledge

# 版本

1.2.3

# 类型

agent

# 描述

这是一个测试知识库，用于验证解析器的功能。

# 依赖

| 依赖名称 | 版本 | Git URL |
| --- | --- | --- |
| dep1 | 1.0.0 | https://github.com/test/dep1.git |
| dep2 | 2.3.4 | https://github.com/test/dep2.git |

# 排除的依赖

| 依赖名称 | 版本 | 排除原因 |
| --- | --- | --- |
| old-dep | 0.5.0 | 已弃用，不再维护 |

# 应用场景

- 场景一：自动化测试
- 场景二：代码生成
- 场景三：数据分析

# 能力

- 自然语言处理
- 代码分析
- 自动化测试

# 文件图结构

```json
{
  "nodes": [
    {"id": "n1", "label": "模块1"},
    {"id": "n2", "label": "模块2"}
  ],
  "edges": [
    {"source": "n1", "target": "n2"}
  ]
}
```

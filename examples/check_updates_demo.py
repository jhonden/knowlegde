#!/usr/bin/env python3
"""
版本检查器演示脚本

展示如何使用 VersionChecker 检查知识库依赖的最新版本。
"""

from pathlib import Path
from unittest.mock import Mock, patch

from kb.update.checker import VersionChecker
from kb.core.parser import KnowledgeParser


def demo_check_updates():
    """演示检查多个依赖的更新。"""
    print("=" * 60)
    print("演示 1: 检查多个依赖的更新")
    print("=" * 60)

    # 创建模拟的 GitHub API 响应
    mock_responses = {
        "github.com/example/common-data-types": {"tag_name": "v2.0.0"},
        "github.com/example/utils-lib": {"tag_name": "v2.1.0"},
    }

    def mock_get(url, *args, **kwargs):
        """模拟 requests.get"""
        response = Mock()
        if "github.com/example/common-data-types" in url:
            response.json.return_value = mock_responses["github.com/example/common-data-types"]
        elif "github.com/example/utils-lib" in url:
            response.json.return_value = mock_responses["github.com/example/utils-lib"]
        else:
            response.json.return_value = {"tag_name": "v1.0.0"}
        return response

    with patch('kb.update.checker.requests.get', side_effect=mock_get):
        # 创建示例依赖
        from kb.core.models import Dependency
        dependencies = [
            Dependency(
                name="CommonDataTypes",
                version="1.0.0",
                git_url="https://github.com/example/common-data-types"
            ),
            Dependency(
                name="UtilsLib",
                version="2.1.0",
                git_url="https://github.com/example/utils-lib"
            ),
        ]

        # 创建检查器并检查更新
        checker = VersionChecker()
        update_list = checker.check_updates(dependencies)

        # 显示结果
        print(f"\n检查了 {len(dependencies)} 个依赖")
        print(f"发现 {len(update_list)} 个可用更新\n")

        if update_list.has_updates():
            for update in update_list:
                print(f"  {update.name}:")
                print(f"    当前版本: {update.current_version}")
                print(f"    最新版本: {update.latest_version}")
                print(f"    Git URL: {update.git_url}")
                print()
        else:
            print("  所有依赖都是最新版本")


def demo_check_single_dependency():
    """演示检查单个依赖的更新。"""
    print("=" * 60)
    print("演示 2: 检查单个依赖的更新")
    print("=" * 60)

    # 创建临时的知识库文件
    import tempfile
    import os

    knowledge_content = """# TestLib

## 基本信息

- **名称**: TestLib
- **版本**: 1.0.0
- **类型**: test
- **职责描述**: 测试知识库

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonDataTypes | 1.0.0 | https://github.com/example/common-data-types |
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_file = Path(tmpdir) / "Knowledge.md"
        knowledge_file.write_text(knowledge_content)

        # 模拟 GitHub API 响应
        mock_response = Mock()
        mock_response.json.return_value = {"tag_name": "v2.5.0"}

        with patch('kb.update.checker.requests.get', return_value=mock_response):
            checker = VersionChecker()
            update_list = checker.check_single_dependency(
                knowledge_file, "CommonDataTypes"
            )

            # 显示结果
            for update in update_list:
                print(f"\n依赖名称: {update.name}")
                print(f"当前版本: {update.current_version}")
                print(f"最新版本: {update.latest_version}")
                print(f"有可用更新: {'是' if update.update_available else '否'}")
                print()


def demo_version_comparison():
    """演示版本比较。"""
    print("=" * 60)
    print("演示 3: 版本比较示例")
    print("=" * 60)

    checker = VersionChecker()

    test_cases = [
        ("1.0.0", "1.0.1", "修订版本更新"),
        ("1.0.0", "1.1.0", "次版本更新"),
        ("1.0.0", "2.0.0", "主版本更新"),
        ("2.0.0", "1.0.0", "降级"),
        ("1.0.0", "1.0.0", "相同版本"),
        ("1.0.0", "v1.0.1", "带 v 前缀"),
        ("1.0.0", "1.0.1-alpha.1", "预发布版本"),
    ]

    print("\n版本比较结果:")
    print(f"{'当前版本':<15} {'目标版本':<15} {'结果':<20} 说明")
    print("-" * 60)

    for current, latest, description in test_cases:
        has_update = checker._compare_versions(current, latest)
        result = "有更新" if has_update else "无更新"
        print(f"{current:<15} {latest:<15} {result:<20} {description}")

    print()


def demo_error_handling():
    """演示错误处理。"""
    print("=" * 60)
    print("演示 4: 错误处理")
    print("=" * 60)

    from kb.core.models import Dependency
    from kb.exceptions import KnowledgeBaseError

    checker = VersionChecker()

    # 测试不支持的 URL
    print("\n1. 测试不支持的 URL:")
    try:
        dependency = Dependency(
            name="TestLib",
            version="1.0.0",
            git_url="https://bitbucket.org/example/repo"
        )
        update = checker._check_single_dependency(dependency)
    except KnowledgeBaseError as e:
        print(f"   捕获到预期错误: {e}")

    # 测试无效的 URL 格式
    print("\n2. 测试无效的 URL 格式:")
    try:
        owner, repo = checker._extract_owner_repo("invalid-url")
    except KnowledgeBaseError as e:
        print(f"   捕获到预期错误: {e}")

    # 测试版本号格式错误
    print("\n3. 测试版本号格式错误:")
    try:
        parts = checker._parse_version("1.0")
    except ValueError as e:
        print(f"   捕获到预期错误: {e}")

    print()


def main():
    """主函数。"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + " " * 10 + "版本检查器 (VersionChecker) 演示" + " " * 21 + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")

    # 运行各个演示
    demo_check_updates()
    print("\n")

    demo_check_single_dependency()
    print("\n")

    demo_version_comparison()
    print("\n")

    demo_error_handling()

    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n")


if __name__ == "__main__":
    main()

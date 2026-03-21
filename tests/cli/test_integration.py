"""Integration tests for CLI commands using core modules."""
from pathlib import Path
from click.testing import CliRunner
from kb.cli.main import cli


def test_init_with_valid_knowledge():
    """Test init command with valid Knowledge.md using core parser."""
    runner = CliRunner()

    # Create a valid Knowledge.md content based on the fixture format
    knowledge_content = """# Test Knowledge Library

## 基本信息

- **名称**: TestLib
- **版本**: 2.0.0
- **类型**: test-knowledge
- **职责描述**: 测试知识库示例

## 依赖

| 知识库名称 | 版本号 | Git地址 |
|-----------|--------|---------|
| CommonLib | 1.1.0 | https://github.com/example/common-lib |

## 排除依赖

| 知识库名称 | 版本号 | 原因 |
|-----------|--------|------|
| OldLib | 1.0.0 | 已过时 |

## 适用场景

单元测试、集成测试

## 对外能力

- 提供测试工具
- 定义测试框架
"""

    with runner.isolated_filesystem():
        # Create Knowledge.md file
        Path("Knowledge.md").write_text(knowledge_content)

        # Create src directory (as would be typical)
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "test_file.py").write_text("# Test content")

        # Run init command
        result = runner.invoke(cli, ["init"])

        # Verify the command succeeded
        assert result.exit_code == 0

        # Verify that Knowledge metadata was parsed and displayed
        assert "正在解析知识库文件" in result.output
        assert "知识库名称: TestLib" in result.output
        assert "版本: 2.0.0" in result.output
        assert "类型: test-knowledge" in result.output
        assert "职责描述: 测试知识库示例" in result.output
        assert "依赖数量: 1" in result.output
        assert "CommonLib@1.1.0 (https://github.com/example/common-lib)" in result.output

        # Verify completion message
        assert "初始化完成" in result.output


def test_init_with_minimal_knowledge():
    """Test init command with minimal Knowledge.md."""
    runner = CliRunner()

    minimal_content = """# Minimal Knowledge

## 基本信息

- **名称**: MinimalKB
- **版本**: 1.0.0
- **类型**: minimal
- **职责描述**: 最小化知识库
"""

    with runner.isolated_filesystem():
        Path("Knowledge.md").write_text(minimal_content)

        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert "正在解析知识库文件" in result.output
        assert "知识库名称: MinimalKB" in result.output
        assert "版本: 1.0.0" in result.output
        assert "初始化完成" in result.output


def test_package_with_valid_knowledge():
    """Test package command with valid Knowledge.md using core parser."""
    runner = CliRunner()

    knowledge_content = """# PackageTest Lib

## 基本信息

- **名称**: PackageTest
- **版本**: 3.1.0
- **类型**: package-knowledge
- **职责描述**: 测试打包功能
"""

    with runner.isolated_filesystem():
        # Create src directory with files
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('Hello World')")
        (src_dir / "config.py").write_text("DEBUG = True")

        # Create subdirectory
        subdir = src_dir / "utils"
        subdir.mkdir()
        (subdir / "helper.py").write_text("def helper(): pass")

        # Create Knowledge.md
        Path("Knowledge.md").write_text(knowledge_content)

        # Run package command
        result = runner.invoke(cli, ["package"])

        # Verify the command succeeded
        assert result.exit_code == 0

        # Verify that Knowledge metadata was parsed and displayed
        assert "正在解析知识库文件" in result.output
        assert "知识库名称: PackageTest" in result.output
        assert "版本: 3.1.0" in result.output

        # Verify completion message
        assert "打包完成" in result.output

        # Verify publish directory and package were created
        publish_dir = Path("publish")
        assert publish_dir.exists()

        # Verify package file exists and has correct name
        package_files = list(publish_dir.glob("*.tar.gz"))
        assert len(package_files) == 1
        assert package_files[0].name == "PackageTest-3.1.0.tar.gz"


def test_package_with_invalid_knowledge_fallback():
    """Test package command with invalid Knowledge.md should fallback to defaults."""
    runner = CliRunner()

    invalid_content = """# Invalid Knowledge

## 基本信息

- **名称**: InvalidLib
# Missing version and other required fields
"""

    with runner.isolated_filesystem():
        # Create src directory
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")

        # Create invalid Knowledge.md
        Path("Knowledge.md").write_text(invalid_content)

        # Run package command
        result = runner.invoke(cli, ["package"])

        # Should still succeed but with warning and fallback values
        assert result.exit_code == 0
        assert "警告: 解析知识库文件失败" in result.output
        assert "使用默认值" in result.output
        assert "正在解析知识库文件" not in result.output  # Parsing failed, no success message

        # Should use fallback values
        assert "知识库名称: knowledge-package" in result.output
        assert "版本: 1.0.0" in result.output
        assert "打包完成" in result.output


def test_init_with_empty_content_fails_gracefully():
    """Test init command with empty Knowledge.md."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        Path("Knowledge.md").write_text("")

        result = runner.invoke(cli, ["init"])

        # Should fail due to empty file (validation before parsing)
        assert result.exit_code == 0
        assert "错误: 知识库文件" in result.output
        assert "为空" in result.output


def test_package_without_knowledge_fails():
    """Test package command without Knowledge.md should fail."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create src directory but no Knowledge.md
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")

        result = runner.invoke(cli, ["package"])

        # Should fail before parsing
        assert result.exit_code != 0
        assert "错误: 未找到知识库文件" in result.output
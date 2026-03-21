from click.testing import CliRunner
from kb.cli.main import cli
from pathlib import Path
import tempfile
import os


def test_init_command():
    """测试在包含Knowledge.md的目录中初始化"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # 创建Knowledge.md文件
        Path("Knowledge.md").write_text("# Test Knowledge Base")
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "初始化完成" in result.output


def test_init_without_knowledge_file():
    """测试在缺少Knowledge.md的目录中初始化"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # 不创建Knowledge.md文件
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "错误: 未找到知识库文件" in result.output
        assert "请确保文件存在" in result.output


def test_init_with_custom_path():
    """测试使用自定义路径初始化"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # 在子目录中创建Knowledge.md
        subdir = Path("subdir")
        subdir.mkdir()
        (subdir / "Knowledge.md").write_text("# Test Knowledge Base")

        # 使用--path参数指定路径
        result = runner.invoke(cli, ["init", "--path", str(subdir / "Knowledge.md")])
        assert result.exit_code == 0
        assert "初始化完成" in result.output
        assert str(subdir / "Knowledge.md") in result.output


def test_init_with_nonexistent_path():
    """测试使用不存在的路径初始化"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # 使用不存在的文件路径
        result = runner.invoke(cli, ["init", "--path", "nonexistent.md"])
        assert result.exit_code == 0
        assert "错误: 未找到知识库文件" in result.output
        assert "nonexistent.md" in result.output

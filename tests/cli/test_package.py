from pathlib import Path

from click.testing import CliRunner
from kb.cli.main import cli


def test_package_command_success(tmp_path):
    """测试成功打包的路径"""
    runner = CliRunner()

    # 创建测试目录结构
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # 创建src目录并添加一些文件
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "file1.txt").write_text("content1")
        (src_dir / "file2.txt").write_text("content2")

        # 创建子目录和文件
        subdir = src_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")

        # 创建Knowledge.md
        Path("Knowledge.md").write_text("# Test Knowledge Base\n\nName: test\nVersion: 1.0.0")

        # 运行命令
        result = runner.invoke(cli, ["package"])

        # 验证结果
        assert result.exit_code == 0
        assert "打包完成" in result.output

        # 验证publish目录和文件被创建
        publish_dir = Path("publish")
        assert publish_dir.exists()
        assert publish_dir.is_dir()

        # 验证包文件被创建
        package_files = list(publish_dir.glob("*.tar.gz"))
        assert len(package_files) == 1


def test_package_command_src_not_exists(tmp_path):
    """测试src目录不存在的场景"""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # 创建Knowledge.md但不创建src目录
        Path("Knowledge.md").write_text("# Test")

        # 运行命令
        result = runner.invoke(cli, ["package"])

        # 验证失败
        assert result.exit_code != 0
        assert "错误: 源码目录" in result.output
        assert "不存在" in result.output


def test_package_command_knowledge_not_exists(tmp_path):
    """测试Knowledge.md不存在的场景"""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # 创建src目录但不创建Knowledge.md
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")

        # 运行命令
        result = runner.invoke(cli, ["package"])

        # 验证失败
        assert result.exit_code != 0
        assert "错误: 未找到知识库文件" in result.output


def test_package_command_custom_src(tmp_path):
    """测试使用自定义src路径"""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # 创建自定义源码目录
        custom_src = Path("custom_src")
        custom_src.mkdir()
        (custom_src / "file.txt").write_text("content")

        # 创建Knowledge.md
        Path("Knowledge.md").write_text("# Test")

        # 运行命令使用自定义src
        result = runner.invoke(cli, ["package", "--src", "custom_src"])

        # 验证成功
        assert result.exit_code == 0
        assert "打包完成" in result.output

        # 验证publish目录被创建
        assert Path("publish").exists()


def test_package_command_publish_dir_auto_created(tmp_path):
    """测试publish目录自动创建"""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # 创建必需的目录和文件
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "file.txt").write_text("content")
        Path("Knowledge.md").write_text("# Test")

        # 确保publish目录不存在
        assert not Path("publish").exists()

        # 运行命令
        result = runner.invoke(cli, ["package"])

        # 验证成功
        assert result.exit_code == 0
        assert "打包完成" in result.output

        # 验证publish目录被自动创建
        publish_dir = Path("publish")
        assert publish_dir.exists()
        assert publish_dir.is_dir()

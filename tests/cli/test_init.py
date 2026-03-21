from click.testing import CliRunner
from kb.cli.main import cli


def test_init_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    assert "初始化完成" in result.output

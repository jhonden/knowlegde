from click.testing import CliRunner
from kb.cli.main import cli


def test_package_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["package"])
    assert result.exit_code == 0
    assert "打包完成" in result.output

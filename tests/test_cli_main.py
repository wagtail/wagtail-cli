from typer.testing import CliRunner

from wgtl_api_cli.cli.main import app


runner = CliRunner()


def test_help_lists_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Wagtail v3 API" in result.output


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip()

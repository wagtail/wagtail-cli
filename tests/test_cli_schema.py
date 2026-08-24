import respx

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


BASE = "https://x.test/api/v3"
runner = CliRunner()


def _env(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", BASE)
    monkeypatch.setenv("WAGTAIL_CLI_TOKEN", "tok")


@respx.mock
def test_schema_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/schema/").respond(
        200, json={"types": [{"name": "blog.BlogPage", "label": "blog page"}]}
    )
    result = runner.invoke(app, ["schema", "list"])
    assert result.exit_code == 0
    assert "blog.BlogPage" in result.output


@respx.mock
def test_schema_show_returns_json_even_when_tty(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/schema/blog.BlogPage/").respond(
        200, json={"read": {"title": "BlogPage"}}
    )
    result = runner.invoke(app, ["schema", "show", "blog.BlogPage"])
    assert result.exit_code == 0
    assert "BlogPage" in result.output
    # must be JSON (machine-readable), not the human table shape
    assert '"read":{"title":"BlogPage"}' in result.output

import respx

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


BASE = "https://x.test/api/v3"
runner = CliRunner()


def _env(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", BASE)
    monkeypatch.setenv("WAGTAIL_CLI_TOKEN", "tok")


@respx.mock
def test_whoami_json_when_piped(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/whoami/").respond(200, json={"user": {"username": "admin"}})
    result = runner.invoke(app, ["api", "whoami"])
    assert result.exit_code == 0
    assert '"username":"admin"' in result.output  # compact JSON (not a TTY)


@respx.mock
def test_whoami_auth_error_exit_4(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/whoami/").respond(
        401, json={"title": "Unauthorized", "status": 401}
    )
    result = runner.invoke(app, ["api", "whoami"])
    assert result.exit_code == 4
    assert "Unauthorized" in result.output


def test_whoami_unconfigured_exit_2(monkeypatch):
    monkeypatch.delenv("WAGTAIL_CLI_BASE_URL", raising=False)
    monkeypatch.delenv("WAGTAIL_CLI_TOKEN", raising=False)
    result = runner.invoke(app, ["--url", BASE, "api", "whoami"])  # url but no token
    assert result.exit_code == 2
    assert "wt init" in result.output


def test_conflicting_output_flags_exit_2_no_traceback():
    result = runner.invoke(app, ["--json", "--human", "api", "whoami"])
    assert result.exit_code == 2
    assert "Cannot combine --json and --human" in result.stderr
    assert "Traceback" not in result.output
    assert "Traceback" not in result.stderr


@respx.mock
def test_init_writes_dotfile(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "wagtail_cli.config._user_dotfile", lambda: tmp_path / ".wagtail-cli.toml"
    )
    respx.get(f"{BASE}/whoami/").respond(200, json={"user": {"username": "admin"}})
    result = runner.invoke(app, ["--url", BASE, "--token", "tok123", "api", "init"])
    assert result.exit_code == 0
    data = (tmp_path / ".wagtail-cli.toml").read_text()
    assert 'url = "https://x.test/api/v3"' in data and 'token = "tok123"' in data


@respx.mock
def test_init_dry_run_writes_nothing(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "wagtail_cli.config._user_dotfile", lambda: tmp_path / ".wagtail-cli.toml"
    )
    # No route is registered: if any request is made, respx raises and the
    # test fails. Dry-run must skip both network and filesystem writes.
    result = runner.invoke(
        app, ["--dry-run", "--url", BASE, "--token", "tok123", "api", "init"]
    )
    assert result.exit_code == 0
    assert not (tmp_path / ".wagtail-cli.toml").exists()
    assert "dry-run: would write" in result.output
    assert "tok123" not in result.output  # token redacted

import json

import respx

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


BASE = "https://x.test/api/v3"
TYPE = "base.FooterText"
runner = CliRunner()


def _env(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", BASE)
    monkeypatch.setenv("WAGTAIL_CLI_TOKEN", "tok")


@respx.mock
def test_snippets_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/snippets/{TYPE}/").respond(200, json={"count": 1, "items": []})
    result = runner.invoke(app, ["snippets", "list", TYPE])
    assert result.exit_code == 0


@respx.mock
def test_snippets_get(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/snippets/{TYPE}/22/").respond(200, json={"id": 22})
    result = runner.invoke(app, ["snippets", "get", TYPE, "22"])
    assert result.exit_code == 0
    assert '"id":22' in result.output


@respx.mock
def test_snippets_create_via_field(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/snippets/{TYPE}/").respond(201, json={"id": 30})
    result = runner.invoke(app, ["snippets", "create", TYPE, "--field", "text:Hello"])
    assert result.exit_code == 0
    body = json.loads(respx.calls[0].request.content)
    assert body == {"text": "Hello"}


@respx.mock
def test_snippets_update_patch(monkeypatch):
    _env(monkeypatch)
    respx.patch(f"{BASE}/snippets/{TYPE}/22/").respond(200, json={"id": 22})
    result = runner.invoke(
        app,
        ["snippets", "update", TYPE, "22", "--field", "text:Updated", "--yes"],
    )
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "PATCH"
    body = json.loads(respx.calls[0].request.content)
    assert body == {"text": "Updated"}


@respx.mock
def test_snippets_update_refuses_non_tty_without_yes(monkeypatch):
    _env(monkeypatch)
    # CliRunner stdin is not a TTY, so confirmation fails unless --yes.
    result = runner.invoke(
        app, ["snippets", "update", TYPE, "22", "--field", "text:Updated"]
    )
    assert result.exit_code == 2
    assert len(respx.calls) == 0


@respx.mock
def test_snippets_delete_requires_yes(monkeypatch):
    _env(monkeypatch)
    respx.delete(f"{BASE}/snippets/{TYPE}/22/").respond(204)
    result = runner.invoke(app, ["snippets", "delete", TYPE, "22", "--yes"])
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "DELETE"


@respx.mock
def test_snippets_delete_refuses_non_tty_without_yes(monkeypatch):
    _env(monkeypatch)
    result = runner.invoke(app, ["snippets", "delete", TYPE, "22"])
    assert result.exit_code == 2
    assert len(respx.calls) == 0


@respx.mock
def test_snippets_publish(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/publish/").respond(
        200, json={"id": 22}
    )
    result = runner.invoke(app, ["snippets", "publish", TYPE, "22"])
    assert result.exit_code == 0


@respx.mock
def test_snippets_unpublish(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/unpublish/").respond(
        200, json={"id": 22}
    )
    result = runner.invoke(app, ["snippets", "unpublish", TYPE, "22"])
    assert result.exit_code == 0


@respx.mock
def test_snippets_revert(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/revert/").respond(
        200, json={"id": 22}
    )
    result = runner.invoke(app, ["snippets", "revert", TYPE, "22", "--revision", "7"])
    assert result.exit_code == 0
    assert json.loads(respx.calls[0].request.content) == {"revision_id": 7}


@respx.mock
def test_snippets_copy_for_translation(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/copy_for_translation/").respond(
        200, json={"id": 22}
    )
    result = runner.invoke(
        app, ["snippets", "copy-for-translation", TYPE, "22", "--locale", "fr"]
    )
    assert result.exit_code == 0
    assert json.loads(respx.calls[0].request.content) == {"locale": "fr"}


@respx.mock
def test_snippets_revisions_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/snippets/{TYPE}/22/revisions/").respond(200, json={"items": []})
    result = runner.invoke(app, ["snippets", "revisions", "list", TYPE, "22"])
    assert result.exit_code == 0


@respx.mock
def test_snippets_revisions_get(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/snippets/{TYPE}/22/revisions/5/").respond(200, json={"id": 5})
    result = runner.invoke(app, ["snippets", "revisions", "get", TYPE, "22", "5"])
    assert result.exit_code == 0
    assert '"id":5' in result.output


@respx.mock
def test_snippets_create_dry_run_no_http(monkeypatch):
    _env(monkeypatch)
    result = runner.invoke(
        app,
        ["--dry-run", "snippets", "create", TYPE, "--field", "text:Hello"],
    )
    assert result.exit_code == 0
    assert "POST" in result.output and "/snippets/" in result.output
    assert len(respx.calls) == 0


@respx.mock
def test_snippets_validation_error_exit_7(monkeypatch):
    _env(monkeypatch)
    problem = {
        "type": "about:blank",
        "title": "Unprocessable Entity",
        "status": 422,
        "detail": "Validation failed",
        "errors": [{"loc": ["text"]}],
    }
    respx.post(f"{BASE}/snippets/{TYPE}/").respond(422, json=problem)
    result = runner.invoke(app, ["snippets", "create", TYPE, "--field", "text:Bad"])
    assert result.exit_code == 7
    assert "Validation failed" in result.output

import json

import respx

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


BASE = "https://x.test/api/v3"
runner = CliRunner()


def _env(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", BASE)
    monkeypatch.setenv("WAGTAIL_CLI_TOKEN", "tok")


# --- sites ---


@respx.mock
def test_sites_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/sites/").respond(200, json={"count": 1, "items": []})
    result = runner.invoke(app, ["sites", "list"])
    assert result.exit_code == 0


@respx.mock
def test_sites_create_via_field(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/sites/").respond(201, json={"id": 5})
    result = runner.invoke(
        app,
        [
            "sites",
            "create",
            "--field",
            "hostname:example.com",
            "--field",
            "root_page_id:4",
        ],
    )
    assert result.exit_code == 0
    body = json.loads(respx.calls[0].request.content)
    assert body == {"hostname": "example.com", "root_page_id": "4"}


@respx.mock
def test_sites_update_put(monkeypatch):
    _env(monkeypatch)
    respx.put(f"{BASE}/sites/5/").respond(200, json={"id": 5})
    result = runner.invoke(
        app,
        [
            "sites",
            "update",
            "5",
            "--field",
            "hostname:new.example.com",
            "--field",
            "root_page_id:4",
            "--yes",
        ],
    )
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_sites_delete_requires_yes(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr("wagtail_cli.cli.sites._is_tty", lambda: False)
    result = runner.invoke(app, ["sites", "delete", "5"])
    assert result.exit_code == 2
    assert "--yes" in result.stderr or "--yes" in result.output


# --- locales ---


@respx.mock
def test_locales_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/locales/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(app, ["locales", "list"])
    assert result.exit_code == 0


@respx.mock
def test_locales_create_via_field(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/locales/").respond(201, json={"id": 4})
    result = runner.invoke(app, ["locales", "create", "--field", "language_code:fr"])
    assert result.exit_code == 0
    assert json.loads(respx.calls[0].request.content) == {"language_code": "fr"}


@respx.mock
def test_locales_update_put(monkeypatch):
    _env(monkeypatch)
    respx.put(f"{BASE}/locales/4/").respond(200, json={"id": 4})
    result = runner.invoke(
        app, ["locales", "update", "4", "--field", "language_code:de", "--yes"]
    )
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_locales_delete_yes(monkeypatch):
    _env(monkeypatch)
    respx.delete(f"{BASE}/locales/4/").respond(204)
    result = runner.invoke(app, ["locales", "delete", "4", "--yes"])
    assert result.exit_code == 0


# --- redirects ---


@respx.mock
def test_redirects_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/redirects/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(app, ["redirects", "list"])
    assert result.exit_code == 0


@respx.mock
def test_redirects_find_path(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/redirects/find/", params={"html_path": "/old/"}).respond(
        302, headers={"location": "/api/v3/redirects/9/?"}
    )
    result = runner.invoke(app, ["redirects", "find", "--path", "/old/"])
    assert result.exit_code == 0
    assert "location" in result.output


def test_redirects_find_requires_arg(monkeypatch):
    result = runner.invoke(app, ["redirects", "find"])
    assert result.exit_code == 2
    assert "--id" in result.output or "--id" in result.stderr


@respx.mock
def test_redirects_create_via_field(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/redirects/").respond(201, json={"id": 9})
    result = runner.invoke(
        app,
        [
            "redirects",
            "create",
            "--field",
            "old_path:/old/",
            "--field",
            "redirect_link:/new/",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(respx.calls[0].request.content) == {
        "old_path": "/old/",
        "redirect_link": "/new/",
    }


@respx.mock
def test_redirects_update_put(monkeypatch):
    _env(monkeypatch)
    respx.put(f"{BASE}/redirects/9/").respond(200, json={"id": 9})
    result = runner.invoke(
        app,
        ["redirects", "update", "9", "--field", "redirect_link:/new2/", "--yes"],
    )
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_redirects_delete_yes(monkeypatch):
    _env(monkeypatch)
    respx.delete(f"{BASE}/redirects/9/").respond(204)
    result = runner.invoke(app, ["redirects", "delete", "9", "--yes"])
    assert result.exit_code == 0

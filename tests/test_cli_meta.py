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
    result = runner.invoke(app, ["api", "sites", "list"])
    assert result.exit_code == 0


@respx.mock
def test_sites_list_local_select(monkeypatch):
    """--select works after the subcommand, not only as a global flag."""
    _env(monkeypatch)
    respx.get(f"{BASE}/sites/").respond(
        200,
        json={
            "count": 1,
            "items": [
                {
                    "id": 1,
                    "hostname": "example.com",
                    "port": 443,
                    "root_page_id": 4,
                    "site_name": "Example",
                    "is_default_site": True,
                }
            ],
        },
    )
    result = runner.invoke(
        app,
        [
            "--json",
            "api",
            "sites",
            "list",
            "--select",
            "id,hostname,root_page_id",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "count": 1,
        "items": [{"id": 1, "hostname": "example.com", "root_page_id": 4}],
    }


@respx.mock
def test_sites_list_local_and_global_select_merge(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/sites/").respond(
        200,
        json={"count": 1, "items": [{"id": 1, "hostname": "example.com", "port": 443}]},
    )
    result = runner.invoke(
        app,
        [
            "--json",
            "--select",
            "port",
            "api",
            "sites",
            "list",
            "--select",
            "id",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "count": 1,
        "items": [{"id": 1, "port": 443}],
    }


@respx.mock
def test_sites_get_local_select(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/sites/2/").respond(
        200, json={"id": 2, "hostname": "example.com", "port": 443}
    )
    result = runner.invoke(
        app, ["--json", "api", "sites", "get", "2", "--select", "hostname"]
    )
    assert result.exit_code == 0
    assert json.loads(result.output) == {"hostname": "example.com"}


@respx.mock
def test_sites_list_local_json(monkeypatch):
    """--json works after the subcommand, not only as a global flag."""
    _env(monkeypatch)
    respx.get(f"{BASE}/sites/").respond(
        200, json={"count": 1, "items": [{"id": 1, "hostname": "example.com"}]}
    )
    result = runner.invoke(app, ["api", "sites", "list", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "count": 1,
        "items": [{"id": 1, "hostname": "example.com"}],
    }


@respx.mock
def test_sites_list_local_human_overrides_global_json(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/sites/").respond(
        200, json={"count": 1, "items": [{"id": 1, "hostname": "example.com"}]}
    )
    result = runner.invoke(app, ["--json", "api", "sites", "list", "--human"])
    assert result.exit_code == 0
    # Human table rather than the compact JSON payload.
    assert "hostname" in result.output
    assert not result.output.startswith("{")


def test_sites_list_local_json_human_conflict(monkeypatch):
    result = runner.invoke(app, ["api", "sites", "list", "--json", "--human"])
    assert result.exit_code == 2
    assert "Cannot combine --json and --human" in result.output + result.stderr


@respx.mock
def test_sites_list_local_dry_run(monkeypatch):
    """--dry-run works after the subcommand and sends no request."""
    _env(monkeypatch)
    route = respx.get(f"{BASE}/sites/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(app, ["api", "sites", "list", "--dry-run"])
    assert result.exit_code == 0
    assert f"GET {BASE}/sites/" in result.output
    assert not route.called


@respx.mock
def test_sites_create_local_dry_run(monkeypatch):
    _env(monkeypatch)
    route = respx.post(f"{BASE}/sites/").respond(201, json={"id": 5})
    result = runner.invoke(
        app,
        [
            "api",
            "sites",
            "create",
            "--field",
            "hostname:example.com",
            "--field",
            "root_page_id:4",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert f"POST {BASE}/sites/" in result.output
    assert not route.called


@respx.mock
def test_sites_list_local_json_error_is_json(monkeypatch):
    """A command-local --json must also make errors machine-readable."""
    _env(monkeypatch)
    respx.get(f"{BASE}/sites/").respond(403, json={"title": "Forbidden", "status": 403})
    result = runner.invoke(app, ["api", "sites", "list", "--json"])
    assert result.exit_code == 5
    assert json.loads(result.stderr)["error"]["status"] == 403


@respx.mock
def test_sites_create_via_field(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/sites/").respond(201, json={"id": 5})
    result = runner.invoke(
        app,
        [
            "api",
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
            "api",
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
    result = runner.invoke(app, ["api", "sites", "delete", "5"])
    assert result.exit_code == 2
    assert "--yes" in result.stderr or "--yes" in result.output


# --- locales ---


@respx.mock
def test_locales_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/locales/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(app, ["api", "locales", "list"])
    assert result.exit_code == 0


@respx.mock
def test_locales_create_via_field(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/locales/").respond(201, json={"id": 4})
    result = runner.invoke(
        app, ["api", "locales", "create", "--field", "language_code:fr"]
    )
    assert result.exit_code == 0
    assert json.loads(respx.calls[0].request.content) == {"language_code": "fr"}


@respx.mock
def test_locales_update_put(monkeypatch):
    _env(monkeypatch)
    respx.put(f"{BASE}/locales/4/").respond(200, json={"id": 4})
    result = runner.invoke(
        app, ["api", "locales", "update", "4", "--field", "language_code:de", "--yes"]
    )
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_locales_delete_yes(monkeypatch):
    _env(monkeypatch)
    respx.delete(f"{BASE}/locales/4/").respond(204)
    result = runner.invoke(app, ["api", "locales", "delete", "4", "--yes"])
    assert result.exit_code == 0


# --- redirects ---


@respx.mock
def test_redirects_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/redirects/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(app, ["api", "redirects", "list"])
    assert result.exit_code == 0


@respx.mock
def test_redirects_find_path(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/redirects/find/", params={"html_path": "/old/"}).respond(
        302, headers={"location": "/api/v3/redirects/9/?"}
    )
    result = runner.invoke(app, ["api", "redirects", "find", "--path", "/old/"])
    assert result.exit_code == 0
    assert "location" in result.output


def test_redirects_find_requires_arg(monkeypatch):
    result = runner.invoke(app, ["api", "redirects", "find"])
    assert result.exit_code == 2
    assert "--id" in result.output or "--id" in result.stderr


@respx.mock
def test_redirects_create_via_field(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/redirects/").respond(201, json={"id": 9})
    result = runner.invoke(
        app,
        [
            "api",
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
        ["api", "redirects", "update", "9", "--field", "redirect_link:/new2/", "--yes"],
    )
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_redirects_delete_yes(monkeypatch):
    _env(monkeypatch)
    respx.delete(f"{BASE}/redirects/9/").respond(204)
    result = runner.invoke(app, ["api", "redirects", "delete", "9", "--yes"])
    assert result.exit_code == 0

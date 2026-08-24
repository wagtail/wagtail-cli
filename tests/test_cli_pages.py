import json

import respx

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


BASE = "https://x.test/api/v3"
runner = CliRunner()


def _env(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", BASE)
    monkeypatch.setenv("WAGTAIL_CLI_TOKEN", "tok")


@respx.mock
def test_pages_list_passes_filters(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(
        app,
        [
            "pages",
            "list",
            "--type",
            "blog.BlogPage",
            "--limit",
            "5",
            "--search",
            "iris",
            "--order",
            "-first_published_at",
        ],
    )
    assert result.exit_code == 0
    url = str(respx.calls[0].request.url)
    assert "type=blog.BlogPage" in url
    assert "limit=5" in url
    assert "search=iris" in url
    assert "order=-first_published_at" in url


@respx.mock
def test_pages_list_multiple_types_repeated_param(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/").respond(200, json={"count": 0, "items": []})
    runner.invoke(app, ["pages", "list", "--type", "a.A", "--type", "b.B"])
    url = str(respx.calls[0].request.url)
    assert "type=a.A" in url and "type=b.B" in url


@respx.mock
def test_pages_get_with_version_and_html(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/7/").respond(200, json={"id": 7, "title": "X"})
    result = runner.invoke(app, ["pages", "get", "7", "--version", "live", "--html"])
    assert result.exit_code == 0
    url = str(respx.calls[0].request.url)
    assert "version=live" in url
    assert "rich_text_format=html" in url


@respx.mock
def test_pages_find_returns_location(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/find/", params={"html_path": "/blog/"}).respond(
        302, headers={"location": "/api/v3/pages/61/?pid=1"}
    )
    result = runner.invoke(app, ["pages", "find", "--path", "/blog/"])
    assert result.exit_code == 0
    assert "location" in result.output


@respx.mock
def test_pages_create_with_field_and_publish(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/pages/").respond(200, json={"id": 9, "title": "Hello"})
    result = runner.invoke(
        app,
        [
            "pages",
            "create",
            "blog.BlogPage",
            "--parent",
            "3",
            "--title",
            "Hello",
            "--field",
            "subtitle:World",
            "--publish",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(respx.calls[0].request.content)
    assert payload["meta"] == {
        "type": "blog.BlogPage",
        "parent_id": 3,
        "action": "publish",
    }
    assert payload["title"] == "Hello"
    assert payload["subtitle"] == "World"


@respx.mock
def test_pages_create_resolves_path_parent(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/find/", params={"html_path": "/blog/"}).respond(
        302, headers={"location": "/api/v3/pages/61/?"}
    )
    respx.post(f"{BASE}/pages/").respond(200, json={"id": 100})
    result = runner.invoke(
        app, ["pages", "create", "blog.BlogPage", "--parent", "/blog/", "--title", "X"]
    )
    assert result.exit_code == 0
    payload = json.loads(respx.calls[1].request.content)
    assert payload["meta"]["parent_id"] == 61


@respx.mock
def test_pages_create_dry_run_no_http(monkeypatch):
    _env(monkeypatch)
    result = runner.invoke(
        app,
        [
            "--dry-run",
            "pages",
            "create",
            "blog.BlogPage",
            "--parent",
            "3",
            "--title",
            "T",
        ],
    )
    assert result.exit_code == 0
    assert len(respx.calls) == 0
    assert f"POST {BASE}/pages/" in result.output


@respx.mock
def test_pages_update_sends_patch(monkeypatch):
    _env(monkeypatch)
    respx.patch(f"{BASE}/pages/7/").respond(200, json={"id": 7, "title": "New"})
    result = runner.invoke(
        app,
        ["pages", "update", "7", "--title", "New", "--field", "subtitle:S", "--yes"],
    )
    assert result.exit_code == 0
    payload = json.loads(respx.calls[0].request.content)
    assert payload == {"title": "New", "subtitle": "S"}


@respx.mock
def test_pages_delete_with_yes(monkeypatch):
    _env(monkeypatch)
    respx.delete(f"{BASE}/pages/5/").respond(204)
    result = runner.invoke(app, ["pages", "delete", "5", "--yes"])
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "DELETE"
    assert str(respx.calls[0].request.url).endswith("/pages/5/")


def test_pages_delete_without_yes_exit_2_non_tty(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr("wagtail_cli.cli.pages._is_tty", lambda: False)
    result = runner.invoke(app, ["pages", "delete", "5"])
    assert result.exit_code == 2
    assert "--yes" in result.stderr or "--yes" in result.output


@respx.mock
def test_pages_update_without_yes_exit_2_non_tty_no_http(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr("wagtail_cli.cli.pages._is_tty", lambda: False)
    result = runner.invoke(app, ["pages", "update", "5", "--title", "New"])
    assert result.exit_code == 2
    assert "--yes" in result.stderr or "--yes" in result.output
    assert len(respx.calls) == 0


@respx.mock
def test_pages_non_numeric_id_clean_exit_2():
    result = runner.invoke(app, ["pages", "get", "abc"])
    assert result.exit_code == 2
    assert "Traceback" not in result.output
    assert "Traceback" not in result.stderr


@respx.mock
def test_pages_find_requires_id_or_path():
    result = runner.invoke(app, ["pages", "find"])
    assert result.exit_code == 2
    assert "--id" in result.output or "--id" in result.stderr


@respx.mock
def test_pages_publish_unpublish(monkeypatch):
    _env(monkeypatch)
    pub = respx.post(f"{BASE}/pages/7/actions/publish/").respond(
        200, json={"id": 7, "status": "live"}
    )
    res1 = runner.invoke(app, ["pages", "publish", "7"])
    assert res1.exit_code == 0
    assert "live" in res1.output
    respx.post(f"{BASE}/pages/7/actions/unpublish/").respond(
        200, json={"id": 7, "status": "draft"}
    )
    res2 = runner.invoke(app, ["pages", "unpublish", "7"])
    assert res2.exit_code == 0
    assert pub.called


@respx.mock
def test_pages_copy(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/find/", params={"html_path": "/blog/"}).respond(
        302, headers={"location": "/api/v3/pages/61/?"}
    )
    respx.post(f"{BASE}/pages/7/actions/copy/").respond(200, json={"id": 8})
    result = runner.invoke(
        app,
        [
            "pages",
            "copy",
            "7",
            "--destination",
            "/blog/",
            "--title",
            "Copy",
            "--keep-live",
        ],
    )
    assert result.exit_code == 0
    body = json.loads(respx.calls[-1].request.content)
    assert body["destination_id"] == 61  # resolved from /blog/
    assert body["title"] == "Copy"
    assert body["keep_live"] is True


@respx.mock
def test_pages_move(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/pages/7/actions/move/").respond(200, json={"id": 7})
    result = runner.invoke(app, ["pages", "move", "7", "--destination", "10"])
    assert result.exit_code == 0
    body = json.loads(respx.calls[0].request.content)
    assert body == {"destination_id": 10}


@respx.mock
def test_pages_revert(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/pages/7/actions/revert/").respond(200, json={"id": 7})
    result = runner.invoke(app, ["pages", "revert", "7", "--revision", "42"])
    assert result.exit_code == 0
    body = json.loads(respx.calls[0].request.content)
    assert body == {"revision_id": 42}


@respx.mock
def test_pages_create_alias(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/pages/7/actions/create_alias/").respond(200, json={"id": 50})
    result = runner.invoke(app, ["pages", "create-alias", "7", "--destination", "10"])
    assert result.exit_code == 0
    body = json.loads(respx.calls[0].request.content)
    assert body == {"destination_id": 10}


@respx.mock
def test_pages_convert_alias(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/pages/7/actions/convert_alias/").respond(200, json={"id": 7})
    result = runner.invoke(app, ["pages", "convert-alias", "7"])
    assert result.exit_code == 0


@respx.mock
def test_pages_copy_for_translation(monkeypatch):
    _env(monkeypatch)
    respx.post(f"{BASE}/pages/7/actions/copy_for_translation/").respond(
        200, json={"id": 90}
    )
    result = runner.invoke(
        app, ["pages", "copy-for-translation", "7", "--locale", "fr"]
    )
    assert result.exit_code == 0
    body = json.loads(respx.calls[0].request.content)
    assert body == {"locale": "fr"}


@respx.mock
def test_pages_revisions_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/7/revisions/").respond(
        200, json={"count": 1, "items": [{"id": 42}]}
    )
    result = runner.invoke(app, ["pages", "revisions", "list", "7"])
    assert result.exit_code == 0
    assert str(respx.calls[0].request.url).endswith("/pages/7/revisions/")


@respx.mock
def test_pages_revisions_get(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/pages/7/revisions/42/").respond(200, json={"id": 42, "page": 7})
    result = runner.invoke(app, ["pages", "revisions", "get", "7", "42"])
    assert result.exit_code == 0


@respx.mock
def test_pages_422_exit_7_with_problem_on_stderr(monkeypatch):
    _env(monkeypatch)
    problem = {
        "type": "about:blank",
        "title": "Unprocessable Entity",
        "status": 422,
        "detail": "Validation failed",
        "errors": [{"loc": ["title"]}],
    }
    respx.post(f"{BASE}/pages/").respond(422, json=problem)
    result = runner.invoke(
        app, ["pages", "create", "blog.BlogPage", "--parent", "3", "--title", "Bad"]
    )
    assert result.exit_code == 7
    assert "422" in result.stderr
    assert "Unprocessable Entity" in result.stderr

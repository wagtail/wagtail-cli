import respx

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


BASE = "https://x.test/api/v3"
runner = CliRunner()


def _env(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", BASE)
    monkeypatch.setenv("WAGTAIL_CLI_TOKEN", "tok")


def _png(tmp_path):
    f = tmp_path / "img.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n")
    return f


@respx.mock
def test_images_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/images/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(app, ["images", "list", "--limit", "5"])
    assert result.exit_code == 0
    assert "limit=5" in str(respx.calls[0].request.url)


@respx.mock
def test_images_get(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/images/7/").respond(200, json={"id": 7, "title": "X"})
    result = runner.invoke(app, ["images", "get", "7"])
    assert result.exit_code == 0
    assert '"id":7' in result.output


@respx.mock
def test_images_create_multipart(monkeypatch, tmp_path):
    _env(monkeypatch)
    f = _png(tmp_path)
    respx.post(f"{BASE}/images/").respond(201, json={"id": 10})
    result = runner.invoke(
        app,
        ["images", "create", str(f), "--title", "Sunset", "--field", "description:A"],
    )
    assert result.exit_code == 0
    sent = respx.calls[0].request
    assert sent.headers["content-type"].startswith("multipart/form-data")
    assert b"img.png" in sent.content
    assert b"\x89PNG" in sent.content


@respx.mock
def test_images_update_with_yes(monkeypatch):
    _env(monkeypatch)
    respx.patch(f"{BASE}/images/7/").respond(200, json={"id": 7})
    result = runner.invoke(app, ["images", "update", "7", "--title", "New", "--yes"])
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "PATCH"


def test_images_update_without_yes_non_tty(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr("wagtail_cli.cli.images._is_tty", lambda: False)
    result = runner.invoke(app, ["images", "update", "7", "--title", "New"])
    assert result.exit_code == 2
    assert "--yes" in result.stderr or "--yes" in result.output
    assert len(respx.calls) == 0


@respx.mock
def test_images_delete_with_yes(monkeypatch):
    _env(monkeypatch)
    respx.delete(f"{BASE}/images/7/").respond(204)
    result = runner.invoke(app, ["images", "delete", "7", "--yes"])
    assert result.exit_code == 0
    assert respx.calls[0].request.method == "DELETE"


@respx.mock
def test_images_create_missing_file(monkeypatch, tmp_path):
    _env(monkeypatch)
    result = runner.invoke(
        app, ["images", "create", str(tmp_path / "nope.png"), "--title", "X"]
    )
    assert result.exit_code == 2
    assert "Cannot read file" in (result.stderr or result.output)


@respx.mock
def test_images_create_dry_run_no_http(monkeypatch, tmp_path):
    _env(monkeypatch)
    f = _png(tmp_path)
    result = runner.invoke(
        app, ["--dry-run", "images", "create", str(f), "--title", "X"]
    )
    assert result.exit_code == 0
    assert len(respx.calls) == 0
    assert f"POST {BASE}/images/" in result.output


@respx.mock
def test_documents_list(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/documents/").respond(200, json={"count": 0, "items": []})
    result = runner.invoke(app, ["documents", "list"])
    assert result.exit_code == 0


@respx.mock
def test_documents_create_multipart(monkeypatch, tmp_path):
    _env(monkeypatch)
    f = tmp_path / "a.pdf"
    f.write_bytes(b"%PDF-1.4")
    respx.post(f"{BASE}/documents/").respond(201, json={"id": 12})
    result = runner.invoke(app, ["documents", "create", str(f), "--title", "Brief"])
    assert result.exit_code == 0
    sent = respx.calls[0].request
    assert sent.headers["content-type"].startswith("multipart/form-data")
    assert b"a.pdf" in sent.content


@respx.mock
def test_documents_delete_requires_yes(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr("wagtail_cli.cli.documents._is_tty", lambda: False)
    result = runner.invoke(app, ["documents", "delete", "3"])
    assert result.exit_code == 2
    assert "--yes" in result.stderr or "--yes" in result.output

import json

import httpx
import pytest
import respx

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


DOCS = "http://docs.test"
runner = CliRunner()


@pytest.fixture(autouse=True)
def docs_env(monkeypatch):
    """Point tests at the mock docs host and the stable fallback."""
    monkeypatch.setenv("WAGTAIL_CLI_DOCS_URL", DOCS)
    monkeypatch.setattr("wagtail_cli.docs.detect_wagtail_version", lambda: None)


def _index_md():
    return "# Welcome\n\nIntro.\n\n## Index\n\n* [Getting started](getting_started/index.html.md)\n"


def _reference_md():
    return """# v3 API reference

Project-specific note.

### GET /api/v3/documents/

**List documents**

### POST /api/v3/documents/

**Create document**
"""


@respx.mock
def test_docs_no_args_shows_index():
    respx.get(f"{DOCS}/en/stable/index.html.md").respond(200, text=_index_md())
    result = runner.invoke(app, ["docs"])
    assert result.exit_code == 0
    assert "Getting started" in result.output
    assert "## Index" not in result.output


@respx.mock
def test_docs_bare_path_fetches_page():
    respx.get(f"{DOCS}/en/stable/releases/8.0.html.md").respond(
        200, text="# Wagtail 8.0 release notes"
    )
    result = runner.invoke(app, ["docs", "releases/8.0"])
    assert result.exit_code == 0
    assert "Wagtail 8.0 release notes" in result.output


@respx.mock
def test_docs_full_url():
    respx.get(f"{DOCS}/en/stable/releases/8.0.html.md").respond(
        200, text="# Release notes"
    )
    result = runner.invoke(app, ["docs", f"{DOCS}/en/stable/releases/8.0.html"])
    assert result.exit_code == 0
    assert "Release notes" in result.output


@respx.mock
def test_docs_version_flag():
    respx.get(f"{DOCS}/en/7.2/topics/images.html.md").respond(200, text="# Images")
    result = runner.invoke(app, ["docs", "--version", "7.2", "topics/images.html"])
    assert result.exit_code == 0
    assert "Images" in result.output


@respx.mock
def test_docs_uses_locally_installed_wagtail_version(monkeypatch):
    monkeypatch.setattr("wagtail_cli.docs.detect_wagtail_version", lambda: "8.0")
    respx.get(f"{DOCS}/en/8.0/topics/images.html.md").respond(200, text="# Images")
    result = runner.invoke(app, ["docs", "topics/images.html"])
    assert result.exit_code == 0


@respx.mock
def test_docs_version_fallback_to_stable():
    respx.get(f"{DOCS}/en/7.2/releases/8.0.html.md").respond(404)
    respx.get(f"{DOCS}/en/stable/releases/8.0.html.md").respond(
        200, text="# Wagtail 8.0 release notes"
    )
    result = runner.invoke(app, ["docs", "--version", "7.2", "releases/8.0"])
    assert result.exit_code == 0
    assert "Wagtail 8.0 release notes" in result.output
    assert "stable" in result.stderr


@respx.mock
def test_docs_version_redirects_to_html_falls_back_to_stable():
    # Sphinx redirects missing versioned pages to an HTML index (HTTP 200).
    respx.get(f"{DOCS}/en/7.2/releases/8.0.html.md").mock(
        side_effect=[
            httpx.Response(
                302, headers={"location": f"{DOCS}/en/7.2/releases/index.html"}
            ),
        ]
    )
    respx.get(f"{DOCS}/en/7.2/releases/index.html").respond(
        200, text="<html>not found</html>", headers={"content-type": "text/html"}
    )
    respx.get(f"{DOCS}/en/stable/releases/8.0.html.md").respond(
        200, text="# Wagtail 8.0 release notes"
    )
    result = runner.invoke(app, ["docs", "--version", "7.2", "releases/8.0"])
    assert result.exit_code == 0
    assert "Wagtail 8.0 release notes" in result.output


@respx.mock
def test_docs_502_html_error_not_reported_as_not_found():
    # A server-side HTML error page must not be treated as a missing page.
    respx.get(f"{DOCS}/en/7.2/bogus.html.md").respond(
        502, text="<html>Bad gateway</html>", headers={"content-type": "text/html"}
    )
    result = runner.invoke(app, ["docs", "--version", "7.2", "bogus"])
    assert result.exit_code == 1
    assert "502" in result.stderr


@respx.mock
def test_docs_404_error_mentions_version():
    respx.get(f"{DOCS}/en/stable/bogus.html.md").respond(404)
    result = runner.invoke(app, ["docs", "bogus"])
    assert result.exit_code == 6
    assert "bogus" in result.stderr


@respx.mock
def test_docs_404_after_fallback_error_mentions_both_versions():
    respx.get(f"{DOCS}/en/7.2/bogus.html.md").respond(404)
    respx.get(f"{DOCS}/en/stable/bogus.html.md").respond(404)
    result = runner.invoke(app, ["docs", "--version", "7.2", "bogus"])
    assert result.exit_code == 6
    assert "7.2" in result.stderr
    assert "stable" in result.stderr


@respx.mock
def test_docs_language_flag():
    respx.get(f"{DOCS}/fr/stable/index.html.md").respond(200, text=_index_md())
    result = runner.invoke(app, ["docs", "--language", "fr"])
    assert result.exit_code == 0
    assert "Getting started" in result.output


@respx.mock
def test_docs_index_without_index_section_is_friendly_error():
    respx.get(f"{DOCS}/en/stable/index.html.md").respond(
        200, text="# Welcome\n\nNo index section here.\n"
    )
    result = runner.invoke(app, ["docs"])
    assert result.exit_code == 2
    assert "Index" in result.stderr


@respx.mock
def test_docs_index_version_fallback():
    respx.get(f"{DOCS}/en/7.2/index.html.md").respond(404)
    respx.get(f"{DOCS}/en/stable/index.html.md").respond(200, text=_index_md())
    result = runner.invoke(app, ["docs", "--version", "7.2"])
    assert result.exit_code == 0
    assert "Getting started" in result.output


@respx.mock
def test_docs_custom_url_flag():
    respx.get("https://pr-build.test/en/stable/index.html.md").respond(
        200, text=_index_md()
    )
    result = runner.invoke(app, ["docs", "--docs-url", "https://pr-build.test"])
    assert result.exit_code == 0
    assert "Getting started" in result.output


@respx.mock
def test_docs_custom_url_env_var(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_DOCS_URL", "https://pr-build.test")
    respx.get("https://pr-build.test/en/stable/index.html.md").respond(
        200, text=_index_md()
    )
    result = runner.invoke(app, ["docs"])
    assert result.exit_code == 0
    assert "Getting started" in result.output


@respx.mock
def test_docs_network_error():
    respx.get(f"{DOCS}/en/stable/index.html.md").mock(
        side_effect=httpx.ConnectError("nope")
    )
    result = runner.invoke(app, ["docs"])
    assert result.exit_code == 3


# --- wt docs api ---


@respx.mock
def test_docs_api_without_operation_lists_index():
    respx.get(f"{DOCS}/en/stable/advanced_topics/api/v3/reference.html.md").respond(
        200, text=_reference_md()
    )
    result = runner.invoke(app, ["docs", "api"])
    assert result.exit_code == 0
    assert "GET /api/v3/documents/" in result.output
    assert "POST /api/v3/documents/" in result.output


@respx.mock
def test_docs_api_operation_full_heading():
    respx.get(f"{DOCS}/en/stable/advanced_topics/api/v3/reference.html.md").respond(
        200, text=_reference_md()
    )
    result = runner.invoke(app, ["docs", "api", "GET", "/api/v3/documents/"])
    assert result.exit_code == 0
    assert "List documents" in result.output
    assert "Create document" not in result.output


@respx.mock
def test_docs_api_operation_lenient_query():
    respx.get(f"{DOCS}/en/stable/advanced_topics/api/v3/reference.html.md").respond(
        200, text=_reference_md()
    )
    result = runner.invoke(app, ["docs", "api", "get", "/cms-api/v3/documents"])
    assert result.exit_code == 0
    assert "List documents" in result.output


@respx.mock
def test_docs_api_ambiguous_lists_candidates():
    respx.get(f"{DOCS}/en/stable/advanced_topics/api/v3/reference.html.md").respond(
        200, text=_reference_md()
    )
    result = runner.invoke(app, ["docs", "api", "documents"])
    assert result.exit_code == 2
    assert "GET /api/v3/documents/" in result.output
    assert "POST /api/v3/documents/" in result.output


@respx.mock
def test_docs_api_not_found_hint_is_project_specific():
    respx.get(f"{DOCS}/en/stable/advanced_topics/api/v3/reference.html.md").respond(
        200, text=_reference_md()
    )
    result = runner.invoke(app, ["docs", "api", "GET", "/api/v3/bogus/"])
    assert result.exit_code == 2
    assert "project-specific" in result.output
    assert "wt docs api" in result.output


@respx.mock
def test_docs_api_reference_404():
    respx.get(f"{DOCS}/en/stable/advanced_topics/api/v3/reference.html.md").respond(404)
    result = runner.invoke(app, ["docs", "api"])
    assert result.exit_code == 6


# --- wt docs search ---


@respx.mock
def test_docs_search_concise_list():
    route = respx.get(f"{DOCS}/_/api/v3/search/").respond(
        200,
        json={
            "count": 1,
            "query": "picture",
            "results": [
                {
                    "title": "Jinja2 template support",
                    "path": "/en/stable/reference/jinja2.html",
                    "blocks": [{"title": "", "content": "Resize or convert an image."}],
                }
            ],
        },
    )
    result = runner.invoke(app, ["docs", "search", "picture"])
    assert result.exit_code == 0
    assert "1. Jinja2 template support" in result.output
    assert "/en/stable/reference/jinja2.html" in result.output
    assert "Resize or convert an image." in result.output
    assert route.called
    assert "project:wagtail/stable picture" in route.calls[0].request.url.params["q"]


@respx.mock
def test_docs_search_json_flag():
    payload = {"count": 0, "query": "zzz", "results": []}
    respx.get(f"{DOCS}/_/api/v3/search/").respond(200, json=payload)
    result = runner.invoke(app, ["docs", "search", "--json", "zzz"])
    assert result.exit_code == 0
    assert json.loads(result.output) == payload


@respx.mock
def test_docs_search_uses_version_flag(monkeypatch):
    route = respx.get(f"{DOCS}/_/api/v3/search/").respond(
        200, json={"count": 0, "query": "picture", "results": []}
    )
    monkeypatch.setattr("wagtail_cli.docs.detect_wagtail_version", lambda: "7.2")
    result = runner.invoke(app, ["docs", "search", "picture"])
    assert result.exit_code == 0
    assert "project:wagtail/7.2 picture" in route.calls[0].request.url.params["q"]
    assert "wt docs --version stable search" in result.stderr


@respx.mock
def test_docs_search_non_json_response():
    respx.get(f"{DOCS}/_/api/v3/search/").respond(
        200, text="<html>blocked</html>", headers={"content-type": "text/html"}
    )
    result = runner.invoke(app, ["docs", "search", "picture"])
    assert result.exit_code == 1
    assert "JSON" in result.stderr


@respx.mock
def test_docs_search_error():
    respx.get(f"{DOCS}/_/api/v3/search/").respond(500)
    result = runner.invoke(app, ["docs", "search", "picture"])
    assert result.exit_code == 1

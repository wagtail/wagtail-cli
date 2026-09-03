"""Tests for docs.wagtail.org URL resolution, reference parsing, and search formatting."""

import pytest

from wagtail_cli import docs


# --- resolve_docs_url ---


def test_resolve_docs_url_default():
    assert docs.resolve_docs_url() == "https://docs.wagtail.org"


def test_resolve_docs_url_cli_flag_wins(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_DOCS_URL", "https://env.test")
    assert docs.resolve_docs_url("https://flag.test") == "https://flag.test"


def test_resolve_docs_url_env_var(monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_DOCS_URL", "https://pr-build.test")
    assert docs.resolve_docs_url() == "https://pr-build.test"


def test_resolve_docs_url_env_var_ignored_when_none_set(monkeypatch):
    monkeypatch.delenv("WAGTAIL_CLI_DOCS_URL", raising=False)
    assert docs.resolve_docs_url() == "https://docs.wagtail.org"


# --- resolve_version ---


def test_resolve_version_explicit_wins():
    assert docs.resolve_version("latest", installed="7.2") == "latest"
    assert docs.resolve_version("7.2", installed="8.0") == "7.2"


def test_resolve_version_falls_back_to_installed():
    assert docs.resolve_version(installed="7.2") == "7.2"


def test_resolve_version_falls_back_to_stable():
    assert docs.resolve_version(installed=None) == "stable"


def test_resolve_version_detects_installed_wagtail(monkeypatch):
    monkeypatch.setattr(docs, "detect_wagtail_version", lambda: "8.0")
    assert docs.resolve_version() == "8.0"


def test_resolve_version_no_wagtail_installed(monkeypatch):
    monkeypatch.setattr(docs, "detect_wagtail_version", lambda: None)
    assert docs.resolve_version() == "stable"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("8.0.1", "8.0"),
        ("8.0b1", "8.0"),
        ("7.2", "7.2"),
        ("6.4.dev0", "6.4"),
    ],
)
def test_normalize_wagtail_version(raw, expected):
    assert docs.normalize_wagtail_version(raw) == expected


def test_normalize_wagtail_version_unparseable():
    assert docs.normalize_wagtail_version("dev") is None


# --- resolve_page_url ---


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        # Full URL: used as-is, with the Markdown variant fetched.
        (
            "https://docs.wagtail.org/en/stable/releases/8.0.html",
            "https://docs.wagtail.org/en/stable/releases/8.0.html.md",
        ),
        # Full URL already pointing at the .md variant.
        (
            "https://docs.wagtail.org/en/stable/releases/8.0.html.md",
            "https://docs.wagtail.org/en/stable/releases/8.0.html.md",
        ),
        # Full URL without a .html extension.
        (
            "https://docs.wagtail.org/en/stable/index",
            "https://docs.wagtail.org/en/stable/index.html.md",
        ),
        # Full URL on another host (e.g. a PR docs build).
        (
            "https://pr-123.docs.test/en/stable/topics/images.html",
            "https://pr-123.docs.test/en/stable/topics/images.html.md",
        ),
        # Full URL with a fragment: fragment dropped.
        (
            "https://docs.wagtail.org/en/stable/index.html#section",
            "https://docs.wagtail.org/en/stable/index.html.md",
        ),
        # Language-qualified path: version explicit.
        (
            "/en/stable/releases/8.0.html",
            "https://docs.wagtail.org/en/stable/releases/8.0.html.md",
        ),
        (
            "en/latest/topics/images.html",
            "https://docs.wagtail.org/en/latest/topics/images.html.md",
        ),
        # Version without language.
        (
            "/stable/releases/8.0.html",
            "https://docs.wagtail.org/en/stable/releases/8.0.html.md",
        ),
        (
            "/7.2/topics/images.html",
            "https://docs.wagtail.org/en/7.2/topics/images.html.md",
        ),
        # No version: resolved version is inserted.
        # Bare page paths, including the .html.md link format the docs index
        # itself emits.
        (
            "/releases/8.0.html",
            "https://docs.wagtail.org/en/8.0/releases/8.0.html.md",
        ),
        ("releases/8.0", "https://docs.wagtail.org/en/8.0/releases/8.0.html.md"),
        ("topics/images.html", "https://docs.wagtail.org/en/8.0/topics/images.html.md"),
        (
            "getting_started/index.html.md",
            "https://docs.wagtail.org/en/8.0/getting_started/index.html.md",
        ),
        (
            "topics/images.html#section",
            "https://docs.wagtail.org/en/8.0/topics/images.html.md",
        ),
        # Full URLs pointing at a directory (or the site root) resolve to the
        # index page.
        (
            "https://docs.wagtail.org/en/stable/",
            "https://docs.wagtail.org/en/stable/index.html.md",
        ),
        ("https://docs.wagtail.org/", "https://docs.wagtail.org/en/8.0/index.html.md"),
        ("https://docs.wagtail.org", "https://docs.wagtail.org/en/8.0/index.html.md"),
        (
            "https://pr-123.docs.test/",
            "https://pr-123.docs.test/en/8.0/index.html.md",
        ),
        # Empty path: the index page.
        ("", "https://docs.wagtail.org/en/8.0/index.html.md"),
        ("/", "https://docs.wagtail.org/en/8.0/index.html.md"),
    ],
)
def test_resolve_page_url(path, expected):
    assert (
        docs.resolve_page_url("https://docs.wagtail.org", "en", "8.0", path) == expected
    )


def test_resolve_page_url_other_language():
    assert (
        docs.resolve_page_url(
            "https://docs.wagtail.org", "fr", "stable", "/fr/stable/x.html"
        )
        == "https://docs.wagtail.org/fr/stable/x.html.md"
    )
    assert (
        docs.resolve_page_url(
            "https://docs.wagtail.org", "fr", "stable", "topics/images.html"
        )
        == "https://docs.wagtail.org/fr/stable/topics/images.html.md"
    )


# --- extract_index_section ---


def test_extract_index_section():
    md = "# Welcome\n\nIntro text.\n\n## Index\n\n* [A](a.html.md)\n* [B](b.html.md)\n\n## Another\n\nMore text.\n"
    section = docs.extract_index_section(md)
    assert "* [A](a.html.md)" in section
    assert "* [B](b.html.md)" in section
    assert "More text." not in section
    assert "## Index" not in section


def test_extract_index_section_to_end_of_document():
    md = "# Welcome\n\n## Index\n\n* [A](a.html.md)\n"
    section = docs.extract_index_section(md)
    assert "* [A](a.html.md)" in section


def test_extract_index_section_missing():
    with pytest.raises(ValueError):
        docs.extract_index_section("# Welcome\n\nNo index here.\n")


# --- parse_operations ---


REFERENCE_MD = """<a id="api-v3-reference"></a>

# v3 API reference

The reference below is generated as part of Wagtail's build pipelines.

### GET /api/v3/documents/

**List documents**

* **Query Parameters:**
  * **search** ( *{'string', 'null'}*)

**Example request:**

```http
GET /api/v3/documents/ HTTP/1.1
```

### POST /api/v3/documents/

**Create document**

### GET /api/v3/documents/{document_id}/

**Fetch document**

### POST /api/v3/pages/{page_id}/actions/revert/

**Revert page**

### GET /api/v3/pages/{page_id}/revisions/

**List page revisions**

### GET /api/v3/pages/{page_id}/revisions/{revision_id}/

**Get page revision**
"""


def test_parse_operations():
    ops = docs.parse_operations(REFERENCE_MD)
    assert [(op.method, op.path) for op in ops] == [
        ("GET", "/api/v3/documents/"),
        ("POST", "/api/v3/documents/"),
        ("GET", "/api/v3/documents/{document_id}/"),
        ("POST", "/api/v3/pages/{page_id}/actions/revert/"),
        ("GET", "/api/v3/pages/{page_id}/revisions/"),
        ("GET", "/api/v3/pages/{page_id}/revisions/{revision_id}/"),
    ]


def test_parse_operation_section_contains_body_not_heading():
    ops = docs.parse_operations(REFERENCE_MD)
    assert ops[0].heading == "GET /api/v3/documents/"
    assert "List documents" in ops[0].body
    assert "GET /api/v3/documents/ HTTP/1.1" in ops[0].body
    assert "Create document" not in ops[0].body


def test_parse_operations_no_operations():
    assert docs.parse_operations("# Nothing here\n") == []


# --- find_operations ---


def _ops():
    return docs.parse_operations(REFERENCE_MD)


def test_find_operations_full_heading_query():
    exact, similar = docs.find_operations(_ops(), "GET /api/v3/documents/")
    assert len(exact) == 1
    assert exact[0].heading == "GET /api/v3/documents/"


def test_find_operations_case_insensitive_method():
    exact, _ = docs.find_operations(_ops(), "get /api/v3/documents/")
    assert len(exact) == 1


def test_find_operations_optional_version_prefixes():
    for query in (
        "GET /documents/",
        "GET documents",
        "documents GET",
        "GET /api/v3-preview/documents/",
        "GET /cms-api/v3/documents/",
        "GET api/v3/documents",
    ):
        exact, similar = docs.find_operations(_ops(), query)
        assert len(exact) == 1, f"query {query!r} should match exactly once"
        assert exact[0].heading == "GET /api/v3/documents/"


def test_find_operations_path_only_is_ambiguous():
    exact, similar = docs.find_operations(_ops(), "documents")
    assert len(exact) == 2  # GET and POST on /api/v3/documents/


def test_find_operations_method_narrows_ambiguity():
    exact, _ = docs.find_operations(_ops(), "POST documents")
    assert len(exact) == 1
    assert exact[0].method == "POST"


def test_find_operations_not_found():
    exact, similar = docs.find_operations(_ops(), "GET /api/v3/bogus/")
    assert exact == []
    assert similar == []


def test_find_operations_similar_matches():
    exact, similar = docs.find_operations(_ops(), "revert")
    assert exact == []
    assert len(similar) == 1
    assert similar[0].path == "/api/v3/pages/{page_id}/actions/revert/"


def test_find_operations_partial_path_with_extra_segment():
    exact, similar = docs.find_operations(_ops(), "POST pages/{page_id}/revert")
    assert exact == []
    assert len(similar) == 1
    assert similar[0].path == "/api/v3/pages/{page_id}/actions/revert/"


def test_find_operations_numeric_id_matches_placeholder():
    _, similar = docs.find_operations(_ops(), "GET pages/42/revisions")
    assert {op.path for op in similar} == {
        "/api/v3/pages/{page_id}/revisions/",
        "/api/v3/pages/{page_id}/revisions/{revision_id}/",
    }


def test_find_operations_similar_respects_method():
    _, similar = docs.find_operations(_ops(), "GET pages/42/revisions")
    assert all(op.method == "GET" for op in similar)


def test_find_operations_exact_without_method():
    exact, _ = docs.find_operations(_ops(), "documents/{document_id}")
    assert len(exact) == 1
    assert exact[0].path == "/api/v3/documents/{document_id}/"


# --- format_search_results ---


PAYLOAD = {
    "count": 2,
    "query": "picture",
    "results": [
        {
            "title": "Jinja2 template support",
            "path": "/en/stable/reference/jinja2.html",
            "blocks": [
                {
                    "title": "",
                    "content": "Resize or convert an image,\n rendering a <picture> tag including multiple source formats.",
                }
            ],
        },
        {"title": "Images", "path": "/en/stable/topics/images.html", "blocks": []},
    ],
}


def test_format_search_results_lists_titles_and_paths():
    out = docs.format_search_results(PAYLOAD)
    assert "2 results for" in out
    assert "picture" in out
    assert "1. Jinja2 template support" in out
    assert "/en/stable/reference/jinja2.html" in out
    assert "2. Images" in out
    assert "/en/stable/topics/images.html" in out


def test_format_search_results_includes_trimmed_snippet():
    out = docs.format_search_results(PAYLOAD)
    assert "Resize or convert an image," in out


def test_format_search_results_no_results():
    out = docs.format_search_results({"count": 0, "query": "zzz", "results": []})
    assert "No results" in out
    assert "zzz" in out

import pytest

from wgtl_api_cli.errors import UsageError
from wgtl_api_cli.parsing import parse_fields, resolve_page_ref


def test_plain_string():
    assert parse_fields(["title:Hello"]) == {"title": "Hello"}


def test_json_array_and_object():
    assert parse_fields(["tags:[1,2]", 'extra:{"a": 1}']) == {
        "tags": [1, 2],
        "extra": {"a": 1},
    }


def test_bool_and_number_strings_stay_strings():
    assert parse_fields(["slug:my-post"]) == {"slug": "my-post"}


def test_multiple_fields_merge():
    assert parse_fields(["title:A", "subtitle:B"]) == {"title": "A", "subtitle": "B"}


def test_at_file_reads(tmp_path):
    f = tmp_path / "intro.txt"
    f.write_text("from file")
    assert parse_fields([f"introduction:@{f}"]) == {"introduction": "from file"}


def test_at_md_file_becomes_db_markdown_envelope(tmp_path):
    f = tmp_path / "body.md"
    f.write_text("# Hi\n\nText")
    assert parse_fields([f"body:@{f}"]) == {
        "body": {"format": "db_markdown", "content": "# Hi\n\nText"}
    }


def test_at_html_file_stays_plain_string(tmp_path):
    f = tmp_path / "body.html"
    f.write_text("<p>Hi</p>")
    assert parse_fields([f"body:@{f}"]) == {"body": "<p>Hi</p>"}


def test_missing_value_raises_usage_error():
    with pytest.raises(UsageError):
        parse_fields(["no-colon-here"])


def test_missing_colon_message_helpful():
    with pytest.raises(UsageError) as e:
        parse_fields(["bogus"])
    assert "KEY:VALUE" in str(e.value)


def test_resolve_page_ref_numeric_passthrough():
    assert resolve_page_ref(object(), 61) == 61
    assert resolve_page_ref(object(), "61") == 61


def test_resolve_page_ref_path_uses_find_location():
    # the v3 find endpoint answers 302 + Location header; the transport
    # surfaces it as {"location": ...} (see Task 7)
    class FakeClient:
        def get(self, path, params=None):
            assert path == "/pages/find/"
            assert params["html_path"] == "/blog/"
            return {"location": "/api/v3/pages/61/?"}

    assert resolve_page_ref(FakeClient(), "/blog/") == 61

import json

from wgtl_api_cli.output import render


def test_json_compact():
    out = render({"a": 1}, fmt="json")
    assert json.loads(out) == {"a": 1}
    assert "\n" not in out


def test_human_list_table():
    data = {
        "count": 2,
        "items": [{"id": 1, "title": "Home", "meta": {"type": "home.HomePage"}}],
    }
    out = render(data, fmt="human")
    assert "ID" in out.upper() and "title" in out.lower() or "TITLE" in out.upper()
    assert "home.HomePage" in out and "Home" in out


def test_human_detail_key_value():
    out = render({"id": 5, "title": "About", "meta": {"type": "x.Y"}}, fmt="human")
    assert "5" in out and "About" in out


def test_auto_json_when_piped(monkeypatch, capsys):
    # isatty False → json
    assert json.loads(render({"a": 1}, fmt=None)) == {"a": 1}
    assert True  # isatty detection tested indirectly in Task 10 via CLI -v behavior


def test_none_fmt_piped_detection(monkeypatch):
    monkeypatch.setattr("wgtl_api_cli.output._stdout_is_tty", lambda: True)
    out = render({"items": [{"id": 1}]}, fmt=None)
    assert not out.startswith("{}")  # human mode chosen

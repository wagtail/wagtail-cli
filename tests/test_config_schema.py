"""Tests for the published .wagtail-cli.toml JSON Schema."""

import json
import tomllib

from pathlib import Path

from wagtail_cli.config import SCHEMA_URL, Config, save_user_config


SCHEMA_PATH = Path(__file__).parent.parent / "docs" / "schema" / "wagtail-cli.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_declares_only_known_keys():
    schema = _load_schema()
    assert schema["type"] == "object"
    # Unknown keys must be rejected so typos are caught in editors.
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"url", "token"}


def test_schema_covers_every_key_the_cli_reads():
    """The schema and ``load_config`` must not drift apart."""
    from wagtail_cli import config

    source = Path(config.__file__).read_text(encoding="utf-8")
    for key in _load_schema()["properties"]:
        assert f'data.get("{key}"' in source


def test_schema_url_is_absolute_and_matches_id():
    schema = _load_schema()
    assert schema["$id"].startswith("https://")
    assert SCHEMA_URL == schema["$id"]


def test_serialized_config_matches_schema(tmp_path):
    path = tmp_path / ".wagtail-cli.toml"
    save_user_config(Config(base_url="https://x.test/api/v3/", token="t"), path=path)
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    schema = _load_schema()
    assert set(data) <= set(schema["properties"])
    for key, value in data.items():
        assert schema["properties"][key]["type"] == "string"
        assert isinstance(value, str)

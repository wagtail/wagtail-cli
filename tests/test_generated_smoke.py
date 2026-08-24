"""Smoke test for the clientele-generated client.

Guards against a botched `just generate-client` regen. The generated
package is never hand-edited; this test only verifies it imports and
exposes the expected surface.
"""

from pathlib import Path

from wagtail_cli.client import client, schemas


SNAPSHOT = Path(__file__).parent.parent / "src/wagtail_cli/client/openapi.json"


def test_page_type_schema_present():
    # A page-type schema class must exist (per-project types are in the schema).
    assert hasattr(schemas, "BlogPageSchema")


def test_client_exposes_all_operations():
    # The live schema has 58 path×method operations; every one is generated
    # as a function on the client. Generous floor guards against truncation.
    ops = [n for n in dir(client) if not n.startswith("_")]
    assert len(ops) >= 50


def test_snapshot_file_present():
    # The committed OpenAPI snapshot must exist for regeneration.
    assert SNAPSHOT.is_file()

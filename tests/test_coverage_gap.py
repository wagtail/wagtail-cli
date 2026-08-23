"""OpenAPI coverage-gap check.

Drift detector between the committed v3 OpenAPI schema snapshot
(``src/wgtl_api_cli/client/openapi.json``) and the CLI command surface.

* A schema operation with no mapping row fails — we shipped an API endpoint
  with no CLI command.
* A mapping row with no schema operation fails — the CLI exposes a command
  that no longer exists in the API (a stale command after the API changed).
"""

from __future__ import annotations

import json

from pathlib import Path


SCHEMA_PATH = (
    Path(__file__).parent / ".." / "src" / "wgtl_api_cli" / "client" / "openapi.json"
)

# (HTTP_METHOD, path_prefix) -> human CLI invocation.
# path_prefix uses the OpenAPI path template placeholders ({page_id}, {type},
# {pk}, {type_name}) verbatim. The command column documents which command
# covers the operation (for humans); the test only asserts the key is mapped.
MAPPING: dict[tuple[str, str], str] = {
    # whoami
    ("GET", "/api/v3/whoami/"): "wgtl whoami",
    # schema
    ("GET", "/api/v3/schema/"): "wgtl schema list",
    ("GET", "/api/v3/schema/{type_name}/"): "wgtl schema show <type>",
    # pages (CRUD + find)
    ("GET", "/api/v3/pages/"): "wgtl pages list",
    ("POST", "/api/v3/pages/"): "wgtl pages create",
    ("GET", "/api/v3/pages/find/"): "wgtl pages find",
    ("GET", "/api/v3/pages/{page_id}/"): "wgtl pages get",
    ("PATCH", "/api/v3/pages/{page_id}/"): "wgtl pages update",
    ("DELETE", "/api/v3/pages/{page_id}/"): "wgtl pages delete",
    # pages actions
    ("POST", "/api/v3/pages/{page_id}/actions/publish/"): "wgtl pages publish",
    ("POST", "/api/v3/pages/{page_id}/actions/unpublish/"): "wgtl pages unpublish",
    ("POST", "/api/v3/pages/{page_id}/actions/copy/"): "wgtl pages copy",
    ("POST", "/api/v3/pages/{page_id}/actions/move/"): "wgtl pages move",
    ("POST", "/api/v3/pages/{page_id}/actions/revert/"): "wgtl pages revert",
    (
        "POST",
        "/api/v3/pages/{page_id}/actions/create_alias/",
    ): "wgtl pages create-alias",
    (
        "POST",
        "/api/v3/pages/{page_id}/actions/convert_alias/",
    ): "wgtl pages convert-alias",
    (
        "POST",
        "/api/v3/pages/{page_id}/actions/copy_for_translation/",
    ): "wgtl pages copy-for-translation",
    (
        "DELETE",
        "/api/v3/pages/{page_id}/actions/delete/",
    ): "wgtl pages delete (canonical delete action)",
    # page revisions
    ("GET", "/api/v3/pages/{page_id}/revisions/"): "wgtl pages revisions list",
    (
        "GET",
        "/api/v3/pages/{page_id}/revisions/{revision_id}/",
    ): "wgtl pages revisions get",
    # images
    ("GET", "/api/v3/images/"): "wgtl images list",
    ("POST", "/api/v3/images/"): "wgtl images create",
    ("GET", "/api/v3/images/{image_id}/"): "wgtl images get",
    ("PATCH", "/api/v3/images/{image_id}/"): "wgtl images update",
    ("DELETE", "/api/v3/images/{image_id}/"): "wgtl images delete",
    # documents
    ("GET", "/api/v3/documents/"): "wgtl documents list",
    ("POST", "/api/v3/documents/"): "wgtl documents create",
    ("GET", "/api/v3/documents/{document_id}/"): "wgtl documents get",
    ("PATCH", "/api/v3/documents/{document_id}/"): "wgtl documents update",
    ("DELETE", "/api/v3/documents/{document_id}/"): "wgtl documents delete",
    # snippets (type-parameterized CRUD + actions + revisions)
    ("GET", "/api/v3/snippets/{type}/"): "wgtl snippets list",
    ("POST", "/api/v3/snippets/{type}/"): "wgtl snippets create",
    ("GET", "/api/v3/snippets/{type}/{pk}/"): "wgtl snippets get",
    ("PATCH", "/api/v3/snippets/{type}/{pk}/"): "wgtl snippets update",
    ("DELETE", "/api/v3/snippets/{type}/{pk}/"): "wgtl snippets delete",
    ("POST", "/api/v3/snippets/{type}/{pk}/actions/publish/"): "wgtl snippets publish",
    (
        "POST",
        "/api/v3/snippets/{type}/{pk}/actions/unpublish/",
    ): "wgtl snippets unpublish",
    ("POST", "/api/v3/snippets/{type}/{pk}/actions/revert/"): "wgtl snippets revert",
    (
        "POST",
        "/api/v3/snippets/{type}/{pk}/actions/copy_for_translation/",
    ): "wgtl snippets copy-for-translation",
    ("GET", "/api/v3/snippets/{type}/{pk}/revisions/"): "wgtl snippets revisions list",
    (
        "GET",
        "/api/v3/snippets/{type}/{pk}/revisions/{revision_id}/",
    ): "wgtl snippets revisions get",
    (
        "DELETE",
        "/api/v3/snippets/{type}/{pk}/actions/delete/",
    ): "wgtl snippets delete (canonical delete action)",
    # sites
    ("GET", "/api/v3/sites/"): "wgtl sites list",
    ("POST", "/api/v3/sites/"): "wgtl sites create",
    ("GET", "/api/v3/sites/{site_id}/"): "wgtl sites get",
    ("PUT", "/api/v3/sites/{site_id}/"): "wgtl sites update",
    ("DELETE", "/api/v3/sites/{site_id}/"): "wgtl sites delete",
    # locales
    ("GET", "/api/v3/locales/"): "wgtl locales list",
    ("POST", "/api/v3/locales/"): "wgtl locales create",
    ("GET", "/api/v3/locales/{locale_id}/"): "wgtl locales get",
    ("PUT", "/api/v3/locales/{locale_id}/"): "wgtl locales update",
    ("DELETE", "/api/v3/locales/{locale_id}/"): "wgtl locales delete",
    # redirects (CRUD + find)
    ("GET", "/api/v3/redirects/"): "wgtl redirects list",
    ("POST", "/api/v3/redirects/"): "wgtl redirects create",
    ("GET", "/api/v3/redirects/find/"): "wgtl redirects find",
    ("GET", "/api/v3/redirects/{redirect_id}/"): "wgtl redirects get",
    ("PUT", "/api/v3/redirects/{redirect_id}/"): "wgtl redirects update",
    ("DELETE", "/api/v3/redirects/{redirect_id}/"): "wgtl redirects delete",
}


def _load_schema_ops() -> set[tuple[str, str]]:
    data = json.loads(SCHEMA_PATH.read_text())
    ops: set[tuple[str, str]] = set()
    for path, methods in data["paths"].items():
        for method in methods:
            ops.add((method.upper(), path))
    return ops


def test_every_schema_operation_is_mapped() -> None:
    schema_ops = _load_schema_ops()
    unmapped = schema_ops - set(MAPPING.keys())
    assert not unmapped, (
        f"{len(unmapped)} schema operation(s) have no CLI command; add rows to "
        f"MAPPING in {__file__}: {sorted(unmapped)}"
    )


def test_every_mapping_operation_exists_in_schema() -> None:
    schema_ops = _load_schema_ops()
    stale = set(MAPPING.keys()) - schema_ops
    assert not stale, (
        f"{len(stale)} mapping row(s) reference operations absent from the "
        f"schema snapshot (stale commands): {sorted(stale)}"
    )


def test_schema_snapshot_has_no_unmapped_extra_operations() -> None:
    # Explicitly documents the total count so schema changes force a conscious
    # review of the mapping table.
    assert len(_load_schema_ops()) == len(MAPPING) == 58

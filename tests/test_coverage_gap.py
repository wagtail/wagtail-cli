"""OpenAPI coverage-gap check.

Drift detector between the committed v3 OpenAPI schema snapshot
(``tests/clientele_client/openapi.json``) and the CLI command surface.

* A schema operation with no mapping row fails — we shipped an API endpoint
  with no CLI command.
* A mapping row with no schema operation fails — the CLI exposes a command
  that no longer exists in the API (a stale command after the API changed).
"""

from __future__ import annotations

import json

from pathlib import Path


SCHEMA_PATH = Path(__file__).parent / "clientele_client" / "openapi.json"

# (HTTP_METHOD, path_prefix) -> human CLI invocation.
# path_prefix uses the OpenAPI path template placeholders ({page_id}, {type},
# {pk}, {type_name}) verbatim. The command column documents which command
# covers the operation (for humans); the test only asserts the key is mapped.
MAPPING: dict[tuple[str, str], str] = {
    # whoami
    ("GET", "/api/v3/whoami/"): "wt api whoami",
    # schema
    ("GET", "/api/v3/schema/"): "wt api schema list",
    ("GET", "/api/v3/schema/{type_name}/"): "wt api schema show <type>",
    # pages (CRUD + find)
    ("GET", "/api/v3/pages/"): "wt api pages list",
    ("POST", "/api/v3/pages/"): "wt api pages create",
    ("GET", "/api/v3/pages/find/"): "wt api pages find",
    ("GET", "/api/v3/pages/{page_id}/"): "wt api pages get",
    ("PATCH", "/api/v3/pages/{page_id}/"): "wt api pages update",
    ("DELETE", "/api/v3/pages/{page_id}/"): "wt api pages delete",
    # pages actions
    ("POST", "/api/v3/pages/{page_id}/actions/publish/"): "wt api pages publish",
    ("POST", "/api/v3/pages/{page_id}/actions/unpublish/"): "wt api pages unpublish",
    ("POST", "/api/v3/pages/{page_id}/actions/copy/"): "wt api pages copy",
    ("POST", "/api/v3/pages/{page_id}/actions/move/"): "wt api pages move",
    ("POST", "/api/v3/pages/{page_id}/actions/revert/"): "wt api pages revert",
    (
        "POST",
        "/api/v3/pages/{page_id}/actions/create_alias/",
    ): "wt api pages create-alias",
    (
        "POST",
        "/api/v3/pages/{page_id}/actions/convert_alias/",
    ): "wt api pages convert-alias",
    (
        "POST",
        "/api/v3/pages/{page_id}/actions/copy_for_translation/",
    ): "wt api pages copy-for-translation",
    (
        "DELETE",
        "/api/v3/pages/{page_id}/actions/delete/",
    ): "wt api pages delete (canonical delete action)",
    # page revisions
    ("GET", "/api/v3/pages/{page_id}/revisions/"): "wt api pages revisions list",
    (
        "GET",
        "/api/v3/pages/{page_id}/revisions/{revision_id}/",
    ): "wt api pages revisions get",
    # images
    ("GET", "/api/v3/images/"): "wt api images list",
    ("POST", "/api/v3/images/"): "wt api images create",
    ("GET", "/api/v3/images/{image_id}/"): "wt api images get",
    ("PATCH", "/api/v3/images/{image_id}/"): "wt api images update",
    ("DELETE", "/api/v3/images/{image_id}/"): "wt api images delete",
    # documents
    ("GET", "/api/v3/documents/"): "wt api documents list",
    ("POST", "/api/v3/documents/"): "wt api documents create",
    ("GET", "/api/v3/documents/{document_id}/"): "wt api documents get",
    ("PATCH", "/api/v3/documents/{document_id}/"): "wt api documents update",
    ("DELETE", "/api/v3/documents/{document_id}/"): "wt api documents delete",
    # snippets (type-parameterized CRUD + actions + revisions)
    ("GET", "/api/v3/snippets/{type}/"): "wt api snippets list",
    ("POST", "/api/v3/snippets/{type}/"): "wt api snippets create",
    ("GET", "/api/v3/snippets/{type}/{pk}/"): "wt api snippets get",
    ("PATCH", "/api/v3/snippets/{type}/{pk}/"): "wt api snippets update",
    ("DELETE", "/api/v3/snippets/{type}/{pk}/"): "wt api snippets delete",
    (
        "POST",
        "/api/v3/snippets/{type}/{pk}/actions/publish/",
    ): "wt api snippets publish",
    (
        "POST",
        "/api/v3/snippets/{type}/{pk}/actions/unpublish/",
    ): "wt api snippets unpublish",
    ("POST", "/api/v3/snippets/{type}/{pk}/actions/revert/"): "wt api snippets revert",
    (
        "POST",
        "/api/v3/snippets/{type}/{pk}/actions/copy_for_translation/",
    ): "wt api snippets copy-for-translation",
    (
        "GET",
        "/api/v3/snippets/{type}/{pk}/revisions/",
    ): "wt api snippets revisions list",
    (
        "GET",
        "/api/v3/snippets/{type}/{pk}/revisions/{revision_id}/",
    ): "wt api snippets revisions get",
    (
        "DELETE",
        "/api/v3/snippets/{type}/{pk}/actions/delete/",
    ): "wt api snippets delete (canonical delete action)",
    # sites
    ("GET", "/api/v3/sites/"): "wt api sites list",
    ("POST", "/api/v3/sites/"): "wt api sites create",
    ("GET", "/api/v3/sites/{site_id}/"): "wt api sites get",
    ("PUT", "/api/v3/sites/{site_id}/"): "wt api sites update",
    ("DELETE", "/api/v3/sites/{site_id}/"): "wt api sites delete",
    # locales
    ("GET", "/api/v3/locales/"): "wt api locales list",
    ("POST", "/api/v3/locales/"): "wt api locales create",
    ("GET", "/api/v3/locales/{locale_id}/"): "wt api locales get",
    ("PUT", "/api/v3/locales/{locale_id}/"): "wt api locales update",
    ("DELETE", "/api/v3/locales/{locale_id}/"): "wt api locales delete",
    # redirects (CRUD + find)
    ("GET", "/api/v3/redirects/"): "wt api redirects list",
    ("POST", "/api/v3/redirects/"): "wt api redirects create",
    ("GET", "/api/v3/redirects/find/"): "wt api redirects find",
    ("GET", "/api/v3/redirects/{redirect_id}/"): "wt api redirects get",
    ("PUT", "/api/v3/redirects/{redirect_id}/"): "wt api redirects update",
    ("DELETE", "/api/v3/redirects/{redirect_id}/"): "wt api redirects delete",
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

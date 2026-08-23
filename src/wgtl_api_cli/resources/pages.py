from __future__ import annotations

from typing import Any


def build_page_payload(
    *,
    type_name: str | None = None,
    parent_id: int | None = None,
    title: str | None = None,
    slug: str | None = None,
    fields: dict | None = None,
    publish: bool = False,
    for_create: bool = True,
) -> dict:
    """Build a page create/update request body.

    For creates, the v3 API requires a ``meta`` object with ``type`` and
    ``parent_id`` (both required). ``meta.action == "publish"`` publishes the
    just-created revision. All other fields land at the top level.
    """
    fields = fields or {}
    if for_create:
        meta: dict[str, Any] = {"type": type_name, "parent_id": parent_id}
        if publish:
            meta["action"] = "publish"
        payload: dict[str, Any] = {"meta": meta, "title": title}
        if slug:
            payload["slug"] = slug
        payload.update(fields)
        return payload

    # update (PATCH) — PATCH semantics, send only what is provided
    payload = {}
    if title:
        payload["title"] = title
    if slug:
        payload["slug"] = slug
    payload.update(fields)
    return payload


def list_pages(
    client,
    *,
    type=None,
    ancestor_of=None,
    child_of=None,
    descendant_of=None,
    translation_of=None,
    locale=None,
    site=None,
    search=None,
    search_operator=None,
    order=None,
    limit=None,
    offset=None,
) -> dict:
    params = {
        "type": type,
        "ancestor_of": ancestor_of,
        "child_of": child_of,
        "descendant_of": descendant_of,
        "translation_of": translation_of,
        "locale": locale,
        "site": site,
        "search": search,
        "search_operator": search_operator,
        "order": order,
        "limit": limit,
        "offset": offset,
    }
    return client.get("/pages/", params=params)


def find_page(client, *, html_path=None, id=None, site=None) -> dict:
    return client.get(
        "/pages/find/",
        params={"id": id, "html_path": html_path, "site": site},
    )


def get_page(client, page_id, *, version=None, rich_text_format=None) -> dict:
    return client.get(
        f"/pages/{page_id}/",
        params={"version": version, "rich_text_format": rich_text_format},
    )


def create_page(client, payload) -> dict:
    return client.post("/pages/", body=payload)


def update_page(client, page_id, payload) -> dict:
    return client.patch(f"/pages/{page_id}/", body=payload)


def delete_page(client, page_id) -> dict:
    return client.delete(f"/pages/{page_id}/")


def publish_page(client, page_id) -> dict:
    return client.post(f"/pages/{page_id}/actions/publish/")


def unpublish_page(client, page_id) -> dict:
    return client.post(f"/pages/{page_id}/actions/unpublish/")


def copy_page(
    client,
    page_id,
    *,
    destination_id,
    slug=None,
    title=None,
    recursive=None,
    keep_live=None,
) -> dict:
    body: dict[str, Any] = {"destination_id": destination_id}
    if slug is not None:
        body["slug"] = slug
    if title is not None:
        body["title"] = title
    if recursive is not None:
        body["recursive"] = recursive
    if keep_live is not None:
        body["keep_live"] = keep_live
    return client.post(f"/pages/{page_id}/actions/copy/", body=body)


def move_page(client, page_id, *, destination_id) -> dict:
    return client.post(
        f"/pages/{page_id}/actions/move/",
        body={"destination_id": destination_id},
    )


def revert_page(client, page_id, *, revision_id) -> dict:
    return client.post(
        f"/pages/{page_id}/actions/revert/", body={"revision_id": revision_id}
    )


def create_alias(client, page_id, *, destination_id) -> dict:
    return client.post(
        f"/pages/{page_id}/actions/create_alias/",
        body={"destination_id": destination_id},
    )


def convert_alias(client, page_id) -> dict:
    return client.post(f"/pages/{page_id}/actions/convert_alias/")


def copy_for_translation(client, page_id, *, locale) -> dict:
    return client.post(
        f"/pages/{page_id}/actions/copy_for_translation/",
        body={"locale": locale},
    )


def list_revisions(client, page_id, *, limit=None, offset=None) -> dict:
    return client.get(
        f"/pages/{page_id}/revisions/",
        params={"limit": limit, "offset": offset},
    )


def get_revision(client, page_id, revision_id) -> dict:
    return client.get(f"/pages/{page_id}/revisions/{revision_id}/")

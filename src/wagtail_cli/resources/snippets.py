from __future__ import annotations


def list_snippets(
    client,
    type,
    *,
    locale=None,
    translation_of=None,
    search=None,
    search_operator=None,
    order=None,
    limit=None,
    offset=None,
) -> dict:
    """List snippets of a type, with optional filters/ordering/pagination."""
    params = {
        "locale": locale,
        "translation_of": translation_of,
        "search": search,
        "search_operator": search_operator,
        "order": order,
        "limit": limit,
        "offset": offset,
    }
    return client.get(f"/snippets/{type}/", params=params)


def get_snippet(client, type, pk) -> dict:
    return client.get(f"/snippets/{type}/{pk}/")


def create_snippet(client, type, body: dict) -> dict:
    return client.post(f"/snippets/{type}/", body=body)


def update_snippet(client, type, pk, body: dict) -> dict:
    return client.patch(f"/snippets/{type}/{pk}/", body=body)


def delete_snippet(client, type, pk) -> dict:
    return client.delete(f"/snippets/{type}/{pk}/")


def publish_snippet(client, type, pk) -> dict:
    return client.post(f"/snippets/{type}/{pk}/actions/publish/")


def unpublish_snippet(client, type, pk) -> dict:
    return client.post(f"/snippets/{type}/{pk}/actions/unpublish/")


def revert_snippet(client, type, pk, *, revision_id) -> dict:
    return client.post(
        f"/snippets/{type}/{pk}/actions/revert/", body={"revision_id": revision_id}
    )


def copy_snippet_for_translation(client, type, pk, *, locale) -> dict:
    return client.post(
        f"/snippets/{type}/{pk}/actions/copy_for_translation/",
        body={"locale": locale},
    )


def list_snippet_revisions(client, type, pk, *, limit=None, offset=None) -> dict:
    return client.get(
        f"/snippets/{type}/{pk}/revisions/",
        params={"limit": limit, "offset": offset},
    )


def get_snippet_revision(client, type, pk, revision_id) -> dict:
    return client.get(f"/snippets/{type}/{pk}/revisions/{revision_id}/")

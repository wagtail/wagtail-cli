from __future__ import annotations

from pathlib import Path


def list_documents(
    client,
    *,
    search=None,
    search_operator=None,
    order=None,
    limit=None,
    offset=None,
) -> dict:
    return client.get(
        "/documents/",
        params={
            "search": search,
            "search_operator": search_operator,
            "order": order,
            "limit": limit,
            "offset": offset,
        },
    )


def get_document(client, document_id) -> dict:
    return client.get(f"/documents/{document_id}/")


def create_document(
    client,
    *,
    file: Path,
    title: str,
    fields: dict | None = None,
) -> dict:
    """Upload a new document (multipart/form-data)."""
    body = {"title": title, **(fields or {})}
    return client.upload("/documents/", body, "file", file)


def update_document(client, document_id, body: dict) -> dict:
    return client.patch(f"/documents/{document_id}/", body=body)


def delete_document(client, document_id) -> dict:
    return client.delete(f"/documents/{document_id}/")

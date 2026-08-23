from __future__ import annotations

from pathlib import Path


def list_images(
    client,
    *,
    search=None,
    search_operator=None,
    order=None,
    limit=None,
    offset=None,
) -> dict:
    return client.get(
        "/images/",
        params={
            "search": search,
            "search_operator": search_operator,
            "order": order,
            "limit": limit,
            "offset": offset,
        },
    )


def get_image(client, image_id) -> dict:
    return client.get(f"/images/{image_id}/")


def create_image(
    client,
    *,
    file: Path,
    title: str,
    fields: dict | None = None,
) -> dict:
    """Upload a new image (multipart/form-data)."""
    body = {"title": title, **(fields or {})}
    return client.upload("/images/", body, "file", file)


def update_image(client, image_id, body: dict) -> dict:
    return client.patch(f"/images/{image_id}/", body=body)


def delete_image(client, image_id) -> dict:
    return client.delete(f"/images/{image_id}/")

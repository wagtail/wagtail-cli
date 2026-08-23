from __future__ import annotations


def list_redirects(client, *, order=None, limit=None, offset=None) -> dict:
    return client.get(
        "/redirects/",
        params={"order": order, "limit": limit, "offset": offset},
    )


def find_redirect(client, *, id=None, html_path=None) -> dict:
    return client.get(
        "/redirects/find/",
        params={"id": id, "html_path": html_path},
    )


def get_redirect(client, redirect_id) -> dict:
    return client.get(f"/redirects/{redirect_id}/")


def create_redirect(client, body: dict) -> dict:
    return client.post("/redirects/", body=body)


def update_redirect(client, redirect_id, body: dict) -> dict:
    return client.put(f"/redirects/{redirect_id}/", body=body)


def delete_redirect(client, redirect_id) -> dict:
    return client.delete(f"/redirects/{redirect_id}/")

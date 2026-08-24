from __future__ import annotations


def list_sites(client, *, limit=None, offset=None) -> dict:
    return client.get("/sites/", params={"limit": limit, "offset": offset})


def get_site(client, site_id) -> dict:
    return client.get(f"/sites/{site_id}/")


def create_site(client, body: dict) -> dict:
    return client.post("/sites/", body=body)


def update_site(client, site_id, body: dict) -> dict:
    return client.put(f"/sites/{site_id}/", body=body)


def delete_site(client, site_id) -> dict:
    return client.delete(f"/sites/{site_id}/")

from __future__ import annotations


def list_locales(client, *, limit=None, offset=None) -> dict:
    return client.get("/locales/", params={"limit": limit, "offset": offset})


def get_locale(client, locale_id) -> dict:
    return client.get(f"/locales/{locale_id}/")


def create_locale(client, body: dict) -> dict:
    return client.post("/locales/", body=body)


def update_locale(client, locale_id, body: dict) -> dict:
    return client.put(f"/locales/{locale_id}/", body=body)


def delete_locale(client, locale_id) -> dict:
    return client.delete(f"/locales/{locale_id}/")

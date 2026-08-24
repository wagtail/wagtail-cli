from __future__ import annotations

from typing import Any


def list_types(client) -> Any:
    return client.get("/schema/")


def get_type_schema(client, type_name: str) -> Any:
    return client.get(f"/schema/{type_name}/")

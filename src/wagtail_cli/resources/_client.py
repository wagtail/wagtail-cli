from __future__ import annotations

import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from wagtail_cli.errors import NetworkError, error_for_status


@dataclass
class DryRunRequest:
    method: str
    url: str
    params: dict | None
    body: Any = None
    file: str | None = None


class WgtlClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.dry_run = dry_run
        self.verbose = verbose
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    def _log(self, *args: str) -> None:
        if self.verbose:
            print(*args, file=sys.stderr)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        body: Any = None,
        files: dict | None = None,
        data: dict | None = None,
        file_label: str | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        self._log(f"> {method} {url}")
        if self.dry_run:
            return DryRunRequest(
                method=method,
                url=url,
                params=params,
                body=body if body is not None else data,
                file=file_label,
            )
        try:
            resp = self._http.request(
                method, path, params=params, json=body, files=files, data=data
            )
        except httpx.HTTPError as e:
            raise NetworkError(str(e)) from e
        self._log(f"< {resp.status_code}")
        if resp.status_code == 204:
            return {}
        if resp.status_code in (301, 302, 303, 307, 308):
            return {"location": resp.headers.get("location", "")}
        try:
            payload = resp.json()
        except ValueError:
            payload = resp.text
        if resp.status_code >= 400:
            raise error_for_status(resp.status_code, payload)
        return payload if payload != "" else {}

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request(
            "GET",
            path,
            params={k: v for k, v in (params or {}).items() if v is not None},
        )

    def post(self, path: str, body: dict | None = None) -> Any:
        return self._request("POST", path, body=body)

    def patch(self, path: str, body: dict) -> Any:
        return self._request("PATCH", path, body=body)

    def put(self, path: str, body: dict) -> Any:
        return self._request("PUT", path, body=body)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def upload(self, path: str, fields: dict, file_field: str, file_path: Path) -> Any:
        if self.dry_run:
            return self._request(
                "POST",
                path,
                data=fields,
                file_label=f"{file_field}={file_path.name}",
            )
        with open(file_path, "rb") as fh:
            files = {file_field: (file_path.name, fh)}
            return self._request("POST", path, data=fields, files=files)

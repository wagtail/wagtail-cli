from __future__ import annotations

from typing import Any


class WgtlError(Exception):
    """Base CLI error. `problem` is the verbatim RFC 7807 body (or raw text)."""

    exit_code: int = 1

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        problem: dict | list | str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.problem = problem


class UsageError(WgtlError):
    exit_code = 2


class NetworkError(WgtlError):
    exit_code = 3


class AuthError(WgtlError):
    exit_code = 4


class ForbiddenError(WgtlError):
    exit_code = 5


class NotFoundError(WgtlError):
    exit_code = 6


class ValidationError(WgtlError):
    exit_code = 7


def _message(status: int, problem: Any) -> str:
    if isinstance(problem, dict):
        title = problem.get("title") or ""
        detail = problem.get("detail") or ""
        return f"{title}: {detail}".strip(": ") or f"HTTP {status}"
    return f"HTTP {status}"


def error_for_status(status: int, problem: Any) -> WgtlError:
    cls = {
        400: ValidationError,
        401: AuthError,
        403: ForbiddenError,
        404: NotFoundError,
        422: ValidationError,
    }.get(status, WgtlError)
    return cls(_message(status, problem), status_code=status, problem=problem)

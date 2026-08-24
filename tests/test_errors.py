import pytest

from wagtail_cli.errors import (
    AuthError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    UsageError,
    ValidationError,
    WgtlError,
    error_for_status,
)


@pytest.mark.parametrize(
    "exc,code",
    [
        (WgtlError("x"), 1),
        (UsageError("x"), 2),
        (NetworkError("x"), 3),
        (AuthError("x"), 4),
        (ForbiddenError("x"), 5),
        (NotFoundError("x"), 6),
        (ValidationError("x"), 7),
    ],
)
def test_exit_codes(exc, code):
    assert exc.exit_code == code


def test_error_carries_problem_verbatim():
    problem = {
        "type": "about:blank",
        "title": "Unprocessable Entity",
        "status": 422,
        "detail": "Validation failed",
        "errors": [],
    }
    e = error_for_status(422, problem)
    assert isinstance(e, ValidationError)
    assert e.status_code == 422
    assert e.problem == problem


@pytest.mark.parametrize(
    "status,cls",
    [
        (401, AuthError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (422, ValidationError),
        (400, ValidationError),
        (500, WgtlError),
    ],
)
def test_error_for_status_mapping(status, cls):
    assert isinstance(error_for_status(status, {"status": status}), cls)


def test_problem_title_becomes_message():
    e = error_for_status(404, {"title": "Not Found", "detail": "No page"})
    assert "Not Found" in str(e)


def test_non_dict_problem_passthrough():
    e = error_for_status(502, "<html>bad gateway</html>")
    assert e.problem == "<html>bad gateway</html>"
    assert isinstance(e, WgtlError) and e.exit_code == 1

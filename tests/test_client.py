import httpx
import pytest
import respx

from wgtl_api_cli.errors import AuthError, NetworkError, NotFoundError, ValidationError
from wgtl_api_cli.resources._client import DryRunRequest, WgtlClient


BASE = "https://x.test/api/v3"
ROUTER = respx.Router(assert_all_called=False)


def client(**kw) -> WgtlClient:
    return WgtlClient(BASE, "tok", **kw)


@respx.mock
def test_bearer_and_accept_headers():
    respx.get(f"{BASE}/whoami/").respond(200, json={})
    c = client()
    c.get("/whoami/")
    assert respx.calls[0].request.headers["authorization"] == "Bearer tok"
    assert respx.calls[0].request.headers["accept"] == "application/json"


@respx.mock
def test_get_params():
    route = respx.get(f"{BASE}/pages/").respond(200, json={"count": 0, "items": []})
    client().get("/pages/", params={"limit": 5})
    assert "limit=5" in str(route.calls[0].request.url)


@respx.mock
def test_422_maps_to_validation_error_with_problem():
    problem = {
        "type": "about:blank",
        "title": "Unprocessable Entity",
        "status": 422,
        "detail": "Validation failed",
        "errors": [{"loc": ["title"]}],
    }
    respx.post(f"{BASE}/pages/").respond(422, json=problem)
    with pytest.raises(ValidationError) as e:
        client().post("/pages/", {"meta": {}})
    assert e.value.problem == problem


@respx.mock
def test_401_404_mapping():
    respx.get(f"{BASE}/whoami/").respond(
        401, json={"title": "Unauthorized", "status": 401}
    )
    with pytest.raises(AuthError) as e:
        client().get("/whoami/")
    assert e.value.exit_code == 4
    respx.get(f"{BASE}/pages/99/").respond(
        404, json={"title": "Not Found", "status": 404}
    )
    with pytest.raises(NotFoundError):
        client().get("/pages/99/")


@respx.mock
def test_network_error():
    respx.get(f"{BASE}/whoami/").mock(side_effect=httpx.ConnectError("nope"))
    with pytest.raises(NetworkError) as e:
        client().get("/whoami/")
    assert e.value.exit_code == 3


@respx.mock
def test_dry_run_makes_no_http_call():
    out = client(dry_run=True).post("/pages/", {"title": "T"})
    assert isinstance(out, DryRunRequest)
    assert (out.method, out.url) == ("POST", f"{BASE}/pages/")
    assert out.body == {"title": "T"}
    assert len(respx.calls) == 0


@respx.mock
def test_find_302_returns_location_not_followed():
    respx.get(f"{BASE}/pages/find/").respond(
        302, headers={"location": "/api/v3/pages/61/?"}
    )
    out = client().get("/pages/find/", params={"html_path": "/blog/"})
    assert out == {"location": "/api/v3/pages/61/?"}


@respx.mock
def test_delete_empty_success():
    respx.delete(f"{BASE}/pages/1/").respond(204)
    assert client().delete("/pages/1/") == {}


@respx.mock
def test_upload_multipart(tmp_path):
    f = tmp_path / "a.png"
    f.write_bytes(b"\x89PNG")
    respx.post(f"{BASE}/images/").respond(200, json={"id": 7})
    out = client().upload("/images/", {"title": "A"}, "file", f)
    assert out == {"id": 7}
    sent = respx.calls[0].request
    assert sent.headers["content-type"].startswith("multipart/form-data")
    assert b"a.png" in sent.content and b"\x89PNG" in sent.content

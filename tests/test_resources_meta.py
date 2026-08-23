import json

import respx

from wgtl_api_cli.resources._client import WgtlClient
from wgtl_api_cli.resources.locales import (
    create_locale,
    delete_locale,
    get_locale,
    list_locales,
    update_locale,
)
from wgtl_api_cli.resources.redirects import (
    create_redirect,
    delete_redirect,
    find_redirect,
    get_redirect,
    list_redirects,
    update_redirect,
)
from wgtl_api_cli.resources.sites import (
    create_site,
    delete_site,
    get_site,
    list_sites,
    update_site,
)


BASE = "https://x.test/api/v3"


def client(**kw) -> WgtlClient:
    return WgtlClient(BASE, "tok", **kw)


# --- sites ---


@respx.mock
def test_list_sites():
    route = respx.get(f"{BASE}/sites/").respond(200, json={"count": 1, "items": []})
    list_sites(client(), limit=5)
    assert "limit=5" in str(route.calls[0].request.url)


@respx.mock
def test_get_site():
    respx.get(f"{BASE}/sites/2/").respond(200, json={"id": 2})
    assert get_site(client(), 2) == {"id": 2}


@respx.mock
def test_create_site():
    respx.post(f"{BASE}/sites/").respond(201, json={"id": 5})
    body = {"hostname": "example.com", "root_page_id": 4}
    out = create_site(client(), body)
    assert out == {"id": 5}
    assert json.loads(respx.calls[0].request.content) == body


@respx.mock
def test_update_site_put():
    respx.put(f"{BASE}/sites/5/").respond(200, json={"id": 5})
    update_site(client(), 5, {"hostname": "new.example.com", "root_page_id": 4})
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_delete_site():
    respx.delete(f"{BASE}/sites/5/").respond(204)
    assert delete_site(client(), 5) == {}


# --- locales ---


@respx.mock
def test_list_locales():
    route = respx.get(f"{BASE}/locales/").respond(200, json={"count": 0, "items": []})
    list_locales(client(), offset=1)
    assert "offset=1" in str(route.calls[0].request.url)


@respx.mock
def test_get_locale():
    respx.get(f"{BASE}/locales/2/").respond(200, json={"id": 2})
    assert get_locale(client(), 2) == {"id": 2}


@respx.mock
def test_create_locale():
    respx.post(f"{BASE}/locales/").respond(201, json={"id": 4})
    create_locale(client(), {"language_code": "fr"})
    assert json.loads(respx.calls[0].request.content) == {"language_code": "fr"}


@respx.mock
def test_update_locale_put():
    respx.put(f"{BASE}/locales/4/").respond(200, json={"id": 4})
    update_locale(client(), 4, {"language_code": "de"})
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_delete_locale():
    respx.delete(f"{BASE}/locales/4/").respond(204)
    assert delete_locale(client(), 4) == {}


# --- redirects ---


@respx.mock
def test_list_redirects():
    route = respx.get(f"{BASE}/redirects/").respond(200, json={"count": 0, "items": []})
    list_redirects(client(), order="-created_at")
    assert "order=-created_at" in str(route.calls[0].request.url)


@respx.mock
def test_find_redirect_location():
    route = respx.get(f"{BASE}/redirects/find/").respond(
        302, headers={"location": "/api/v3/redirects/9/?"}
    )
    out = find_redirect(client(), html_path="/old/")
    assert out == {"location": "/api/v3/redirects/9/?"}
    assert "html_path=%2Fold%2F" in str(route.calls[0].request.url)


@respx.mock
def test_get_redirect():
    respx.get(f"{BASE}/redirects/9/").respond(200, json={"id": 9})
    assert get_redirect(client(), 9) == {"id": 9}


@respx.mock
def test_create_redirect():
    respx.post(f"{BASE}/redirects/").respond(201, json={"id": 9})
    create_redirect(client(), {"old_path": "/old/", "redirect_link": "/new/"})
    assert json.loads(respx.calls[0].request.content) == {
        "old_path": "/old/",
        "redirect_link": "/new/",
    }


@respx.mock
def test_update_redirect_put():
    respx.put(f"{BASE}/redirects/9/").respond(200, json={"id": 9})
    update_redirect(client(), 9, {"old_path": "/old/", "redirect_link": "/new2/"})
    assert respx.calls[0].request.method == "PUT"


@respx.mock
def test_delete_redirect():
    respx.delete(f"{BASE}/redirects/9/").respond(204)
    assert delete_redirect(client(), 9) == {}

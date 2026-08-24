import json

import respx

from wagtail_cli.resources._client import WgtlClient
from wagtail_cli.resources.snippets import (
    copy_snippet_for_translation,
    create_snippet,
    delete_snippet,
    get_snippet,
    get_snippet_revision,
    list_snippet_revisions,
    list_snippets,
    publish_snippet,
    revert_snippet,
    unpublish_snippet,
    update_snippet,
)


BASE = "https://x.test/api/v3"
TYPE = "base.FooterText"


def client(**kw) -> WgtlClient:
    return WgtlClient(BASE, "tok", **kw)


@respx.mock
def test_list_snippets():
    route = respx.get(f"{BASE}/snippets/{TYPE}/").respond(
        200, json={"count": 1, "items": []}
    )
    out = list_snippets(client(), TYPE, search="hello", limit=5)
    assert out == {"count": 1, "items": []}
    url = str(route.calls[0].request.url)
    assert "search=hello" in url
    assert "limit=5" in url


@respx.mock
def test_list_snippets_type_in_path():
    route = respx.get(f"{BASE}/snippets/breads.BreadType/").respond(
        200, json={"count": 0, "items": []}
    )
    list_snippets(client(), "breads.BreadType")
    assert route.calls[0].request.url.path == "/api/v3/snippets/breads.BreadType/"


@respx.mock
def test_get_snippet():
    respx.get(f"{BASE}/snippets/{TYPE}/22/").respond(200, json={"id": 22})
    assert get_snippet(client(), TYPE, "22") == {"id": 22}


@respx.mock
def test_create_snippet():
    respx.post(f"{BASE}/snippets/{TYPE}/").respond(201, json={"id": 30})
    body = {"text": "Hello"}
    out = create_snippet(client(), TYPE, body)
    assert out == {"id": 30}
    assert json.loads(respx.calls[0].request.content) == body


@respx.mock
def test_update_snippet_patch():
    respx.patch(f"{BASE}/snippets/{TYPE}/22/").respond(200, json={"id": 22})
    update_snippet(client(), TYPE, "22", {"text": "Updated"})
    assert respx.calls[0].request.method == "PATCH"
    assert json.loads(respx.calls[0].request.content) == {"text": "Updated"}


@respx.mock
def test_delete_snippet():
    respx.delete(f"{BASE}/snippets/{TYPE}/22/").respond(204)
    assert delete_snippet(client(), TYPE, "22") == {}
    assert respx.calls[0].request.method == "DELETE"


@respx.mock
def test_publish_snippet():
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/publish/").respond(
        200, json={"id": 22}
    )
    assert publish_snippet(client(), TYPE, "22") == {"id": 22}
    assert (
        respx.calls[0].request.url.path
        == f"/api/v3/snippets/{TYPE}/22/actions/publish/"
    )


@respx.mock
def test_unpublish_snippet():
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/unpublish/").respond(
        200, json={"id": 22}
    )
    assert unpublish_snippet(client(), TYPE, "22") == {"id": 22}


@respx.mock
def test_revert_snippet_body():
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/revert/").respond(
        200, json={"id": 22}
    )
    revert_snippet(client(), TYPE, "22", revision_id=7)
    assert json.loads(respx.calls[0].request.content) == {"revision_id": 7}


@respx.mock
def test_copy_snippet_for_translation_body():
    respx.post(f"{BASE}/snippets/{TYPE}/22/actions/copy_for_translation/").respond(
        200, json={"id": 22}
    )
    copy_snippet_for_translation(client(), TYPE, "22", locale="fr")
    assert json.loads(respx.calls[0].request.content) == {"locale": "fr"}


@respx.mock
def test_list_snippet_revisions():
    route = respx.get(f"{BASE}/snippets/{TYPE}/22/revisions/").respond(
        200, json={"items": []}
    )
    list_snippet_revisions(client(), TYPE, "22", limit=10)
    assert "limit=10" in str(route.calls[0].request.url)


@respx.mock
def test_get_snippet_revision():
    respx.get(f"{BASE}/snippets/{TYPE}/22/revisions/5/").respond(200, json={"id": 5})
    assert get_snippet_revision(client(), TYPE, "22", 5) == {"id": 5}

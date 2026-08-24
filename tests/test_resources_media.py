import json

import respx

from wagtail_cli.resources._client import WgtlClient
from wagtail_cli.resources.documents import (
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
)
from wagtail_cli.resources.images import (
    create_image,
    delete_image,
    get_image,
    list_images,
    update_image,
)


BASE = "https://x.test/api/v3"


def client(**kw) -> WgtlClient:
    return WgtlClient(BASE, "tok", **kw)


# --- images ---


@respx.mock
def test_list_images():
    route = respx.get(f"{BASE}/images/").respond(200, json={"count": 1, "items": []})
    out = list_images(client(), search="sunset", limit=5)
    assert out == {"count": 1, "items": []}
    url = str(route.calls[0].request.url)
    assert "search=sunset" in url
    assert "limit=5" in url


@respx.mock
def test_list_images_none_params_dropped():
    route = respx.get(f"{BASE}/images/").respond(200, json={"count": 0, "items": []})
    list_images(client(), order="title")
    url = str(route.calls[0].request.url)
    assert "order=title" in url
    assert "search=" not in url


@respx.mock
def test_get_image():
    respx.get(f"{BASE}/images/7/").respond(200, json={"id": 7})
    out = get_image(client(), 7)
    assert out == {"id": 7}
    assert respx.calls[0].request.url.path == "/api/v3/images/7/"


@respx.mock
def test_create_image_multipart(tmp_path):
    f = tmp_path / "sunset.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n")
    respx.post(f"{BASE}/images/").respond(201, json={"id": 10, "title": "Sunset"})
    out = create_image(client(), file=f, title="Sunset", fields={"description": "A"})
    assert out == {"id": 10, "title": "Sunset"}
    sent = respx.calls[0].request
    assert sent.method == "POST"
    assert sent.headers["content-type"].startswith("multipart/form-data")
    assert b"sunset.png" in sent.content
    assert b"\x89PNG" in sent.content


@respx.mock
def test_update_image_patch():
    respx.patch(f"{BASE}/images/7/").respond(200, json={"id": 7, "title": "New"})
    out = update_image(client(), 7, {"title": "New"})
    assert out == {"id": 7, "title": "New"}
    assert respx.calls[0].request.method == "PATCH"
    assert json.loads(respx.calls[0].request.content) == {"title": "New"}


@respx.mock
def test_delete_image():
    respx.delete(f"{BASE}/images/7/").respond(204)
    assert delete_image(client(), 7) == {}
    assert respx.calls[0].request.method == "DELETE"


@respx.mock
def test_create_image_dry_run(tmp_path):
    f = tmp_path / "a.png"
    f.write_bytes(b"\x89PNG")
    out = create_image(client(dry_run=True), file=f, title="X")
    assert respx.calls == []
    assert out.method == "POST"
    assert out.file == "file=a.png"
    assert out.body == {"title": "X"}


# --- documents ---


@respx.mock
def test_list_documents():
    route = respx.get(f"{BASE}/documents/").respond(200, json={"count": 0, "items": []})
    list_documents(client(), order="-created_at", offset=2)
    url = str(route.calls[0].request.url)
    assert "order=-created_at" in url
    assert "offset=2" in url


@respx.mock
def test_get_document():
    respx.get(f"{BASE}/documents/3/").respond(200, json={"id": 3})
    assert get_document(client(), 3) == {"id": 3}


@respx.mock
def test_create_document_multipart(tmp_path):
    f = tmp_path / "brief.pdf"
    f.write_bytes(b"%PDF-1.4")
    respx.post(f"{BASE}/documents/").respond(201, json={"id": 12})
    out = create_document(client(), file=f, title="Brief")
    assert out == {"id": 12}
    sent = respx.calls[0].request
    assert sent.headers["content-type"].startswith("multipart/form-data")
    assert b"brief.pdf" in sent.content
    assert b"%PDF-1.4" in sent.content


@respx.mock
def test_update_document_patch():
    respx.patch(f"{BASE}/documents/3/").respond(200, json={"id": 3})
    update_document(client(), 3, {"title": "New"})
    assert respx.calls[0].request.method == "PATCH"


@respx.mock
def test_delete_document():
    respx.delete(f"{BASE}/documents/3/").respond(204)
    assert delete_document(client(), 3) == {}

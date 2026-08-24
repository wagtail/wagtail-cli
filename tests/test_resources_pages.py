import respx

from wagtail_cli.resources._client import WgtlClient
from wagtail_cli.resources.pages import (
    build_page_payload,
    convert_alias,
    copy_for_translation,
    copy_page,
    create_alias,
    create_page,
    delete_page,
    find_page,
    get_page,
    get_revision,
    list_pages,
    list_revisions,
    move_page,
    publish_page,
    revert_page,
    unpublish_page,
    update_page,
)


BASE = "https://x.test/api/v3"
ROUTER = respx.Router(assert_all_called=False)


def client(**kw) -> WgtlClient:
    return WgtlClient(BASE, "tok", **kw)


# --- build_page_payload (pure) ---


def test_create_payload():
    p = build_page_payload(
        type_name="blog.BlogPage",
        parent_id=3,
        title="T",
        fields={"subtitle": "S"},
    )
    assert p == {
        "meta": {"type": "blog.BlogPage", "parent_id": 3},
        "title": "T",
        "subtitle": "S",
    }


def test_create_payload_publish():
    p = build_page_payload(
        type_name="blog.BlogPage", parent_id=3, title="T", publish=True
    )
    assert p["meta"]["action"] == "publish"


def test_create_payload_slug():
    p = build_page_payload(
        type_name="blog.BlogPage", parent_id=3, title="T", slug="my-post"
    )
    assert p["slug"] == "my-post"


def test_update_payload_fields_only():
    assert build_page_payload(title="T", fields={"a": 1}, for_create=False) == {
        "title": "T",
        "a": 1,
    }


def test_update_payload_title_slug_and_fields():
    assert build_page_payload(
        title="T", slug="s", fields={"a": 1}, for_create=False
    ) == {"title": "T", "slug": "s", "a": 1}


def test_update_payload_no_fields_empty():
    assert build_page_payload(for_create=False) == {}


# --- list_pages ---


@respx.mock
def test_list_pages_basic():
    route = respx.get(f"{BASE}/pages/").respond(200, json={"count": 1, "items": []})
    out = list_pages(client(), type="blog.BlogPage", limit=5)
    assert out == {"count": 1, "items": []}
    url = str(route.calls[0].request.url)
    assert "type=blog.BlogPage" in url
    assert "limit=5" in url


@respx.mock
def test_list_pages_none_params_dropped():
    route = respx.get(f"{BASE}/pages/").respond(200, json={"count": 0, "items": []})
    list_pages(client(), order="title")
    url = str(route.calls[0].request.url)
    assert "order=title" in url
    assert "type=" not in url


@respx.mock
def test_list_pages_type_is_repeated_param():
    route = respx.get(f"{BASE}/pages/").respond(200, json={"count": 0, "items": []})
    list_pages(client(), type=["blog.BlogPage", "blog.BlogPost"])
    url = str(route.calls[0].request.url)
    assert url.count("type=") == 2


# --- find_page ---


@respx.mock
def test_find_page_path():
    route = respx.get(f"{BASE}/pages/find/").respond(
        302, headers={"location": "/api/v3/pages/61/?"}
    )
    out = find_page(client(), html_path="/blog/")
    assert out == {"location": "/api/v3/pages/61/?"}
    assert "html_path=%2Fblog%2F" in str(route.calls[0].request.url)


# --- get_page ---


@respx.mock
def test_get_page():
    route = respx.get(f"{BASE}/pages/61/").respond(200, json={"id": 61})
    out = get_page(client(), 61)
    assert out == {"id": 61}
    assert not route.calls[0].request.url.params.get("version")


@respx.mock
def test_get_page_version():
    route = respx.get(f"{BASE}/pages/61/").respond(200, json={"id": 61})
    get_page(client(), 61, version="draft")
    assert route.calls[0].request.url.params["version"] == "draft"


# --- create / update / delete ---


@respx.mock
def test_create_page():
    respx.post(f"{BASE}/pages/").respond(201, json={"id": 100})
    payload = {"meta": {"type": "blog.BlogPage", "parent_id": 3}, "title": "T"}
    out = create_page(client(), payload)
    assert out == {"id": 100}
    sent = respx.calls[0].request
    assert sent.method == "POST"
    assert sent.url.path == "/api/v3/pages/"
    import json

    assert json.loads(sent.content) == payload


@respx.mock
def test_update_page():
    respx.patch(f"{BASE}/pages/61/").respond(200, json={"id": 61})
    out = update_page(client(), 61, {"title": "New"})
    assert out == {"id": 61}
    assert respx.calls[0].request.method == "PATCH"


@respx.mock
def test_delete_page():
    respx.delete(f"{BASE}/pages/61/").respond(204)
    assert delete_page(client(), 61) == {}
    assert respx.calls[0].request.method == "DELETE"


# --- actions ---


@respx.mock
def test_publish_page():
    respx.post(f"{BASE}/pages/61/actions/publish/").respond(200, json={"id": 61})
    out = publish_page(client(), 61)
    assert out == {"id": 61}
    assert respx.calls[0].request.url.path == "/api/v3/pages/61/actions/publish/"


@respx.mock
def test_unpublish_page():
    respx.post(f"{BASE}/pages/61/actions/unpublish/").respond(200, json={"id": 61})
    unpublish_page(client(), 61)
    assert respx.calls[0].request.url.path == "/api/v3/pages/61/actions/unpublish/"


@respx.mock
def test_copy_page():
    respx.post(f"{BASE}/pages/61/actions/copy/").respond(201, json={"id": 62})
    out = copy_page(
        client(), 61, destination_id=9, slug="copy", recursive=True, keep_live=False
    )
    assert out == {"id": 62}
    import json

    sent = json.loads(respx.calls[0].request.content)
    assert sent == {
        "destination_id": 9,
        "slug": "copy",
        "recursive": True,
        "keep_live": False,
    }
    assert respx.calls[0].request.url.path == "/api/v3/pages/61/actions/copy/"


@respx.mock
def test_move_page():
    respx.post(f"{BASE}/pages/61/actions/move/").respond(200, json={"id": 61})
    move_page(client(), 61, destination_id=9)
    import json

    sent = json.loads(respx.calls[0].request.content)
    assert sent == {"destination_id": 9}


@respx.mock
def test_revert_page():
    respx.post(f"{BASE}/pages/61/actions/revert/").respond(200, json={"id": 61})
    revert_page(client(), 61, revision_id=42)
    import json

    sent = json.loads(respx.calls[0].request.content)
    assert sent == {"revision_id": 42}


@respx.mock
def test_create_alias():
    respx.post(f"{BASE}/pages/61/actions/create_alias/").respond(201, json={"id": 70})
    create_alias(client(), 61, destination_id=2)
    import json

    sent = json.loads(respx.calls[0].request.content)
    assert sent == {"destination_id": 2}


@respx.mock
def test_convert_alias():
    respx.post(f"{BASE}/pages/61/actions/convert_alias/").respond(200, json={"id": 61})
    convert_alias(client(), 61)
    assert respx.calls[0].request.url.path == "/api/v3/pages/61/actions/convert_alias/"


@respx.mock
def test_copy_for_translation():
    respx.post(f"{BASE}/pages/61/actions/copy_for_translation/").respond(
        201, json={"id": 80}
    )
    copy_for_translation(client(), 61, locale="fr")
    import json

    sent = json.loads(respx.calls[0].request.content)
    assert sent == {"locale": "fr"}


# --- revisions ---


@respx.mock
def test_list_revisions():
    route = respx.get(f"{BASE}/pages/61/revisions/").respond(
        200, json={"count": 0, "items": []}
    )
    list_revisions(client(), 61, limit=10)
    assert str(route.calls[0].request.url).endswith("/revisions/?limit=10")


@respx.mock
def test_get_revision():
    respx.get(f"{BASE}/pages/61/revisions/42/").respond(200, json={"id": 42})
    out = get_revision(client(), 61, 42)
    assert out == {"id": 42}
    assert respx.calls[0].request.url.path == "/api/v3/pages/61/revisions/42/"

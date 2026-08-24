import respx

from wagtail_cli.resources._client import WgtlClient
from wagtail_cli.resources.schema import get_type_schema, list_types


BASE = "https://x.test/api/v3"


def client(**kw) -> WgtlClient:
    return WgtlClient(BASE, "tok", **kw)


@respx.mock
def test_list_types():
    respx.get(f"{BASE}/schema/").respond(200, json={"types": [{"name": "a.A"}]})
    assert list_types(client()) == {"types": [{"name": "a.A"}]}


@respx.mock
def test_get_type_schema():
    respx.get(f"{BASE}/schema/blog.BlogPage/").respond(200, json={"read": {}})
    assert get_type_schema(client(), "blog.BlogPage") == {"read": {}}
    assert respx.calls[0].request.url.path == "/api/v3/schema/blog.BlogPage/"

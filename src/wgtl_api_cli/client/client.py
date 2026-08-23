from __future__ import annotations

import typing

from clientele import api as clientele_api

from . import config, schemas


client = clientele_api.APIClient(config=config.Config())


@client.get("/api/v3/pages/")
def pages_list(
    result: schemas.PagedBasePageSchema,
    type_: typing.Annotated[
        list[str] | None, clientele_api.Query(alias="type")
    ] = None,
    ancestor_of: int | None = None,
    child_of: int | typing.Literal["root"] | None = None,
    descendant_of: int | typing.Literal["root"] | None = None,
    translation_of: int | typing.Literal["root"] | None = None,
    locale: str | None = None,
    site: str | None = None,
    order: typing.Literal["random"] | list[str] | None = None,
    search: str | None = None,
    search_operator: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedBasePageSchema:
    """List pages"""
    return result


@client.post("/api/v3/pages/")
def pages_create(
    result: schemas.Response,
    data: schemas.Data,
    rich_text_format: str | None = None,
) -> schemas.Response:
    """Create page"""
    return result


@client.get("/api/v3/pages/find/")
def pages_find(
    result: schemas.Response,
    id: int | None = None,
    html_path: str | None = None,
    site: str | None = None,
    version: str | None = None,
) -> schemas.Response:
    """Find page"""
    return result


@client.get("/api/v3/pages/{page_id}/")
def pages_detail(
    result: schemas.Response,
    page_id: int,
    version: str | None = None,
    rich_text_format: str | None = None,
) -> schemas.Response:
    """Page detail"""
    return result


@client.patch("/api/v3/pages/{page_id}/")
def pages_update(
    result: schemas.Response,
    data: schemas.Data,
    page_id: int,
    rich_text_format: str | None = None,
) -> schemas.Response:
    """Update page"""
    return result


@client.delete("/api/v3/pages/{page_id}/")
def pages_delete(result: None, page_id: int) -> None:
    """Delete page"""
    return result


@client.get("/api/v3/pages/{page_id}/revisions/")
def pages_revisions_list(
    result: schemas.PagedRevisionSchema,
    page_id: int,
    created_at_from: str | None = None,
    created_at_to: str | None = None,
    user_id: int | str | None = None,
    approved_go_live_at_from: str | None = None,
    approved_go_live_at_to: str | None = None,
    object_str: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedRevisionSchema:
    """List page revisions"""
    return result


@client.get("/api/v3/pages/{page_id}/revisions/{revision_id}/")
def pages_revisions_detail(
    result: schemas.PageRevisionDetailSchema, page_id: int, revision_id: int
) -> schemas.PageRevisionDetailSchema:
    """Page revision detail"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/publish/")
def pages_actions_publish(result: schemas.Response, page_id: int) -> schemas.Response:
    """Publish page"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/unpublish/")
def pages_actions_unpublish(
    result: schemas.Response,
    data: schemas.PagesActionsUnpublishApplicationJson,
    page_id: int,
) -> schemas.Response:
    """Unpublish page"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/copy/")
def pages_actions_copy(
    result: schemas.Response,
    data: schemas.PagesActionsCopyApplicationJson,
    page_id: int,
) -> schemas.Response:
    """Copy page"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/move/")
def pages_actions_move(
    result: schemas.Response, data: schemas.PageMoveSchema, page_id: int
) -> schemas.Response:
    """Move page"""
    return result


@client.delete("/api/v3/pages/{page_id}/actions/delete/")
def pages_actions_delete(result: None, page_id: int) -> None:
    """Delete page"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/revert/")
def pages_actions_revert(
    result: schemas.Response, data: schemas.PageRevertSchema, page_id: int
) -> schemas.Response:
    """Revert page to a previous revision"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/convert_alias/")
def pages_actions_convert_alias(
    result: schemas.Response, page_id: int
) -> schemas.Response:
    """Convert alias page to a regular page"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/create_alias/")
def pages_actions_create_alias(
    result: schemas.Response,
    data: schemas.PagesActionsCreateAliasApplicationJson,
    page_id: int,
) -> schemas.Response:
    """Create an alias of a page"""
    return result


@client.post("/api/v3/pages/{page_id}/actions/copy_for_translation/")
def pages_actions_copy_for_translation(
    result: schemas.Response, data: schemas.PageCopyForTranslationSchema, page_id: int
) -> schemas.Response:
    """Copy page for translation"""
    return result


@client.get("/api/v3/schema/")
def schema_list(result: schemas.ContentTypeListSchema) -> schemas.ContentTypeListSchema:
    """List registered content types"""
    return result


@client.get("/api/v3/schema/{type_name}/")
def schema_detail(
    result: schemas.SchemaDetailResponse, type_name: str
) -> schemas.SchemaDetailResponse:
    """Schemas for a content type"""
    return result


@client.get("/api/v3/sites/")
def sites_list(
    result: schemas.PagedSiteSchema,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedSiteSchema:
    """List sites"""
    return result


@client.post("/api/v3/sites/")
def sites_create(
    result: schemas.SiteSchema, data: schemas.SiteInputSchema
) -> schemas.SiteSchema:
    """Create site"""
    return result


@client.get("/api/v3/sites/{site_id}/")
def sites_detail(result: schemas.SiteSchema, site_id: int) -> schemas.SiteSchema:
    """Site detail"""
    return result


@client.put("/api/v3/sites/{site_id}/")
def sites_update(
    result: schemas.SiteSchema, data: schemas.SiteInputSchema, site_id: int
) -> schemas.SiteSchema:
    """Update site"""
    return result


@client.delete("/api/v3/sites/{site_id}/")
def sites_delete(result: None, site_id: int) -> None:
    """Delete site"""
    return result


@client.get("/api/v3/whoami/")
def whoami(result: schemas.WhoAmISchema) -> schemas.WhoAmISchema:
    """Current API user"""
    return result


@client.get("/api/v3/snippets/{type_}/")
def snippets_list(
    result: schemas.PagedAnnotated,
    type_: str,
    locale: str | None = None,
    translation_of: str | None = None,
    order: typing.Literal["random"] | list[str] | None = None,
    search: str | None = None,
    search_operator: str | None = None,
    rich_text_format: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedAnnotated:
    """List snippets"""
    return result


@client.post("/api/v3/snippets/{type_}/")
def snippets_create(
    result: schemas.Response,
    data: schemas.Data,
    type_: str,
    rich_text_format: str | None = None,
) -> schemas.Response:
    """Create snippet"""
    return result


@client.get("/api/v3/snippets/{type_}/{pk}/")
def snippets_detail(
    result: schemas.Response,
    type_: str,
    pk: str,
    version: str | None = None,
    rich_text_format: str | None = None,
) -> schemas.Response:
    """Snippet detail"""
    return result


@client.patch("/api/v3/snippets/{type_}/{pk}/")
def snippets_update(
    result: schemas.Response,
    data: schemas.Data,
    type_: str,
    pk: str,
    rich_text_format: str | None = None,
) -> schemas.Response:
    """Update snippet"""
    return result


@client.delete("/api/v3/snippets/{type_}/{pk}/")
def snippets_delete(result: None, type_: str, pk: str) -> None:
    """Delete snippet"""
    return result


@client.get("/api/v3/snippets/{type_}/{pk}/revisions/")
def snippets_revisions_list(
    result: schemas.PagedRevisionSchema,
    type_: str,
    pk: str,
    created_at_from: str | None = None,
    created_at_to: str | None = None,
    user_id: int | str | None = None,
    approved_go_live_at_from: str | None = None,
    approved_go_live_at_to: str | None = None,
    object_str: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedRevisionSchema:
    """List snippet revisions"""
    return result


@client.get("/api/v3/snippets/{type_}/{pk}/revisions/{revision_id}/")
def snippets_revisions_detail(
    result: schemas.SnippetRevisionDetailSchema, type_: str, pk: str, revision_id: int
) -> schemas.SnippetRevisionDetailSchema:
    """Snippet revision detail"""
    return result


@client.delete("/api/v3/snippets/{type_}/{pk}/actions/delete/")
def snippets_actions_delete(result: None, type_: str, pk: str) -> None:
    """Delete snippet"""
    return result


@client.post("/api/v3/snippets/{type_}/{pk}/actions/publish/")
def snippets_actions_publish(
    result: schemas.Response, type_: str, pk: str
) -> schemas.Response:
    """Publish snippet"""
    return result


@client.post("/api/v3/snippets/{type_}/{pk}/actions/unpublish/")
def snippets_actions_unpublish(
    result: schemas.Response, type_: str, pk: str
) -> schemas.Response:
    """Unpublish snippet"""
    return result


@client.post("/api/v3/snippets/{type_}/{pk}/actions/revert/")
def snippets_actions_revert(
    result: schemas.Response, data: schemas.SnippetRevertSchema, type_: str, pk: str
) -> schemas.Response:
    """Revert snippet to a previous revision"""
    return result


@client.post("/api/v3/snippets/{type_}/{pk}/actions/copy_for_translation/")
def snippets_actions_copy_for_translation(
    result: schemas.FooterTextSchema,
    data: schemas.SnippetCopyForTranslationSchema,
    type_: typing.Literal["base.FooterText"],
    pk: str,
) -> schemas.FooterTextSchema:
    """Copy snippet for translation"""
    return result


@client.get("/api/v3/documents/")
def documents_list(
    result: schemas.PagedDocumentSchema,
    order: typing.Literal["random"] | list[str] | None = None,
    search: str | None = None,
    search_operator: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedDocumentSchema:
    """List documents"""
    return result


@client.post("/api/v3/documents/")
def documents_create(
    result: schemas.DocumentSchema, data: schemas.MultiPartBodyParams
) -> schemas.DocumentSchema:
    """Create document"""
    return result


@client.get("/api/v3/documents/{document_id}/")
def documents_detail(
    result: schemas.DocumentSchema, document_id: int
) -> schemas.DocumentSchema:
    """Document detail"""
    return result


@client.patch("/api/v3/documents/{document_id}/")
def documents_update(
    result: schemas.DocumentSchema, data: schemas.DocumentPatchSchema, document_id: int
) -> schemas.DocumentSchema:
    """Update document"""
    return result


@client.delete("/api/v3/documents/{document_id}/")
def documents_delete(result: None, document_id: int) -> None:
    """Delete document"""
    return result


@client.get("/api/v3/images/")
def images_list(
    result: schemas.PagedImageSchema,
    order: typing.Literal["random"] | list[str] | None = None,
    search: str | None = None,
    search_operator: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedImageSchema:
    """List images"""
    return result


@client.post("/api/v3/images/")
def images_create(
    result: schemas.ImageSchema, data: schemas.MultiPartBodyParams
) -> schemas.ImageSchema:
    """Create image"""
    return result


@client.get("/api/v3/images/{image_id}/")
def images_detail(result: schemas.ImageSchema, image_id: int) -> schemas.ImageSchema:
    """Image detail"""
    return result


@client.patch("/api/v3/images/{image_id}/")
def images_update(
    result: schemas.ImageSchema, data: schemas.ImagePatchSchema, image_id: int
) -> schemas.ImageSchema:
    """Update image"""
    return result


@client.delete("/api/v3/images/{image_id}/")
def images_delete(result: None, image_id: int) -> None:
    """Delete image"""
    return result


@client.get("/api/v3/locales/")
def locales_list(
    result: schemas.PagedLocaleSchema,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedLocaleSchema:
    """List locales"""
    return result


@client.post("/api/v3/locales/")
def locales_create(
    result: schemas.LocaleSchema, data: schemas.LocaleInputSchema
) -> schemas.LocaleSchema:
    """Create locale"""
    return result


@client.get("/api/v3/locales/{locale_id}/")
def locales_detail(
    result: schemas.LocaleSchema, locale_id: int
) -> schemas.LocaleSchema:
    """Locale detail"""
    return result


@client.put("/api/v3/locales/{locale_id}/")
def locales_update(
    result: schemas.LocaleSchema, data: schemas.LocaleInputSchema, locale_id: int
) -> schemas.LocaleSchema:
    """Update locale"""
    return result


@client.delete("/api/v3/locales/{locale_id}/")
def locales_delete(result: None, locale_id: int) -> None:
    """Delete locale"""
    return result


@client.get("/api/v3/redirects/")
def redirects_list(
    result: schemas.PagedRedirectSchema,
    order: typing.Literal["random"] | list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> schemas.PagedRedirectSchema:
    """List redirects"""
    return result


@client.post("/api/v3/redirects/")
def redirects_create(
    result: schemas.RedirectSchema, data: schemas.RedirectInputSchema
) -> schemas.RedirectSchema:
    """Create redirect"""
    return result


@client.get("/api/v3/redirects/find/")
def redirects_find(
    result: schemas.RedirectSchema,
    id: int | None = None,
    html_path: str | None = None,
) -> schemas.RedirectSchema:
    """Find redirect"""
    return result


@client.get("/api/v3/redirects/{redirect_id}/")
def redirects_detail(
    result: schemas.RedirectSchema, redirect_id: int
) -> schemas.RedirectSchema:
    """Redirect detail"""
    return result


@client.put("/api/v3/redirects/{redirect_id}/")
def redirects_update(
    result: schemas.RedirectSchema, data: schemas.RedirectInputSchema, redirect_id: int
) -> schemas.RedirectSchema:
    """Update redirect"""
    return result


@client.delete("/api/v3/redirects/{redirect_id}/")
def redirects_delete(result: None, redirect_id: int) -> None:
    """Delete redirect"""
    return result

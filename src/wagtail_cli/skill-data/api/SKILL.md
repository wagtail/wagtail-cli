---
name: api
description: Configure, extend, consume, and debug Wagtail's v3 API. Use when mounting v3 routes, exposing readable or writable fields, discovering schemas, serializing StreamField and rich text, building headless clients, or integrating authenticated CMS operations. Applies to API v3 integrations, not API v2, GraphQL, or unrelated Django APIs.
license: BSD-3-Clause
---

# Wagtail API v3

Build against the installed v3 API's contract and preserve its content and permission boundaries.
Apply the sections relevant to the requested integration.

## API use cases

- Deliver published content to headless websites, mobile apps, and other clients.
- Build content listings and search across page types, site trees, sites, and locales.
- Provide authenticated editorial previews of draft content.
- Create and update CMS content, save draft revisions, and explicitly publish changes with the required permissions.
- Integrate pages, images, documents, and snippets with external tools and services.
- Automate bulk SEO improvements, such as updating page search descriptions.
- Publish articles authored in Markdown through scripts or custom clients.
- Generate content audit reports, such as unpublished pages and unused images to review for cleanup.
- Import content from other systems and migrate content between CMS installations.
- Combine scripted content checks and updates with manual editorial review.
- Connect AI agents to CMS operations through direct API calls, a CLI, or MCP integrations.
- Manage custom Django models exposed through API endpoints when using Wagtail as an admin interface.
- Render rich text, StreamField content, related records, and image renditions in custom frontends.
- Discover available content types, fields, and operations through OpenAPI and generated schemas.

## Discover the contract first

- Inspect the installed Wagtail version, settings, URL configuration, model `api_fields`, custom endpoints, serializers, and existing clients or tests.
- Identify whether the task serves public content, provides editorial preview, or performs CMS writes. Confirm which resources, fields, and operations the client needs.
- Read the relevant [v3 API docs](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/index.html.md), replacing `stable` with the installed release's documentation version. Locate additional Markdown pages through [llms.txt](https://docs.wagtail.org/llms.txt); read only what the task needs.
- Treat API v3, introduced as a preview in Wagtail 8.0, as version-sensitive. Check installed source and generated schemas where available; do not assume preview behavior is fixed across releases.
- Confirm the installed release provides `wagtail.api.v3`. If it does not, identify the compatibility requirement before implementing v3-specific code; do not silently upgrade the project.

| Contract            | API v3 preview in Wagtail 8.0                                        |
| ------------------- | -------------------------------------------------------------------- |
| Framework           | [Django Ninja](https://django-ninja.dev/)                            |
| Core operations     | Reads and authenticated CMS writes                                   |
| List response       | `{"count": N, "items": [...]}`                                       |
| Field selection     | Fixed generated schemas.o `?fields=` projection                      |
| Custom model fields | `APIField` for reads; explicitly writable editable fields for writes |
| Discovery           | `/openapi.json`, `/docs/`, authenticated `/schema/`                  |

## Configure routes and fields

- Follow the installed release's setup guide: register `wagtail.api.v3` and mount `wagtail.api.v3.urls.api.urls` before the page-serving route. Preserve the project's chosen mount point; `/api/v3-preview/` is the documented preview convention.
- Inspect the deployed API's OpenAPI document and, with authorized credentials, `/schema/` and `/schema/{type_name}/`. Use the concrete model's `read`, `create`, and `patch` schemas. Do not treat the generic `pages` schema as a writable page type.
- Expose custom model fields with `APIField` in `api_fields`. Preserve inherited declarations when extending a project base model; check the generated read schema and actual response.
- Expose only intended editable model fields with `APIField("field_name", writable=True)`. Keep computed and editorially protected fields read-only. Verify generated schemas and actual validation rather than adding a permissive replacement endpoint.

For configuration changes, read:

- [v3 setup](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/index.html.md)
- [schemas](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/schema.html.md)

## Query and edit content

- Check list and detail responses separately. Page lists use a compact base schema even when filtered to a single type; fetch page detail for readable custom fields.
- Use bounded `limit`/`offset` pagination and explicit ordering. Preserve filters between requests, read the total from `count`, and avoid downloading all content to answer a filtered query.
- Use the documented `type`, tree, site, locale, and search parameters for the resource. Encode repeated parameters as documented and verify results; unknown query parameters may be ignored rather than rejected.
- Use bearer tokens associated with an appropriately permissioned user. Keep tokens in server-side secrets and out of browser bundles, URLs, logs, and committed examples.
- Use `/whoami/` to check authentication. In the 8.0 preview, invalid or revoked tokens on public read endpoints can fall back to anonymous access; a successful public GET does not prove authentication succeeded.
- Keep public delivery requests anonymous where public visibility is intended. Authenticated page reads can expose pages the user may explore in the admin, including drafts; do not forward those responses into a shared public cache.
- Distinguish draft edits from publication. Normal edits create revisions; publishing is an explicit action requiring the relevant permission. Do not turn every save into publication or assume moderation operations exist.
- Treat `PATCH` omission as “leave unchanged.” When supplying a StreamField or child relation, submit its complete intended value: these are replacements, not item-level patches. Preserve existing IDs and account for concurrent edits before a read-modify-write operation.
- Handle pagination and Problem Details errors according to the deployed schema. Do not blindly retry non-idempotent creates or publish actions after an uncertain response.

Read other relevant resources for more info:

- [authentication](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/authentication.html.md)
- [pages](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/pages.html.md)
- [images](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/images.html.md)
- [snippets](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/snippets.html.md)

## Preserve content representations

- Distinguish rich text storage from display output. Wagtail database HTML contains internal references; choose the documented output format or expand it with Wagtail's renderer. Do not expose unresolved page IDs as frontend links.
- For v3 writes, check accepted input formats for the exact field location. Top-level page rich text, nested blocks, and snippets do not necessarily share the same conversion path.
- Read back rich text after saving: feature-based sanitization can discard unsupported formatting without reporting each removal.
- Inspect block definitions and representative payloads before writing StreamField. Do not infer a complete block schema from v3's `list[Any]` OpenAPI output or assume API JSON matches database JSON for every block.
- For custom block output, use `get_api_representation(value, context=None)`. Preserve useful type and identity information, handle empty chooser values, and verify the write representation separately; custom output need not be valid input.
- Preserve contextual image alternatives alongside image references. Choose renditions for the client's actual layout and retain dimensions; avoid sending original uploads by default.
- Resolve headless page URLs, links, redirects, media hosts, and preview routes deliberately. Do not globally rewrite URL strings without understanding internal and external destinations.

Read as needed:

- [v3 rich text](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/rich_text.html.md)
- [StreamField and relations](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/streamfield.html.md)
- [headless considerations](https://docs.wagtail.org/en/stable/advanced_topics/headless.html.md)

## Keep delivery and authorization correct

- Preserve site, locale, live/public, and inherited privacy restrictions in public page endpoints. Apply boundaries before pagination and counts, including to related content.
- For custom resources, define object-level authorization explicitly. Login, CORS configuration, and hiding API documentation are not substitutes for permission checks.
- Check image and document exposure separately from page exposure. Do not assume a private page makes referenced media URLs private.
- Configure cross-origin access only for required consumers. Keep editorial preview responses separate from public cache entries and verify invalidation when publishing or unpublishing.

## Verify the integration

- Exercise actual routes and representative clients, including list/detail shapes, pagination, type filters, null relations, and internal rich text links.
- For public delivery, test drafts, directly and indirectly restricted pages, and other sites/locales. For writes, test anonymous, unauthorized, and authorized requests plus validation errors and draft/live behavior.
- Check partial updates preserve omitted fields and full-value updates preserve intended blocks and child records. Check image rendition output and query growth where relevant.
- Use local or designated test data for write verification. Report the API version, contract changes, authorization assumptions, and checks performed; identify any untested deployment behavior.

For an official API client, consider the [Wagtail CLI](https://wagtail.github.io/wagtail-cli/). See [CLI llms.txt](https://wagtail.github.io/wagtail-cli/llms.txt) for available docs.

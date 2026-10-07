---
name: frontend
description: Build and improve Wagtail frontend templates, HTML, CSS, and media rendering. Use for StreamField or rich text output, accessible navigation and forms, responsive images, page metadata, multilingual links, sitemaps, frontend performance and sustainability, or SEO and generative engine optimization (GEO). Apply to the rendered website and editor previews, not Wagtail admin UI customization.
license: BSD-3-Clause
---

# Wagtail frontend development

Render editorial content as accessible, efficient, discoverable pages.
Apply the sections relevant to the task, using the project's existing design and asset pipeline.

## Trace the rendering path

- Inspect installed Wagtail and Django versions, the page or block model, template inheritance, context builders, frontend assets, and nearby tests.
- Identify whether the value is plain text, rich text, a bound block, a chooser value, or a rendered fragment before changing escaping or markup.
- Check both normal rendering and editor preview when the component is previewable. Reuse existing components and tokens rather than introducing a new framework or parallel styling system.
- Read only the relevant references below. Replace `stable` in Wagtail links with the installed release's documentation version; locate other Markdown docs through [llms.txt](https://docs.wagtail.org/llms.txt).

## Render through Wagtail's APIs

- Load the needed tag libraries explicitly. Render rich text model fields with `|richtext` and StreamField or bound blocks with `{% include_block %}`. Do not replace them with `|safe`: stored rich text needs internal links and embeds expanded.
- Use `{% include_block %}` where block templates need the current context. Preserve `request` when passing through inclusion tags or custom rendering; `include ... only` can remove required context.
- Distinguish block definitions, bound blocks, and values. A child inside a `StructBlock` or `ListBlock` may be a plain value; use the documented bound-block/rendering pattern for custom child templates.
- Keep ordinary text autoescaped, including captions, alt text, and metadata attributes. Do not inject rich HTML into an attribute. Associate a section with a visible heading using `aria-labelledby` when that heading contains rich text.
- Use `{% pageurl %}`, `{% fullpageurl %}`, or page URL methods with request context. Do not assemble URLs from slugs or assume every link belongs to the default site's hostname.
- Preserve the Wagtail userbar and preview integration. When customizing checker items, preserve unrelated controls and the hook's list-mutation contract.
- Use Wagtail's preview-aware cache tags where caching page fragments. Vary other caches by relevant site, locale, and audience; never let preview content populate a public cache.

Read for template changes:

- [writing templates](https://docs.wagtail.org/en/stable/topics/writing_templates.html.md)
- [StreamField rendering](https://docs.wagtail.org/en/stable/topics/streamfield.html.md): for nested values

## Make semantics and interaction accessible

- Use semantic landmarks, a descriptive page heading, and a logical heading hierarchy. Choose heading levels for structure and CSS for appearance. Avoid empty headings and duplicate IDs when blocks repeat.
- Use links for navigation and buttons for actions. Give controls meaningful accessible names, preserve visible focus, and ensure keyboard access and sensible focus order.
- Keep DOM order meaningful at narrow widths and high zoom. Avoid CSS reordering that makes visual and keyboard reading order disagree.
- Preserve readable contrast and visible states across themes. Do not rely on color alone or remove focus outlines without an adequate replacement.
- Respect reduced-motion preferences and keep essential content available without animation. Use progressive enhancement for interactive components.
- For images, preserve the editor's contextual alternative and intentional decorative choice. An empty `alt=""` must not trigger a fallback to the media title. Do not mutate shared image metadata for one placement.
- Give embedded frames descriptive titles; retain captions, transcripts, and table headers/captions where required by the content.
- Use the page's locale for `<html lang>` where available, retaining regional language subtags. For views without a page, use the active Django language.

Read for the component being built:

- [Wagtail accessibility considerations](https://docs.wagtail.org/en/stable/advanced_topics/accessibility_considerations.html.md)
- [WAI tutorials](https://www.w3.org/WAI/tutorials/)

## Preserve form behavior and feedback

- Render the bound form so submitted values, help text, and field errors survive validation failures. Keep CSRF protection, the form action/method, and the successful submission flow intact.
- Associate labels with input IDs. Group related choices with `fieldset` and `legend`; indicate required and optional fields clearly.
- Put errors beside their fields and connect help/error text through `aria-describedby`. Mark invalid controls with `aria-invalid="true"` and render non-field errors in a discoverable location.
- Preserve existing description IDs when adding an error reference. Escape feedback and values; do not rebuild inputs from raw POST data.
- Prefer the installed Django version's accessible rendering features or the project's form components before manually duplicating widget logic. Check actual generated IDs, especially for grouped widgets and repeated forms.

Read for custom form widgets:

- [accessible forms](https://www.w3.org/WAI/tutorials/forms/)
- The installed Django version's form rendering documentation

## Deliver appropriate media and reduce resource use

- Generate renditions through Wagtail's image or picture tags. Use `width`/`max` for uncropped images and `fill` only when cropping is intended; retain focal-point behavior where applicable.
- Choose a small set of responsive candidates appropriate to the layout, with accurate `sizes` and intrinsic dimensions. Preserve aspect ratio with responsive CSS and avoid sending original uploads or unnecessary oversized variants.
- Keep contextual alt text when using assigned rendition objects or custom `<picture>` markup. Do not assume the rendition's default alt text captures an `ImageBlock` value's context.
- Lazy-load below-the-fold media; avoid lazy-loading the likely largest above-the-fold image. Preserve format fallbacks and handle absent images and small source files.
- Reuse existing renditions and optimize repeated image queries. Avoid generating many near-identical sizes or triggering external embed fetches on every render.
- Prefer CSS and native HTML behavior where sufficient. Keep essential reading and navigation usable without JavaScript; load scripts, fonts, embeds, and third-party resources only where they are needed.
- Measure transferred bytes, requests, layout shifts, and render/query cost on representative pages. Describe measured resource reductions; do not infer precise carbon savings from page weight alone.

Read for relevant media and performance techniques:

- [images in templates](https://docs.wagtail.org/en/stable/topics/images.html.md)
- [performance](https://docs.wagtail.org/en/stable/advanced_topics/performance.html.md)
- [sustainability considerations](https://docs.wagtail.org/en/stable/advanced_topics/sustainability_considerations.html.md)

## Keep metadata and discovery tied to content

- Reuse `seo_title` and `search_description` where they meet the need. Define explicit fallbacks without creating competing editorial sources or persisting computed fallback copy unnecessarily.
- Emit a single intended title, description, canonical link, and each social metadata value. Keep attribute values plain and escaped; use valid absolute URLs where required.
- Derive canonical URLs from the site's URL policy and Wagtail routing. Do not turn arbitrary request query parameters into canonical URLs or hard-code a default host into a multisite component.
- For language alternatives, link to the current page and its actual live public translations using each translation's locale and URL. Do not substitute locale homepages or expose restricted translations.
- Use Wagtail's sitemap integration and place its URL before the catch-all page route. Verify public visibility, site scope, generated scheme/host, and any custom routable-page entries.
- Keep structured data accurate and consistent with visible content. Generate JSON-LD with proper JSON serialization and safe HTML embedding; never interpolate unescaped editorial values into a script element.
- Preserve intended crawler and indexing controls for previews, staging, and private content. `robots.txt` and `noindex` do not enforce access control.

When changing discovery behavior, read:

- [sitemaps](https://docs.wagtail.org/en/stable/reference/contrib/sitemaps.html.md)
- [internationalization](https://docs.wagtail.org/en/stable/advanced_topics/i18n.html.md)
- [Google's SEO guidance](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)

## Treat GEO as an evidence-based publishing concern

- Clarify the intended consumer when the task concerns generative engine optimization: search features, an assistant fetching pages, or a specific content integration.
- Provide crawlable text, clear headings, stable URLs, and accurate attribution and dates where applicable. Keep structured data aligned with visible content; do not invent facts or hidden text for bots.
- Check current primary documentation before claiming a provider needs special markup. Google documents no extra markup or AI text-file requirement for its AI search features; do not generalize that to every provider or promise inclusion.
- Add `llms.txt` or Markdown representations when requested or justified by a concrete consumer. Generate them from the same public content and preserve privacy, locale, link resolution, and freshness; do not create an independently maintained copy of the site.

For claims about Google AI search behavior, read:

- [Google's AI features guidance](https://developers.google.com/search/docs/appearance/ai-features)

## Verify rendered output

- Run relevant template checks, frontend builds, and rendering tests. Inspect actual HTML with representative editorial content, including blank fields, quotes, internal links, repeated blocks, and long text.
- For interaction or layout changes, check keyboard use, focus, narrow viewports, zoom, and relevant user preferences. Use automated accessibility checks to supplement manual inspection; a passing scan is not a complete accessibility assessment.
- For media/performance changes, inspect selected image resources, dimensions, and network cost. For metadata changes, check the document head, public translations, and sitemap output.
- Check preview as well as public rendering when affected. Report visible changes, verification results, and any browser or assistive-technology checks that remain unperformed.

---
name: backend
description: Implement and review Wagtail backend behavior using Django and Python practices. Use for page queries, search, routing, permissions, revisions, snippets, forms, workflows, signals, data migrations, or backend performance. Focus on runtime correctness and data integrity; use content-modeling guidance for schema design and frontend guidance for rendered UI.
license: BSD-3-Clause
---

# Wagtail backend development

Preserve Wagtail's publishing, permission, and data contracts while implementing the requested behavior.
Apply only the sections relevant to the change.

## Work with the project's architecture

- Inspect installed Python, Django, and Wagtail versions, project instructions, settings, and existing tests. Use the existing dependency manager, formatter, linter, and test runner.
- Trace the affected request or operation from entry point to queryset, mutation, and response. Identify whether it runs publicly, in the admin, in preview, or as a background operation.
- Prefer documented Wagtail hooks, model methods, panels, forms, and viewsets over copied core views or monkey patches. Use ordinary Django code for behavior outside Wagtail's extension points.
- Preserve superclass behavior when extending methods such as `get_context`, form validation, or hooks. Keep request-specific state off shared block instances, class attributes, and module globals.
- Follow local Python conventions; use supported syntax, timezone-aware dates, lazy translations for model/admin labels, and explicit exception handling. Do not catch broad exceptions to hide content or permission failures.
- Consult the relevant docs below for unfamiliar APIs. Replace `stable` with the installed release's documentation version; locate Markdown pages through [llms.txt](https://docs.wagtail.org/llms.txt). Use installed source and tests if docs and runtime disagree.

## Build correctly scoped queries

- For public page listings, combine `.live()` and `.public()`; each enforces a different boundary. Account for inherited page restrictions.
- Resolve the request's Wagtail site with `Site.find_for_request(request)` when needed. Scope results to the intended root or section, and to the relevant locale. Decide whether the root itself belongs in the results.
- Treat `.in_menu()` as an editorial navigation flag, not a privacy check. Do not assume a chooser's selection restrictions enforce public visibility at render time.
- Apply visibility, site, locale, and business filters before search/pagination where supported. Do not remove hidden results after slicing: that produces incorrect counts and holes.
- Use stable ordering with a tie-breaker for paginated lists. Preserve the query and route parameters across pagination links.
- Query a concrete page model when only that type is needed. Use `.specific()` when mixed page results need subclass fields, avoiding individual `.specific` fetches in loops.
- Keep reusable queryset methods composable; paginate at the consumer that needs a page of results.

Read for the applicable boundaries:

- [page querysets](https://docs.wagtail.org/en/stable/reference/pages/queryset_reference.html.md)
- [internationalization](https://docs.wagtail.org/en/stable/advanced_topics/i18n.html.md)

## Preserve publishing and preview semantics

- Distinguish stored model state, latest revision, and live revision. Do not assume `.save()` publishes, or that the newest revision is public.
- Use Wagtail's revision and publish/unpublish APIs for editorial operations. Do not toggle `live` or bulk-update revisioned content to imitate publication.
- Check draft-enabled snippets separately from pages. A live snippet's database row can contain newer draft content; render its published revision where needed and handle unpublished and legacy states deliberately.
- Carry request context through block rendering and template tags. Treat preview mode as trusted server-side state; ordinary query parameters must not grant access to protected content.
- Preserve intentional empty preview overrides. Distinguish a missing value from an explicitly empty value rather than using truthiness for both.
- Keep preview and personalized responses out of shared public caches. Use Wagtail's preview-aware cache tags for page fragments and include all relevant site, language, and audience variations in custom cache keys.

Before changing these paths, read as needed:

- [snippet features](https://docs.wagtail.org/en/stable/topics/snippets/features.html.md)
- [personalization](https://docs.wagtail.org/en/stable/advanced_topics/content_personalization.html.md)
- [caching guidance](https://docs.wagtail.org/en/stable/advanced_topics/performance.html.md)

## Enforce permissions where actions happen

- Reuse Wagtail permission policies and page permissions for the object and operation. Check authorization in the action handler as well as any UI visibility logic.
- For custom workflow tasks, keep editor access, available actions, task-state querysets, and action execution consistent. Recheck current user eligibility when acting on an existing workflow state.
- Do not grant broad access solely because a user is logged in, staff, or previously assigned. Follow the task's documented superuser and inactive-account semantics.
- Keep Django form validation and CSRF protection on ordinary form submissions. A presentation fix must not bypass the real submission, validation, or success path.
- Use `format_html` for generated HTML with interpolated values, template autoescaping for ordinary fields, and `json_script` for passing data into JavaScript. Do not use `mark_safe` on untrusted strings.

Read for permission changes:

- [permissions](https://docs.wagtail.org/en/stable/topics/permissions.html.md)
- [tasks and workflows](https://docs.wagtail.org/en/stable/extending/custom_tasks.html.md): for custom moderation

## Put side effects at the right lifecycle event

- Use publication events for publication behavior, not generic model saves. Account for updates, scheduled publication, unpublish/republish, and rollback according to the requirement.
- Defer external effects with `transaction.on_commit()` so rolled-back changes do not announce success. Register callbacks using stable values rather than late-bound loop variables or mutable request state.
- Do not claim exactly-once delivery from a signal or `on_commit()` alone. Where delivery must survive retries or process crashes, use an idempotency record or transactional outbox appropriate to the project's infrastructure.
- Keep receivers narrowly scoped and registration repeatable. Avoid adding a queue or service for behavior that does not require one.

When implementing lifecycle effects, read:

- [Wagtail signals](https://docs.wagtail.org/en/stable/reference/signals.html.md)
- [Django transactions](https://docs.djangoproject.com/en/stable/topics/db/transactions/)

## Preserve data when changing storage

- Inspect existing values and define conflict, empty-value, and reversal policies before writing a data migration or repair command.
- Use historical models from the migration app registry. Preserve unrelated fields, IDs, ordering, timestamps, and editorial states unless changing them is the requirement.
- Include saved revisions when their content must follow the new schema. Use Wagtail's StreamField migration tools for block transformations rather than assuming schema migrations rewrite JSON.
- Account for stored form submissions when renaming form fields; changing the current form definition does not rewrite historical submission keys.
- Make rerunnable repair commands idempotent, scope them explicitly, and process large datasets in suitable batches. Do not use bulk updates where required model behavior or signals would be bypassed unintentionally.
- Verify transformations against representative old, new, and mixed data. Do not silently discard a conflict or edit already-applied migration history.

Read as needed when changing storage:

- [StreamField migrations](https://docs.wagtail.org/en/stable/advanced_topics/streamfield_migrations.html.md)
- [form builder](https://docs.wagtail.org/en/stable/reference/contrib/forms/index.html.md)
- [Django data migrations](https://docs.djangoproject.com/en/stable/topics/migrations/#data-migrations)

## Improve search and performance without changing results

- Extend inherited `search_fields` with appropriate `SearchField` or `FilterField` declarations. Use the configured backend's supported filtering and ordering; do not substitute substring queries for full-text search.
- Include index rebuild requirements when indexing changes. Exercise the backend the project actually uses.
- Measure queries through the rendered view or endpoint. Use `select_related` for single-valued relations and `prefetch_related` for collections; preserve editorial ordering and related-object visibility.
- Consume the prefetched relation or `to_attr` result. Calling a newly filtered manager in each template iteration can reintroduce queries despite a prefetch.
- Use `.defer_streamfields()` for listings that do not use body content. Prefetch required image renditions where supported, and pass the request to page URL helpers to reuse site lookups.
- Reduce repeated work before adding caches. Do not improve timing by silently dropping results or serving stale private content. Verify cache invalidation on content changes where caching is modified.

Read for the change at hand:

- [search indexing](https://docs.wagtail.org/en/stable/topics/search/indexing.html.md)
- [searching](https://docs.wagtail.org/en/stable/topics/search/searching.html.md)
- [performance](https://docs.wagtail.org/en/stable/advanced_topics/performance.html.md)

## Verify behavior at the boundary

- Run the project's relevant lint, Django checks, migration checks, and tests. Add regression coverage for changed behavior rather than mirroring implementation details.
- For visibility and workflow changes, cover allowed and denied paths, including inherited restrictions and state transitions. For side effects, exercise commit and rollback.
- For performance work, compare query growth with small and larger representative datasets and confirm the content is unchanged.
- Report what changed, data or operational steps required, and the checks performed. Distinguish observed results from untested assumptions.

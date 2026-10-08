---
name: content-modeling
description: Design and evolve Wagtail content models and editor interfaces. Use when choosing page types, page tree rules, snippets or settings; adding model fields, inline relations, StreamField blocks or rich text; improving block groups, icons, previews and settings; or migrating existing content structures. For rendering-only changes, use frontend guidance instead.
license: BSD-3-Clause
---

# Wagtail content modeling

Build content structures that editors can understand and that preserve existing content. Apply the sections relevant to the requested change; do not redesign unrelated models.

## Establish the content contract

- Inspect the installed Wagtail and Django versions, neighboring models, blocks, panels, templates, migrations, and tests. Reuse the project's conventions where they fit the requirement.
- Identify what editors create, where it belongs, whether it is reused, and whether it needs a URL, ordering, translation, independent publishing, filtering, or reporting.
- For an existing model, trace readers as well as writers: templates, APIs, search, imports, saved revisions, and fixtures. Separate changes to editor presentation from changes to stored data.
- Consult only the relevant docs below. Replace `stable` with the installed release's documentation version before relying on an API. Use the [documentation index](https://docs.wagtail.org/llms.txt) to find other pages; prefer their `.html.md` versions for reading. If offline, inspect matching installed source and tests.

## Choose the right content primitive

| Need                                                                       | Preferred starting point                                                                 |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Routable editorial content with a place in the tree                        | A `Page` subclass                                                                        |
| Reusable content managed independently of pages                            | A registered snippet; add revision, preview, or workflow support only when needed        |
| Configuration shared by a site or installation                             | `BaseSiteSetting` or `BaseGenericSetting`, respectively                                  |
| A fixed attribute that must be queried, sorted, or validated independently | A model field                                                                            |
| An ordered collection owned and revisioned with its parent                 | Child models with `ParentalKey`, `InlinePanel`, and `Orderable` where ordering is needed |
| A flexible sequence of editorial components                                | `StreamField`                                                                            |
| Formatted prose within a defined place                                     | `RichTextField` or `RichTextBlock` with appropriate features                             |

- Keep queryable business data out of opaque rich text or arbitrary block JSON when a model field or relation fits.
- Prefer domain concepts and constrained design choices over raw HTML, arbitrary CSS classes, or a general layout builder. Preserve a deliberate existing page-builder design when it is part of the requirement.
- Use chooser relations for references to pages, images, documents, and snippets. Do not duplicate titles or URLs when the referenced object should remain the source of truth.
- Preserve inherited panels and search fields when extending them. Add `index.SearchField` for new searchable content and account for rebuilding the configured search index.

## Model the page tree deliberately

- Use `parent_page_types` to limit allowed parents and `subpage_types` to limit allowed children. Make both sides consistent; use an empty `subpage_types` list for leaf pages.
- Distinguish an omitted restriction from an empty list. `parent_page_types = []` prevents ordinary creation of that type; it does not mean any parent.
- Use `max_count` or `max_count_per_parent` only when their scope matches the requirement. Do not use a global singleton limit for a per-site requirement.
- Treat the tree as routing and editorial structure. Do not recreate categories, tags, or reusable entities as pages solely to obtain an admin UI.
- Inspect existing placements before tightening rules. Creation restrictions do not relocate existing content. Preserve URLs or plan redirects when moving content is required.
- For programmatic creation and moves, use Wagtail's tree APIs and check placement rules; do not write `path`, `depth`, or `numchild` directly.

Read docs per content model primitives:

- [page models](https://docs.wagtail.org/en/stable/topics/pages.html.md)
- [snippets](https://docs.wagtail.org/en/stable/topics/snippets/index.html.md)
- [settings](https://docs.wagtail.org/en/stable/reference/contrib/settings.html.md)

## Make StreamField usable for editors

- Use `StructBlock` for named parts of one component, `ListBlock` for repeated items of one type, and `StreamBlock` for an ordered mixture of types. Avoid unnecessary nesting.
- Keep block names and choice values stable: they are stored identifiers. Change `label`, help text, or display logic when only the wording should change.
- Set meaningful labels, `help_text`, and registered `icon` names. Use `group` to organize the block picker by editorial purpose; keep its declaration order intentional.
- Distinguish picker groups from the layout inside a `StructBlock`. On versions supporting it, use `Meta.form_layout` to order fields and `BlockGroup(children=[...], settings=[...])` to put secondary controls behind Settings without changing storage nesting.
- On older versions, use supported field ordering or an existing nested settings block. Do not introduce unsupported layout APIs or change the JSON shape just to rearrange the editor.
- Use `label_format` and `collapsed` where summaries make long streams easier to navigate. Check which parent block controls the initial collapsed state.
- Use `required`, `min_num`, `max_num`, and `block_counts` for actual content constraints. For cross-field validation, use the block's `clean()` method and errors associated with the affected child. Do not assume `Model.full_clean()` recursively validates StreamField values.
- Add representative `preview_value`, a useful `description`, and preview templates where the installed version supports them. Reuse the component's real rendering and required assets. A block-picker preview needs a complete document, unlike a normal block fragment.
- Make previews work with an empty media library, absent request, and optional fields. Avoid hard-coded database IDs, writes, or external requests to generate preview content.
- Put derived values for a `StructBlock` in a `StructValue` subclass via `Meta.value_class` when appropriate. Do not assume methods on the block definition become methods on its value or that choice values automatically render as labels.

Read:

- [StreamField](https://docs.wagtail.org/en/stable/topics/streamfield.html.md)
- [Block reference](https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html.md)
- [Block customization](https://docs.wagtail.org/en/stable/advanced_topics/customization/streamfield_blocks.html.md)

## Constrain rich text and media appropriately

- Choose rich text `features` for the field's context. Keep headings consistent with the surrounding document outline; do not offer heading levels solely to change font size.
- Use structured blocks for content with distinct fields or behavior, such as calls to action, rather than asking editors to assemble them in rich text.
- Preserve Wagtail's stored link and embed references. Render with Wagtail's rich text and block rendering APIs; do not treat database HTML as display HTML or replace rendering with `safe`.
- Prefer `wagtail.images.blocks.ImageBlock` on supported versions when editors need contextual alt text and decorative images. Do not overwrite the shared image title or description to change one use's alternative text.
- Provide help text for alt text, embed titles, table headers, and captions where those choices belong to editors.

When definining these controls, read:

- [rich text features](https://docs.wagtail.org/en/stable/advanced_topics/customization/page_editing_interface.html.md)
- [accessible content modeling](https://docs.wagtail.org/en/stable/advanced_topics/accessibility_considerations.html.md)

## Evolve stored content safely

- Generate model migration state for field and block definition changes. Do not assume an `AlterField` rewrites StreamField JSON or revision content.
- Before renaming, removing, or nesting fields or blocks, define how old values map to new ones, including missing values and conflicts. Preserve unrelated content, ordering, links, and identifiers when their meaning is unchanged.
- Migrate current rows and applicable saved revisions. A migrated page must still support previewing, restoring, and publishing an older revision.
- Prefer Wagtail's `MigrateStreamData` and supplied operations for supported transformations. Target the parent block for child rename/remove operations; include `item` when traversing a `ListBlock`.
- Verify migration imports, operation signatures, and revision storage against the installed version before giving executable code. If matching documentation or source is unavailable, give a provisional data-transformation and verification plan instead of inventing API names or revision fields. In particular, do not assume migration reversal restores the original content.
- In versions providing these APIs, import `MigrateStreamData` from `wagtail.blocks.migrations.migrate_operation` and `RenameStreamChildrenOperation` from `wagtail.blocks.migrations.operations`. `MigrateStreamData` is itself a Django migration operation: its `operations_and_block_paths` parameter contains `(operation, path)` pairs; `""` targets the root stream. Do not wrap an invented `.run()` call or substitute similarly named operations.
- Check `MigrateStreamData`'s revision handling before adding a second revision migration: its default processes the affected model rows and their applicable revisions. A `revisions_from` cutoff changes that coverage. Do not hard-code `Revision.content_json` across versions or assume its no-op reverse restores renamed data.
- Use historical models in custom Django data migrations. Inspect actual stored formats, including legacy list data, instead of transforming rendered HTML or the API representation.
- Document whether a data transformation is reversible. Avoid editing already-applied migrations or deleting old data before its replacement has been verified.

Before changing stored block structure, read:

- [StreamField migrations](https://docs.wagtail.org/en/stable/advanced_topics/streamfield_migrations.html.md)

## Verify the affected behavior

- Run project checks and migration checks. For structural changes, exercise the migration against representative old rows and revisions.
- Exercise the affected editor flow: allowed placement, validation, chooser behavior, block ordering, settings, and previews. Save and reload new content.
- Render representative existing content, including blank optional fields and internal links. Check affected API or search consumers when the change reaches them.
- Report the modeling choice, editor-visible changes, migration requirements, and checks performed. State any checks that could not run.

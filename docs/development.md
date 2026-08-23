# Development

Notes for contributors to `wgtl-api-cli`.

## Package layout

Three layers; dependencies point strictly downward:

```
src/wgtl_api_cli/
├── cli/            # Typer layer: argument parsing, orchestration only
│   ├── main.py     # root app, global options, CliContext, get_client(), emit(), appify()
│   ├── _shared.py  # shared is_tty / require_yes helpers
│   ├── auth.py     # whoami, init
│   ├── schema.py   # schema list|show
│   └── pages.py images.py documents.py snippets.py sites.py locales.py redirects.py
├── resources/      # hand-written facade; the only layer CLI code talks to
│   ├── _client.py  # WgtlClient transport (auth, errors, dry-run, verbose)
│   └── pages.py images.py documents.py snippets.py sites.py locales.py redirects.py schema.py
├── client/         # clientele-generated — never hand-edited
│   └── openapi.json  # committed schema snapshot
├── config.py       # config cascade + .wgtl.toml
├── errors.py       # error hierarchy + exit-code mapping
├── output.py       # JSON/human rendering
└── parsing.py      # --field parsing, @file/@-, page-ref resolution
```

- `cli/` commands call `resources/` functions, never HTTP directly.
- `resources/` builds payloads and calls `WgtlClient`; content fields
  (page types, some snippet types) are site-model-specific and are handled as
  generic dicts.
- `client/` is generated from the committed `openapi.json` and only consulted
  for stable, cross-project schemas.

## Setting up

```bash
just install        # uv sync
just test           # run the unit test suite (no integration)
just lint           # ruff check + format --check
just format         # ruff format
```

## Tests

Four test layers:

- **Unit, CLI layer** (`tests/test_cli_*.py`) — Typer `CliRunner` + respx;
  asserts flags, JSON-vs-human output, exit codes per status, config-cascade
  precedence, `--dry-run`, and `-v`.
- **Unit, resources/transport layer** (`tests/test_client.py`,
  `tests/test_resources_*.py`) — respx-mocked HTTP; asserts exact
  method/URL/params/headers/payload shapes the `resources/` layer emits. This is
  where "do we use clientele/httpx correctly" is pinned down.
- **Coverage gap** (`tests/test_coverage_gap.py`) — loads the committed
  `openapi.json` and asserts every operation maps to exactly one registered CLI
  command. Fails when the API gains an endpoint with no command (drift) or a
  command with no endpoint (stale).
- **Generated smoke** (`tests/test_generated_smoke.py`) — asserts the generated
  `client/` package imports and exposes the expected schema classes, so a botched
  regen fails CI.

### Integration tests

`tests/integration/` require a live Wagtail v3 site and are skipped unless the
environment provides one:

```bash
just test-integration
# uses WGTL_TEST_BASE_URL (default http://127.0.0.1:9001/api/v3) and WGTL_TEST_TOKEN
```

The demo project ships the v3 API; see the quickstart for creating a token.

> The demo site's HTTPS cert is a self-signed dev cert the httpx client doesn't
> trust — use the plain-HTTP `http://127.0.0.1:9001/api/v3` loopback URL for
> local integration runs.

## Regenerating the client

The `client/` package is generated from the committed OpenAPI snapshot:

```bash
just generate-client
```

- The `-o` path **must be absolute** so clientele emits relative imports (a
  relative path produces `src.wgtl_api_cli.client` imports that break wheel
  installs).
- Review the resulting diff before committing — v3 is a preview and schema
  churn surfaces here.
- `just generate-client` re-applies the `# GENERATED` marker to
  `client/__init__.py` (clientele zeroes it on regen).

## Adding a command

1. Find the operation in `client/openapi.json` (or the API docs); note the
   request path, method, body fields, and parameters.
2. Add a `resources/` function building the payload and calling the transport
   (or add a method to the existing resource module).
3. Add a `cli/` command in the matching module that parses args, builds the
   payload (via `parsing`/`resources.build_*`), calls `get_client`, and `emit`s.
   Decorate with `@appify`. For mutating commands, guard with `require_yes` and
   offer `--dry-run` (handled automatically by the transport).
4. If the command consumes/creates content, update `tests/test_coverage_gap.py`
   so the operation stays mapped.
5. Add a unit test with `CliRunner` + respx asserting URL, method, and payload.
6. Update `docs/commands.md`.

## Contributing

Run `just lint` and `just test` before finishing. See
[CONTRIBUTING.md](../CONTRIBUTING.md) for the contribution workflow and
[CHANGELOG.md](../CHANGELOG.md) for release notes.
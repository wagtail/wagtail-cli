# Task runner: https://github.com/casey/just
# Requires: `uv` and `just`.

# List all the justfile recipes.
help:
    just --list --list-prefix 'just '

# Remove all the Python cache files.
clean-pyc:
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +

# Install the dependencies.
install: clean-pyc
    uv sync

# Lint the server code with uv.
lint:
    uv run ruff format --check .
    uv run ruff check .

# Format the server code with uv.
format:
    uv run ruff check . --fix
    uv run ruff format .

# Run tests with pytest.
test:
    uv run pytest

# Run tests with coverage.
coverage:
    uv run pytest --cov src/wagtail_cli
    uv run coverage report -m

# Regenerate the clientele client from the committed OpenAPI snapshot.
# NOTE: must pass the output dir as an ABSOLUTE path so clientele generates
# relative imports (src.wagtail_cli.client would break a wheel install).
# The generated client at src/wagtail_cli/client/ is committed and never
# hand-edited; review the resulting diff before committing.
generate-client:
    uv run clientele start-api -f 'src/wagtail_cli/client/openapi.json' -o "$(pwd)/src/wagtail_cli/client/" --regen
    rm -f src/wagtail_cli/client/pyproject.toml
    # clientele overwrites __init__.py with empty content on regen; re-apply
    # the GENERATED marker so it stays durable. Recipe owns this marker.
    printf '%s\n' '# GENERATED — see justfile generate-client' > src/wagtail_cli/client/__init__.py


# Run the integration test suite against a live Wagtail v3 API.
# Requires WAGTAIL_CLI_TEST_BASE_URL and WAGTAIL_CLI_TEST_TOKEN (or the default below).
# NOTE: bakerydemo's HTTPS dev cert at 9001.wagtail.test is NOT trusted by the
# CLI's httpx client; use the plain-HTTP loopback URL for local runs.
test-integration:
    WAGTAIL_CLI_TEST_BASE_URL=$${WAGTAIL_CLI_TEST_BASE_URL:-http://127.0.0.1:9001/api/v3} uv run pytest -m integration



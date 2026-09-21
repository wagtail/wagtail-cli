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

test-lowest-deps:
    #!/usr/bin/env bash
    set -euo pipefail
    lowest_python=$(uv run python -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["requires-python"].removeprefix(">=").strip())')
    uv run --isolated --python "$lowest_python" --resolution lowest-direct pytest

test-highest-deps:
    uv run --isolated --resolution highest pytest

# Run tests with coverage.
coverage:
    uv run pytest --cov src/wagtail_cli
    uv run coverage report -m

# Build the documentation site.
docs-build:
    uv run mkdocs build --strict

# Build the documentation site and serve it locally.
docs-serve:
    uv run mkdocs serve --strict

# Regenerate the clientele client from the committed OpenAPI snapshot.
# NOTE: must pass the output dir as an ABSOLUTE path so clientele generates
# relative imports (tests.clientele_client would break a wheel install).
# The generated client at tests/clientele_client/ is committed and never
# hand-edited; review the resulting diff before committing.
generate-client:
    uv run clientele start-api -f 'tests/clientele_client/openapi.json' -o "$(pwd)/tests/clientele_client/" --regen
    rm -f tests/clientele_client/pyproject.toml
    # clientele overwrites __init__.py with empty content on regen; re-apply
    # the GENERATED marker so it stays durable. Recipe owns this marker.
    printf '%s\n' '# GENERATED — see justfile generate-client' > tests/clientele_client/__init__.py


# Run the integration test suite against a live Wagtail v3 API.
# Requires WAGTAIL_CLI_TEST_BASE_URL and WAGTAIL_CLI_TEST_TOKEN (or the default below).
# NOTE: bakerydemo's HTTPS dev cert at 9001.wagtail.test is NOT trusted by the
# CLI's httpx client; use the plain-HTTP loopback URL for local runs.
test-integration:
    WAGTAIL_CLI_TEST_BASE_URL=$${WAGTAIL_CLI_TEST_BASE_URL:-http://127.0.0.1:9001/api/v3} uv run pytest -m integration

# Eval tooling; also needs the OpenCode CLI (https://opencode.ai/docs/).
eval-init:
    npm install -g promptfoo@latest @opencode-ai/sdk

# Run the agent-skill evals (see docs/prompts/README.md).
eval *args="":
    #!/usr/bin/env bash
    set -euo pipefail
    configs="docs/prompts/wagtail_api_skill.yaml docs/prompts/wagtail_docs_skill.yaml"
    if [ $# -gt 0 ] && [[ "${1}" == *.yaml ]]; then
        configs="${1}"
        shift
    fi
    for config in ${configs}; do
        OPENCODE_CONFIG="$PWD/docs/prompts/opencode.json" promptfoo eval -c "${config}" --no-cache "$@"
    done

# Open the promptfoo viewer for the most recent eval results.
eval-view:
    promptfoo view -y

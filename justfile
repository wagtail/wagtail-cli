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
    uv run pytest --cov src/wgtl_api_cli
    uv run coverage report -m

# Regenerate the clientele client from the committed OpenAPI snapshot.
# NOTE: must pass the output dir as an ABSOLUTE path so clientele generates
# relative imports (src.wgtl_api_cli.client would break a wheel install).
# The generated client at src/wgtl_api_cli/client/ is committed and never
# hand-edited; review the resulting diff before committing.
generate-client:
    uv run clientele start-api -f 'src/wgtl_api_cli/client/openapi.json' -o "$(pwd)/src/wgtl_api_cli/client/" --regen
    rm -f src/wgtl_api_cli/client/pyproject.toml
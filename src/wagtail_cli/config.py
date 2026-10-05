from __future__ import annotations

import os
import tomllib

from dataclasses import dataclass
from pathlib import Path


USER_DOTFILE_NAME = ".wagtail-cli.toml"

SCHEMA_URL = "https://wagtail.github.io/wagtail-cli/schema/wagtail-cli.json"
"""Published JSON Schema for the dotfiles, used for editor validation."""


def _user_dotfile() -> Path:
    return Path.home() / USER_DOTFILE_NAME


def _project_dotfile() -> Path:
    return Path.cwd() / USER_DOTFILE_NAME


@dataclass
class Config:
    base_url: str | None = None
    token: str | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.token)


def _read_dotfile(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text())
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}


def load_config(cli_url: str | None = None, cli_token: str | None = None) -> Config:
    cfg = Config()
    for path in (_user_dotfile(), _project_dotfile()):  # user first, project wins
        data = _read_dotfile(path)
        cfg.base_url = data.get("url", cfg.base_url)
        cfg.token = data.get("token", cfg.token)
    cfg.base_url = os.environ.get("WAGTAIL_CLI_BASE_URL", cfg.base_url)
    cfg.token = os.environ.get("WAGTAIL_CLI_TOKEN", cfg.token)
    if cli_url:
        cfg.base_url = cli_url
    if cli_token:
        cfg.token = cli_token
    return cfg


def save_user_config(config: Config, path: Path | None = None) -> Path:
    path = path or _user_dotfile()
    path.parent.mkdir(parents=True, exist_ok=True)
    # The leading `#:schema` hint lets TOML-aware editors (Taplo, Even Better
    # TOML, JetBrains) validate and complete the keys in this file.
    path.write_text(
        f"#:schema {SCHEMA_URL}\n"
        f'url = "{config.base_url}"\ntoken = "{config.token or ""}"\n'
    )
    os.chmod(path, 0o600)
    return path

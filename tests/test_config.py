import tomllib

from wagtail_cli.config import Config, load_config, save_user_config


def _isolate(monkeypatch, tmp_path):
    user = tmp_path / "user" / ".wagtail-cli.toml"
    proj = tmp_path / "proj" / ".wagtail-cli.toml"
    monkeypatch.setattr("wagtail_cli.config._user_dotfile", lambda: user)
    monkeypatch.setattr("wagtail_cli.config._project_dotfile", lambda: proj)
    monkeypatch.delenv("WAGTAIL_CLI_BASE_URL", raising=False)
    monkeypatch.delenv("WAGTAIL_CLI_TOKEN", raising=False)
    return user, proj


def test_cli_flags_beat_env(monkeypatch, tmp_path):
    user, _ = _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", "https://env.example")
    monkeypatch.setenv("WAGTAIL_CLI_TOKEN", "env-tok")
    cfg = load_config(cli_url="https://cli.example", cli_token="cli-tok")
    assert (cfg.base_url, cfg.token) == ("https://cli.example", "cli-tok")


def test_env_beats_project_dotfile(monkeypatch, tmp_path):
    user, proj = _isolate(monkeypatch, tmp_path)
    proj.parent.mkdir(parents=True)
    proj.write_text('url = "https://proj.example"\ntoken = "proj-tok"\n')
    monkeypatch.setenv("WAGTAIL_CLI_BASE_URL", "https://env.example")
    cfg = load_config()
    assert cfg.base_url == "https://env.example"
    assert cfg.token == "proj-tok"  # per-key merge


def test_project_beats_user_dotfile(monkeypatch, tmp_path):
    user, proj = _isolate(monkeypatch, tmp_path)
    user.parent.mkdir(parents=True)
    proj.parent.mkdir(parents=True)
    user.write_text('url = "https://user.example"\ntoken = "user-tok"\n')
    proj.write_text('url = "https://proj.example"\n')
    cfg = load_config()
    assert cfg.base_url == "https://proj.example"
    assert cfg.token == "user-tok"


def test_missing_everything(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    cfg = load_config()
    assert cfg.base_url is None and cfg.token is None
    assert cfg.is_configured is False


def test_save_user_config_round_trip(tmp_path):
    path = tmp_path / "sub" / ".wagtail-cli.toml"
    out = save_user_config(Config(base_url="https://x", token="t"), path=path)
    data = tomllib.loads(out.read_text())
    assert data == {"url": "https://x", "token": "t"}


def test_save_user_config_restricts_permissions(tmp_path):
    path = tmp_path / "sub" / ".wagtail-cli.toml"
    save_user_config(Config(base_url="https://x", token="t"), path=path)
    import stat

    assert stat.S_IMODE(path.stat().st_mode) == 0o600

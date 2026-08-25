# How the template works

This project uses [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/) to generate new Wagtail/Django packages. Unlike typical cookiecutter templates that use a directory full of cookiecutter interpolation placeholders, this repository is itself a working Django/Wagtail package. The template generation happens through a custom overlay mechanism.

## Template structure

The repository root contains the full, runnable package:

```
├── src/wagtail_cli/   # The Django app (source code)
├── tests/                 # Test suite
├── demo/                  # Demo Wagtail site
├── .github/workflows/     # CI configuration
├── justfile               # Task runner recipes
├── pyproject.toml         # Package metadata and build config
├── package.json           # Node.js tooling (Prettier)
└── template/              # Files that differ for generated packages
    ├── README.md
    ├── CONTRIBUTING.md
    ├── CHANGELOG.md
    ├── LICENSE
    └── ROADMAP.md
```

Most files at the root are the template -- they are copied as-is to generated packages. Only the files in `template/` differ between this repository and what users get.

## The overlay mechanism: `hooks/pre_prompt.py`

Cookiecutter supports [hooks](https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html) that run at different stages of template generation. This project uses a `pre_prompt` hook ([hooks/pre_prompt.py](../hooks/pre_prompt.py)) that runs before cookiecutter prompts the user for input. It does the following:

### 1. Copy and merge

The hook copies the entire repository root into a target directory, excluding a few paths that shouldn't be part of the generated package:

- `template/` (overlaid separately)
- `hooks/` (cookiecutter internals)
- `cookiecutter.json` (cookiecutter config)
- `.git/` and `__pycache__/`

It then overlays the contents of `template/` on top, so files like `template/README.md` replace the root `README.md` in the generated output.

### 2. Rename project directories

Any directory named `wagtail_cli` is renamed to `wagtail_cli`, which cookiecutter then resolves to the user's chosen project name in snake_case.

### 3. Replace placeholders in file contents

The hook performs text replacements across all text files, converting placeholder values to cookiecutter template variables:

| Placeholder | Cookiecutter variable | Example output |
|---|---|---|
| `wagtail_cli` | `wagtail_cli` | `wagtail_color_picker` |
| `wagtail-cli` | `wagtail-cli` | `wagtail-color-picker` |
| `WgtlApiCli` | `WgtlApiCli` | `WagtailColorPicker` |
| `wagtail-cli` | `wagtail-cli` | `Wagtail Color Picker` |
| `Experimental CLI API client for Wagtail` | `Experimental CLI API client for Wagtail` | `A color picker field for Wagtail` |
| `https://github.com/org-name-or-username/wagtail-cli` | `https://github.com/wagtail/wagtail-cli` | `https://github.com/user/wagtail-color-picker` |
| `2026` | `2026` | `2026` |

Only text files are processed (`.py`, `.md`, `.json`, `.toml`, `.yml`, `.yaml`, `.js`, `.css`, `.html`, `.xml`, `.ini`, `.cfg`, `.sh`, `.bat`, and dotfiles).

## Why this approach

The main benefit is that the template is always runnable and testable. Contributors can `just install && just demo` to work on it, CI runs the full test suite, and linters check real code rather than template syntax. Changes to the package structure or tooling are made once in the root files and automatically flow through to generated packages.

## Further reading

- [Cookiecutter documentation](https://cookiecutter.readthedocs.io/en/stable/)
- [Cookiecutter hooks](https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html)
- [cookiecutter.json reference](https://cookiecutter.readthedocs.io/en/stable/advanced/template_extensions.html)

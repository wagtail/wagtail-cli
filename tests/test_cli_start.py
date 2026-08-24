from wagtail_cli.cli.main import build_startproject_args


DEFAULT_TEMPLATE = (
    "https://github.com/wagtail/wagtail-custom-base-page-template/archive/main.zip"
)


def test_start_defaults():
    args = build_startproject_args(
        "myproj",
        None,
        DEFAULT_TEMPLATE,
        ["html", "rst"],
        ["Dockerfile"],
        [],
        1,
        None,
        None,
        False,
        False,
        False,
        False,
    )
    assert args == [
        "django-admin",
        "startproject",
        f"--template={DEFAULT_TEMPLATE}",
        "--ext=html,rst",
        "--name=Dockerfile",
        "myproj",
    ]


def test_start_directory_and_overrides():
    args = build_startproject_args(
        "myproj",
        "dest",
        "https://x/tmpl.zip",
        ["py", "html"],
        ["README"],
        ["foo"],
        2,
        "site.settings",
        "/tmp/p",  # noqa: S108
        True,
        True,
        True,
        True,
    )
    assert args == [
        "django-admin",
        "startproject",
        "--template=https://x/tmpl.zip",
        "--ext=py,html",
        "--name=README",
        "--exclude=foo",
        "myproj",
        "dest",
        "--version",
        "--verbosity=2",
        "--settings=site.settings",
        "--pythonpath=/tmp/p",
        "--traceback",
        "--no-color",
        "--force-color",
    ]

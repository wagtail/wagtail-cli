"""Guard that both copies of the `wagtail` skill match the pinned checksum.

Regenerate after editing the skill:

    cp src/wagtail_cli/.agents/skills/wagtail/SKILL.md skills/wagtail/SKILL.md
    shasum -a 256 src/wagtail_cli/.agents/skills/wagtail/SKILL.md
"""

import hashlib

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = [
    REPO_ROOT / "skills" / "wagtail" / "SKILL.md",
    REPO_ROOT / "src" / "wagtail_cli" / ".agents" / "skills" / "wagtail" / "SKILL.md",
]
SHA256 = "dbd0f6defbc15da9f90913285bc1c5804408f18b7c3a4d95aac7b2478520040f"


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_skill_matches_pinned_checksum(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == SHA256, (
        f"{path.relative_to(REPO_ROOT)} changed; update both copies and SHA256 to {digest}"
    )

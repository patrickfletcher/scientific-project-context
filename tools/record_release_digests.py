"""Regenerate the earlier-package-text digests from release commits.

Run from the repository root after a release is tagged, listing every release
whose text `check` and `upgrade` should recognize:

    python tools/record_release_digests.py 8315b53=0.1.0.dev22 v0.1.0.dev23=0.1.0.dev23 ...

It reads the packaged files at each ref with `git show`, hashes each tracked
region exactly as the package does, and rewrites
`src/scientific_project_context/history.py`. Never list the current source
version: text it still ships must not read as earlier.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_project_context.project import (  # noqa: E402
    CONTEXT_ROUTE_BEGIN,
    CONTEXT_ROUTE_END,
    SCIENTIFIC_PRACTICE_BEGIN,
    SCIENTIFIC_PRACTICE_END,
    SKILL_TRIGGER_SEPARATOR,
    extract_managed_block,
    parse_agent_skill_content,
)

HISTORY = ROOT / "src" / "scientific_project_context" / "history.py"
HEADER = '''"""Recognize text that an earlier package version shipped in a tracked region.

A project that has not upgraded, or a branch that merged an older copy, holds the
packaged text of an earlier version rather than its own edits. Naming that
version turns "this differs" into "the upgrade replaces this". Digests are of the
region text with LF line endings, taken from this repository's release commits
by `tools/record_release_digests.py`; versions before 0.1.0.dev22 are not
recorded. Regenerate this file with that tool; do not edit it by hand.
"""

from __future__ import annotations

import hashlib

# Region key -> SHA-256 of the packaged region text -> versions that shipped it.
'''
FOOTER = '''

def region_digest(text: str) -> str:
    return hashlib.sha256(text.replace("\\r\\n", "\\n").encode("utf-8")).hexdigest()


def earlier_package_version(region: str, text: str) -> str | None:
    """Return the earlier package version that shipped this exact region text, if any."""

    versions = EARLIER_PACKAGED_REGIONS.get(region, {}).get(region_digest(text))
    if not versions:
        return None
    if len(versions) == 1:
        return versions[0]
    return f"{versions[0]} to {versions[-1]}"
'''


def show(ref: str, path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, check=False
    )
    return result.stdout if result.returncode == 0 else None


def digest(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def packaged_description(description: str) -> str:
    return description.split(SKILL_TRIGGER_SEPARATOR, 1)[0].strip()


def collect(releases: list[tuple[str, str]]) -> dict[str, dict[str, list[str]]]:
    table: dict[str, dict[str, list[str]]] = {}

    def add(key: str, text: str | None, version: str) -> None:
        if text is None:
            return
        versions = table.setdefault(key, {}).setdefault(digest(text), [])
        if version not in versions:
            versions.append(version)

    for ref, version in releases:
        agents = show(ref, "template/AGENTS.md")
        if agents is not None:
            state, block = extract_managed_block(agents, CONTEXT_ROUTE_BEGIN, CONTEXT_ROUTE_END)
            add("routing", block if state == "present" else None, version)
        practice = show(ref, "template/.context/scientific-practice.md")
        if practice is not None:
            state, block = extract_managed_block(
                practice, SCIENTIFIC_PRACTICE_BEGIN, SCIENTIFIC_PRACTICE_END
            )
            add("practice_core", block if state == "present" else None, version)
        listing = subprocess.run(
            ["git", "ls-tree", "--name-only", f"{ref}:template/.agents/skills"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        for name in sorted(listing.stdout.split()):
            content = show(ref, f"template/.agents/skills/{name}/SKILL.md")
            if content is None:
                continue
            parts = parse_agent_skill_content(content)
            add(f"skill:{name}", parts.body, version)
            add(f"description:{name}", packaged_description(parts.description), version)
    return table


def render(table: dict[str, dict[str, list[str]]]) -> str:
    lines = [HEADER.rstrip("\n"), "EARLIER_PACKAGED_REGIONS: dict[str, dict[str, tuple[str, ...]]] = {"]
    for key in sorted(table):
        lines.append(f'    "{key}": {{')
        for value, versions in table[key].items():
            joined = ", ".join(f'"{version}"' for version in versions)
            lines.append(f'        "{value}": ({joined},),')
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines) + "\n" + FOOTER


def main(argv: list[str]) -> int:
    releases = []
    for item in argv:
        ref, _, version = item.partition("=")
        if not ref or not version:
            print(f"expected REF=VERSION, got {item!r}", file=sys.stderr)
            return 2
        releases.append((ref, version))
    if not releases:
        print(__doc__, file=sys.stderr)
        return 2
    HISTORY.write_text(render(collect(releases)), encoding="utf-8")
    print(f"wrote {HISTORY.relative_to(ROOT)} from {len(releases)} releases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

"""Report sentence-length statistics for shipped Markdown.

A maintainer aid for the writing rules in `.context/glossary.md` and the starter
tests: it reports how long sentences are, so a rewrite can be compared with what
it replaced. List items count as sentences; code, tables, and headings are
ignored. Usage:

    python tools/style_metrics.py [files...]

With no files, it reads every Markdown file under `template/`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FENCED_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\[([^\]\n]*)\]\([^)\n]*\)")
ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
BOUNDARY_RE = re.compile(r"(?<=[.!?;:])\s+(?=[A-Z\"(`*])")


def sentences(text: str) -> list[str]:
    """Split Markdown prose into sentences and list items, ignoring code and tables."""

    text = FRONTMATTER_RE.sub("", text)
    text = FENCED_RE.sub("", text)
    text = COMMENT_RE.sub("", text)
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "|", ">")) or ITEM_RE.match(line):
            if current:
                blocks.append(" ".join(current))
                current = []
            if ITEM_RE.match(line):
                current = [ITEM_RE.sub("", line).strip()]
            continue
        current.append(stripped)
    if current:
        blocks.append(" ".join(current))
    found: list[str] = []
    for block in blocks:
        block = LINK_RE.sub(r"\1", INLINE_CODE_RE.sub("Code", block))
        found.extend(part for part in BOUNDARY_RE.split(block) if len(part.split()) >= 3)
    return found


def word_count(sentence: str) -> int:
    return len(sentence.split())


def main(argv: list[str]) -> int:
    paths = [Path(arg) for arg in argv] or sorted((ROOT / "template").rglob("*.md"))
    print(f"{'file':58} {'sent':>5} {'mean':>5} {'>20':>5} {'>25':>5} {'max':>4}")
    for path in paths:
        lengths = [word_count(s) for s in sentences(path.read_text(encoding="utf-8"))]
        if not lengths:
            continue
        count = len(lengths)
        name = path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else str(path)
        print(
            f"{name[-58:]:58} {count:5d} {sum(lengths) / count:5.1f} "
            f"{sum(n > 20 for n in lengths) / count:5.0%} "
            f"{sum(n > 25 for n in lengths) / count:5.0%} {max(lengths):4d}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

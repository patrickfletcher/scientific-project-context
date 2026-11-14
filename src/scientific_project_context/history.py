"""Recognize text that an earlier package version shipped in a tracked region.

A project that has not upgraded, or a branch that merged an older copy, holds the
packaged text of an earlier version rather than its own edits. Naming that
version turns "this differs" into "the upgrade replaces this". Digests are of the
region text with LF line endings, taken from this repository's release commits;
versions before 0.1.0.dev22 are not recorded.
"""

from __future__ import annotations

import hashlib

# Region key -> SHA-256 of the packaged region text -> versions that shipped it.
EARLIER_PACKAGED_REGIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "routing": {
        "5dad873957e4ee305ec73b5ce46c2154c514bd7b68ac2cea2d6d911ca0440aa5": ("0.1.0.dev22",),
        "ee28b1495f7201b3f8e85c0743e7200a79b8c363ac730192cf8827d8fbf20b0f": ("0.1.0.dev23",),
        "2d3c8944c7769ae870452c3e74d6f5bf3d3235c8a8971044575cc4ed0bb430e7": ("0.1.0.dev24", "0.1.0.dev25",),
    },
    "practice_core": {
        "d5618875b4ffe7d4363f2064fc202bc56c5ea5d48a84bcb537104f02a4a28659": ("0.1.0.dev22",),
        "5c3b8e2aae495850c9fe34f994956121f58872694bb9ab0424d57dce6adbc92f": ("0.1.0.dev23",),
        "3815e94784f58ea0087823854f082378d175706fb00ea0cfaac704b202fa9ab8": ("0.1.0.dev24", "0.1.0.dev25",),
    },
    "skill:spctx-project-context": {
        "adea19f4a969f9cba89bfe1715e041244570fafc233f858ca3dba72f150c9f64": ("0.1.0.dev22",),
        "91e8fdbf106fd6088b0547c68be246e64c86cef0e3d5452c32c1548d2ddfc744": ("0.1.0.dev23",),
        "46ee40a58fa19ed6b343406bfd5eb73b3c0c71d89f5798748958329c381b6a20": ("0.1.0.dev24",),
        "401ebb9114502a87ad3199e3fc21c038e8547fb2ebfdbbb699fa0cbbee1dfbc4": ("0.1.0.dev25",),
    },
    "skill:spctx-public-writing": {
        "2b82465e761e66b3d1973b2cf09405256729129bf11014d4bee5eb834cb2d00d": ("0.1.0.dev22",),
        "06b553f374a90669d0df5e7a8a83a0e6a31bc031eeff3daa46d9db2f958f5458": ("0.1.0.dev23",),
        "85eb3ac9a3d07b84df810a5b3c5b8f5e2e20d227cb40e4608f73ec5c674b9a4c": ("0.1.0.dev24", "0.1.0.dev25",),
    },
    "skill:spctx-scientific-change": {
        "44cd1dfc23c648e6498aa9a240075a222d2333b4306acbadcebecb6597e05a78": ("0.1.0.dev22",),
        "31491c5caad8b56cd630393d3f0c4fdaa89606227e0721698295af2c3f401aa4": ("0.1.0.dev23",),
        "28d0d15495a4a1fff992312ca913ac3336e43903249053a80ac0418d845efee0": ("0.1.0.dev24", "0.1.0.dev25",),
    },
}


def earlier_package_version(region: str, text: str) -> str | None:
    """Return the earlier package version that shipped this exact region text, if any."""

    digest = hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()
    versions = EARLIER_PACKAGED_REGIONS.get(region, {}).get(digest)
    if not versions:
        return None
    if len(versions) == 1:
        return versions[0]
    return f"{versions[0]} to {versions[-1]}"

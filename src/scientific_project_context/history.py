"""Recognize text that an earlier package version shipped in a tracked region.

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
EARLIER_PACKAGED_REGIONS: dict[str, dict[str, tuple[str, ...]]] = {
    "description:spctx-literature": {
        "2a64f64bb39d05a516f2b9c4ec106c63d5dbd9800775a98f5393d0c39b447dae": ("0.1.0.dev26",),
    },
    "description:spctx-project-context": {
        "f9bdfc64c9e2c7b90da0571e2b37a3ac680fc6286b4cf48ada0c148fb3a914f7": ("0.1.0.dev22", "0.1.0.dev23", "0.1.0.dev24",),
        "a96a93e4821b989509fdce533aaf4e4224015cecde0b4b6b3f3d1178fac37ffe": ("0.1.0.dev25", "0.1.0.dev26",),
    },
    "description:spctx-public-writing": {
        "84e39206a57b2a2295cfd13320795a55e65fe593ceb83b7e41c07d6920826b83": ("0.1.0.dev22", "0.1.0.dev23", "0.1.0.dev24", "0.1.0.dev25", "0.1.0.dev26",),
    },
    "description:spctx-scientific-change": {
        "4a14817e4634dd8f0303163d7030b97b825f1dfe69140f14f63a3201094310b8": ("0.1.0.dev22", "0.1.0.dev23", "0.1.0.dev24", "0.1.0.dev25",),
        "27a1f37b4f046728de17ea596e10209f4ddcb68204b26066da1828647ea55c9e": ("0.1.0.dev26",),
    },
    "practice_core": {
        "d5618875b4ffe7d4363f2064fc202bc56c5ea5d48a84bcb537104f02a4a28659": ("0.1.0.dev22",),
        "5c3b8e2aae495850c9fe34f994956121f58872694bb9ab0424d57dce6adbc92f": ("0.1.0.dev23",),
        "3815e94784f58ea0087823854f082378d175706fb00ea0cfaac704b202fa9ab8": ("0.1.0.dev24", "0.1.0.dev25",),
        "8d01930fb723ccd4526ee839ede4cd20e07cb4e34e5b9019e208893928eb0ff1": ("0.1.0.dev26",),
    },
    "routing": {
        "5dad873957e4ee305ec73b5ce46c2154c514bd7b68ac2cea2d6d911ca0440aa5": ("0.1.0.dev22",),
        "ee28b1495f7201b3f8e85c0743e7200a79b8c363ac730192cf8827d8fbf20b0f": ("0.1.0.dev23",),
        "2d3c8944c7769ae870452c3e74d6f5bf3d3235c8a8971044575cc4ed0bb430e7": ("0.1.0.dev24", "0.1.0.dev25",),
        "2b608d27bcab38a39c3cfec774d5902a07d0bfb6ab8154cdda7cadf15bd9c4c0": ("0.1.0.dev26",),
    },
    "skill:spctx-literature": {
        "ec93c0123028578c68d54d3439f9184fa89b3a28f155a0c31c1aa4b2fd78b0e6": ("0.1.0.dev26",),
    },
    "skill:spctx-project-context": {
        "adea19f4a969f9cba89bfe1715e041244570fafc233f858ca3dba72f150c9f64": ("0.1.0.dev22",),
        "91e8fdbf106fd6088b0547c68be246e64c86cef0e3d5452c32c1548d2ddfc744": ("0.1.0.dev23",),
        "46ee40a58fa19ed6b343406bfd5eb73b3c0c71d89f5798748958329c381b6a20": ("0.1.0.dev24",),
        "401ebb9114502a87ad3199e3fc21c038e8547fb2ebfdbbb699fa0cbbee1dfbc4": ("0.1.0.dev25",),
        "47380a136e86df398c91b27c4b463e14d54f343fa23486755dd2ff91de80d467": ("0.1.0.dev26",),
    },
    "skill:spctx-public-writing": {
        "2b82465e761e66b3d1973b2cf09405256729129bf11014d4bee5eb834cb2d00d": ("0.1.0.dev22",),
        "06b553f374a90669d0df5e7a8a83a0e6a31bc031eeff3daa46d9db2f958f5458": ("0.1.0.dev23",),
        "85eb3ac9a3d07b84df810a5b3c5b8f5e2e20d227cb40e4608f73ec5c674b9a4c": ("0.1.0.dev24", "0.1.0.dev25",),
        "b9ff927c22a277ce71482deb8ae222898ab50dcba317d9a16b022adbbdf0de35": ("0.1.0.dev26",),
    },
    "skill:spctx-scientific-change": {
        "44cd1dfc23c648e6498aa9a240075a222d2333b4306acbadcebecb6597e05a78": ("0.1.0.dev22",),
        "31491c5caad8b56cd630393d3f0c4fdaa89606227e0721698295af2c3f401aa4": ("0.1.0.dev23",),
        "28d0d15495a4a1fff992312ca913ac3336e43903249053a80ac0418d845efee0": ("0.1.0.dev24", "0.1.0.dev25",),
        "5ba013947131e676962d38375e2441196d28cff96c62c7545708c5190d0727f0": ("0.1.0.dev26",),
    },
}


def region_digest(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def earlier_package_version(region: str, text: str) -> str | None:
    """Return the earlier package version that shipped this exact region text, if any."""

    versions = EARLIER_PACKAGED_REGIONS.get(region, {}).get(region_digest(text))
    if not versions:
        return None
    if len(versions) == 1:
        return versions[0]
    return f"{versions[0]} to {versions[-1]}"

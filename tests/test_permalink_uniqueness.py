"""Falsifier for the directed-ener-98f417 subtopic-index permalink collision cure.

Before the cure, 72 level-3 ``*_index.md`` files across 12 subtopic families
shared 12 truncated permalinks (six claimants each), so only one document per
family was reachable at its URL and five were shadowed. The cure keeps the
live winner at each shared route and gives every shadowed index a unique
``-<slugified index title>`` suffixed permalink (hex fragment fallback when
two cured titles slugify alike).
"""
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
PERMALINK = re.compile(r"^permalink:\s*[\"']?([^\s\"'#]+)[\"']?\s*$", re.M)


def page_permalinks():
    out = {}
    for p in PAGES.glob("*.md"):
        m = FRONT_MATTER.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        pm = PERMALINK.search(m.group(1))
        if pm:
            out[p.name] = pm.group(1)
    return out


FAMILIES = [
    "cost-per-shot", "defensive-lay", "dragonfire-uk", "friendly-elec",
    "helios-lasers", "laser-atmosph", "laser-precisi", "lasers-vs-mic",
    "leonidas-anti", "microwave-dro", "power-cooling", "thor-microwav",
]
SHARED_SLUGS = {f"/directed-ener-98f417-{f}/" for f in FAMILIES}

EXPECTED_CURED = {
    "/directed-ener-98f417-cost-per-shot-shot-cost/",
    "/directed-ener-98f417-thor-microwav-thor/",
    "/directed-ener-98f417-helios-lasers-helios/",
    "/directed-ener-98f417-dragonfire-uk-drone-defence/",
    "/directed-ener-98f417-leonidas-anti-49-drone-test/",
}


class TestPermalinkUniqueness(unittest.TestCase):
    def test_all_permalinks_unique(self):
        pls = page_permalinks()
        counts = Counter(pls.values())
        dups = {k: v for k, v in counts.items() if v > 1}
        owners = {k: sorted(n for n, v in pls.items() if v == k) for k in dups}
        self.assertEqual({}, owners)

    def test_shared_family_slugs_claimed_by_one_document(self):
        pls = page_permalinks()
        for slug in SHARED_SLUGS:
            owners = sorted(n for n, v in pls.items() if v == slug)
            self.assertEqual(1, len(owners), f"{slug} claimed by {owners}")

    def test_expected_cured_index_routes_exist(self):
        pls = set(page_permalinks().values())
        self.assertEqual(set(), EXPECTED_CURED - pls)

    def test_family_slug_used_only_in_permalinks(self):
        # The cured family slugs must not appear as link targets inside any
        # body (nothing should reference an index route it cannot name).
        bad = []
        for p in PAGES.glob("*.md"):
            t = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"directed-ener-98f417-[a-z0-9-]*/", t):
                line = t[: m.start()].count("\n")
                ctx = t.splitlines()[line]
                if "permalink:" not in ctx:
                    bad.append((p.name, m.group(0), ctx.strip()[:60]))
        self.assertEqual([], bad)

    def test_index_bodies_link_only_existing_routes(self):
        existing = set(page_permalinks().values())
        dangling = []
        for p in PAGES.glob("*_index.md"):
            for m in re.finditer(r"\{\{\s*'(/[^']*?)'\s*\|\s*relative_url", p.read_text(encoding="utf-8", errors="replace")):
                if m.group(1) not in existing:
                    dangling.append((p.name, m.group(1)))
        self.assertEqual([], dangling)


if __name__ == "__main__":
    unittest.main()

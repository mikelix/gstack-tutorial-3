# -*- coding: utf-8 -*-
"""Generate the gstack Tutorial No.3 decks (EN + ZH) from one content list.

Usage:  python _build/build_deck.py
Output: dist/gstack-tutorial-3_EN.pptx
        dist/gstack-tutorial-3_ZH.pptx

Both editions come from _build/deck_content.py, so they cannot drift apart
in structure — a deliberate improvement over Tutorial #2, which kept two
parallel 26KB build scripts that had to be kept identical by hand.
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor

sys.path.insert(0, str(Path(__file__).parent))
import mck
from deck_content import SLIDES, pick

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

ACCENT_MAP = {"GOOD": mck.GOOD, "BAD": mck.BAD, "NAVY": mck.NAVY}


def build(lang: str) -> Path:
    prs = Presentation()
    prs.slide_width = mck.W
    prs.slide_height = mck.H

    page = 0
    for kind, raw in SLIDES:
        d = {k: pick(v, lang) for k, v in raw.items()}
        if kind == "cover":
            mck.slide_cover(prs, d["kicker"], d["title"], d["subtitle"], d["meta"])
            continue  # cover carries no page number

        page += 1
        if kind == "divider":
            mck.slide_divider(prs, d["num"], d["title"], d["blurb"], page)
        elif kind == "bullets":
            mck.slide_bullets(prs, d["title"], d["bullets"], page,
                              kicker=d.get("kicker"), source=d.get("source"),
                              lead=d.get("lead"))
        elif kind == "table":
            mck.slide_table(prs, d["title"], d["headers"], d["rows"], page,
                            kicker=d.get("kicker"), source=d.get("source"),
                            widths=d.get("widths"),
                            emphasis_col=d.get("emphasis_col"),
                            lead=d.get("lead"))
        elif kind == "flow":
            mck.slide_flow(prs, d["title"], d["steps"], page,
                           kicker=d.get("kicker"), source=d.get("source"),
                           note=d.get("note"))
        elif kind == "two_col":
            left = (d["left"][0], d["left"][1], ACCENT_MAP[d["left"][2]])
            right = (d["right"][0], d["right"][1], ACCENT_MAP[d["right"][2]])
            mck.slide_two_col(prs, d["title"], left, right, page,
                              kicker=d.get("kicker"), source=d.get("source"))
        elif kind == "code":
            mck.slide_code(prs, d["title"], d["lines"], page,
                           kicker=d.get("kicker"), source=d.get("source"),
                           note=d.get("note"))
        elif kind == "bignum":
            mck.slide_big_number(prs, d["title"], d["stats"], page,
                                 kicker=d.get("kicker"), source=d.get("source"),
                                 note=d.get("note"))
        elif kind == "quote":
            mck.slide_quote(prs, d["quote"], d["attrib"], page,
                            kicker=d.get("kicker"))
        else:
            raise ValueError(f"unknown slide kind: {kind}")

    DIST.mkdir(exist_ok=True)
    out = DIST / f"gstack-tutorial-3_{lang.upper()}.pptx"
    prs.save(str(out))
    return out


if __name__ == "__main__":
    for lang in ("en", "zh"):
        p = build(lang)
        print(f"  wrote {p.relative_to(ROOT)}  ({len(SLIDES)} slides)")

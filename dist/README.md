# dist/ — generated deliverables

**Do not hand-edit anything in this folder.** Every file here is regenerated
from the sources; the moment someone "just fixes a typo in the .docx", the
next rebuild silently reverts it and nobody notices for a week. If a fix is
needed, fix the source and rebuild.

| File | Source |
|---|---|
| `gstack-tutorial-3_EN.pptx` | `_build/deck_content.py` via `_build/build_deck.py` |
| `gstack-tutorial-3_ZH.pptx` | same file, `zh` branch |
| `gstack-tutorial-3_EN.docx` | `_build/doc_content.py` via `_build/build_docx.py` |
| `gstack-tutorial-3_ZH.docx` | same file, `zh` branch |

`TUTORIAL.md` / `TUTORIAL.zh.md` in the repo root remain the canonical
long-form tutorial. The deck and the Word document are presentation and
briefing formats of the same material, not separate sources of truth.

## Rebuild

```bash
python _build/build_deck.py     # -> both .pptx
python _build/build_docx.py     # -> both .docx
python _build/verify_docx.py    # MANDATORY before handing off
```

## Why EN and ZH cannot drift

Both editions are generated from a single content structure in which every
string is an `L(en, zh)` pair. There is no parallel English file and Chinese
file to keep in sync by hand — a deliberate change from gstack Tutorial #2,
whose `PLAYBOOK.md` §3.1 flagged its two 26KB parallel build scripts as
needing to "stay slide-for-slide identical" by discipline alone.

## Verification

`_build/verify_docx.py` implements the mandatory 3-part check from
`MCKINSEY_DOCX_PLAYBOOK.docx` §5, plus a CJK font check:

1. Body structure — last child is `w:sectPr`, zero stray `w:r` at body level
2. No duplicate consecutive text runs
3. ZIP integrity and content types
4. `eastAsia` font set on **every** run (§6) — 283/283 at last build

A file can be a perfectly valid ZIP with well-formed XML and still be broken
in ways only structure inspection catches. Run the verifier before opening
anything in Word, every time.

## Style

Both formats follow `MCKINSEY_DOCX_PLAYBOOK.docx`: navy `#1F4E78` primary,
body `#000000`, caption `#595959`, muted `#808080`, fill `#F2F2F2`; Calibri
body, Consolas for code, Microsoft YaHei for Chinese.

The deck adds one convention the playbook does not cover because it is
document-only: **action titles**. Every content slide's title is a sentence
carrying the takeaway, not a topic label. Read the titles alone and you get
the whole argument — the single convention that most separates a consulting
deck from a corporate one.

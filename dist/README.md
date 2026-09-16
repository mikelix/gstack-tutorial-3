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

## Type scale and the autofit bug (read before touching `mck.py`)

The deck's type scale was raised from an original 21pt title / 14pt body to
a 30pt-minimum-for-prose floor after the project owner hand-tested the first
version and found it too small to present. Getting there exposed a real
python-pptx bug worth understanding before changing any layout code:

**New textboxes default to `spAutoFit`** — PowerPoint independently resizes
the *shape* to fit its real text content, regardless of the height passed to
`add_textbox()`. Every element in this file is positioned from an estimated
height computed in Python; if PowerPoint's real rendered height differs from
that estimate, the mismatch used to show up as silently overlapping text or
a dead gap, one layer removed from the actual bug. `mck.textbox()` now sets
`tf.auto_size = MSO_AUTO_SIZE.NONE` on every textbox for exactly this
reason — do not remove it.

With autofit disabled, the box is authoritative, so an imperfect height
*estimate* only wastes a little whitespace instead of causing an overlap —
but the character-width model behind those estimates (`_line_capacity` /
`_wrapped_lines`) is a hand-calibrated approximation, not real font
metrics, and it has been wrong in both directions on different content.
Two defenses are layered on top of it:

1. **Auto-fit with a safety margin.** `slide_bullets` and `slide_two_col`
   try font sizes from target down to floor and require the *estimated*
   height to clear the available space by 15% before accepting a size —
   because the estimate has repeatedly landed a few percent short of
   PowerPoint's real rendered height.
2. **A build-time `WARN` line** whenever content lands below its target
   size. This is a prompt to shorten the content or restructure it (see the
   two "bullets → table" conversions in `deck_content.py`'s history — a list
   of "term: explanation" pairs fits a table's row-based layout far more
   reliably than free-flowing bullet text), not something to silence by
   loosening the margin further.

**If you see an overflow that WARN didn't catch or a fix didn't resolve**,
don't hand-tune the margin blind — write a small script that imports `mck`
and the real slide-building function, calls it against a live
`Presentation()`, and prints the actual computed `body_y`/`avail_in`/predicted
height for that specific slide (see git history around the two_col and
bullets overflow fixes for the exact pattern). Hand-deriving these numbers
from the constants repeatedly produced wrong answers in this file's own
history — call the real code and print the real numbers instead.

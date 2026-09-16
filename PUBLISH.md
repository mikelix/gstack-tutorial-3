# Publishing this repository to GitHub

## Status: PUBLISHED

| Item | Value |
|---|---|
| Repo | <https://github.com/mikelix/gstack-tutorial-3> |
| Visibility | public |
| Branch | `main` |
| Commit at publish | `c1b7f30` — 13 commits, full local history preserved |
| CI | `repo self-check` green on first push — [run 35044324091](https://github.com/mikelix/gstack-tutorial-3/actions/runs/35044324091) |
| Licence | prose CC BY 4.0 · code Apache-2.0 · `Copyright 2026 Prof. Yi-Kuen Lee` |
| Topics | `gstack` `ai-agents` `tutorial` `video-captioning` `translation` `videocaptioner` `chinese` |

---

## How it was published (for the record)

Unlike tutorial #2's `PUBLISH.md`, no proxy or auth friction this time —
`gh` was already authenticated as `mikelix` from earlier work in this
session.

```bash
gh repo create gstack-tutorial-3 --public --source=. --remote=origin \
    --description "gstack Tutorial No. 3 -- English to Chinese video captioning with videocaptioner, verified by a 5-gate chain"
git push -u origin main
```

`gh repo create` with `--source` and `--remote` does **not** push by
itself unless `--push` is also passed — the repo was created (empty,
`size: 0`) and the push had to be run as a separate explicit step. Worth
remembering for tutorial #4: pass `--push`, or don't assume `--source`
alone did it.

CI (`repo self-check`, `.github/workflows/selfcheck.yml`) ran automatically
on push and passed in 11 seconds — the 100-check `selfcheck.py` plus the
gate-script exit-code assertion, both already proven locally before this
push, so a first-try green run was expected, not lucky.

---

## What shipped

All five audit-trail reviews, the bilingual `TUTORIAL.md`/`.zh.md`,
`docs/expertise_division{,.zh}.md`, `docs/choosing_a_translator{,.zh}.md`,
the verified gate-chain script (`starter/scripts/run_gates.py`), and the
bilingual `.pptx`/`.docx` deliverables in `dist/` — all built from source,
none hand-edited into the shipped state. See `reviews/05-ship.md` for the
full release audit and stated known gaps.

**One correction landed right before this push, worth recording:** the
author caught a wrong Chinese-character rendering of his own name
(`李奕锟` instead of `李贻昆`) in the ZH deck and Word document, and had
initially fixed it by hand-editing the shipped `dist/` files directly.
Per this repo's own "never hand-edit generated files" rule
(`dist/README.md`), the fix was ported to `_build/deck_content.py` and
`_build/doc_content.py` instead and both formats rebuilt from source —
catching, as a side effect, that the hand-edited `.docx` had regressed the
`eastAsia`-on-every-run CJK font guarantee (526/880 vs. the generator's
283/283), which `verify_docx.py` caught before anything shipped with that
regression in it.

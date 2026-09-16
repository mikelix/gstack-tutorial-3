# Review 05 — Ship (`/ship`)

```
Date:            2026-09-16
Reviewer role:   DevOps
Command:         /ship
Scope reviewed:  release contents, bilingual parity, licence, limitation disclosure
Verdict:         REVISE → PASS after two blocking issues fixed in this pass
```

---

## Release contents

| Item | Present | Notes |
|---|---|---|
| `PLAN.md` | ✅ | scope, gate chain, ranked risks, Definition of Done |
| `TUTORIAL.md` + `.zh.md` | ✅ | parity checked below |
| `docs/expertise_division{,.zh}.md` | ✅ (zh added this pass) | see B8 |
| `docs/choosing_a_translator{,.zh}.md` | ✅ (zh added this pass) | see B8 |
| `docs/deck_market_benchmark.md` | ✅, English only, deliberately | see Decisions H2 |
| `starter/INSTALL.md` | ✅ | Windows primary, macOS/Linux secondary |
| `starter/scripts/run_gates.py` | ✅ | Gates T1-T4 + T3b + VOID guard, verified against real pilot artifacts |
| `starter/versions.lock.template` | ✅ | |
| `reviews/01`-`04` | ✅ | full audit trail, written at the time |
| `dist/` — `.pptx` × 2, `.docx` × 2 | ✅ | 31 slides, 15/17 pages; verified via `_build/verify_docx.py` |
| `LICENSE.md` | ✅ (added this pass) | see B9 |
| `.github/scripts/selfcheck.py` + CI workflow | ✅ | 97 checks |

---

## Bilingual parity check

| Check | Result |
|---|---|
| `TUTORIAL.md` vs `.zh.md` section counts | equal (13 H2, 23 H3, 36 checkboxes) |
| Every internal markdown link resolves | ✅ (37+ links, `selfcheck.py` §2) |
| `docs/` reader-facing pages have a `.zh.md` counterpart | ✅ **after fix — see B8** |
| `dist/` deck and docx both shipped in both languages | ✅ |
| Gate names (T1-T5, T3b) identical across languages | ✅ |

**Parity rule adopted, same as tutorial #2:** a change that lands in one
language and not the other fails the release, **for reader-facing content.**
`docs/deck_market_benchmark.md` is scoped out of this rule deliberately — see
Decisions H2 below — because it is not reader-facing teaching material.

---

## Licence review

| Component | Licence | Clear to redistribute? |
|---|---|---|
| Tutorial prose (`TUTORIAL.md`, `.zh.md`, `docs/`, `README.md`) | CC BY 4.0 | ✅ |
| Scripts (`_build/`, `starter/scripts/`) | Apache-2.0 | ✅ |
| `videocaptioner` | GPL-3.0, upstream | ✅ — not vendored; installed via `pip` |
| FFmpeg | LGPL/GPL depending on build | ✅ — not vendored |
| Pilot source video clips | n/a | ✅ — never committed (`.gitignore`); no redistribution question exists |

---

## Limitation disclosure (for the release notes)

**In this release**
- Gates T1-T4 + T3b: mechanical, verified against real pilot artifacts, all
  four exit codes (PASS/FAIL/VOID/environment-error) confirmed distinct
- Gate T5: a named, followable procedure with a floor-and-scale sampling
  rule — not automated, stated as such
- Bilingual tutorial, install guide, and both domain-reference docs
- Bilingual `.pptx` (31 slides) and `.docx` (15/17 pp.), McKinsey house style,
  verified structurally (`verify_docx.py`) and visually (PowerPoint/Word COM
  rendering, not just XML inspection)

**Known, stated gaps (not silent)**
- Gate T5's long-clip sampling caps at 40 segments (~0.8% coverage on a
  5,000-segment hypothetical clip) — a property of sampling, not a defect,
  stated in `docs/expertise_division{,.zh}.md` §4
- Bing translator observed broken and Google observed to silently pass
  through English, both on one date/network/version — readers are told to
  re-verify, not trust the table as permanent
- macOS/Linux install paths are documented but not independently tested to
  the depth Windows was
- `docs/deck_market_benchmark.md` is English-only, by design (see H2)
- No GitHub repository exists yet for this project — see "Not shipped" below

**Positioning**
This is a content-production workflow tutorial, not a linguistics or ASR
research project. The falsifiable claim (`PLAN.md` §1): a reader with no
prior `videocaptioner` experience can go from a raw clip to a verified
captioned output in one sitting, using the 5-gate chain as evidence.

---

## Blocking issues found and fixed in this pass

**B8 — `TUTORIAL.zh.md` linked to English-only reference docs.**
`docs/expertise_division.md` and `docs/choosing_a_translator.md` — both
directly linked from `TUTORIAL.zh.md` as required reading before Phase 2 and
Phase 4 — had no Chinese counterpart. A Chinese-reading student following the
Chinese tutorial would hit an English-only page at the two most
access-sensitive points in the whole project (translator choice, and the one
non-mechanical gate). *Fixed by:* full translations
(`docs/expertise_division.zh.md`, `docs/choosing_a_translator.zh.md`),
`TUTORIAL.zh.md`'s five internal links repointed at them, both files added to
`selfcheck.py`'s required-file list.

**B9 — Every document's footer claimed "CC BY 4.0 / Apache-2.0 — Copyright
2026 Prof. Yi-Kuen Lee" and no `LICENSE.md` existed to back the claim.**
An unbacked licence claim is a defect for a repository, not a style nit —
same severity class as tutorial #2's B7 (stale documentation). *Fixed by:*
`LICENSE.md`, added to `selfcheck.py`'s required-file list.

Both were found by checking against tutorial #2's actual shipped structure
(`Glob docs/*.zh.md`, `Glob LICENSE*`) rather than assuming this repo already
matched it — the same discipline that caught B7 in tutorial #2's own ship
review.

---

## Non-blocking notes

- `dist/` binaries are committed (convenience) and regenerable from `_build/`
  (integrity) — same H1 decision as tutorial #2, same reasoning.
- `docs/deck_market_benchmark.md` is a legitimate example of "some content
  belongs in the repo but not in the reader-facing bilingual surface" — worth
  keeping as a documented exception (H2) rather than either force-translating
  a business memo or silently excluding it from the parity rule.
- `reviews/03-eng-review.md`'s E2 open item (Gate T5 sampling scale) was
  closed in the previous session pass, before this ship review started —
  confirmed still applied correctly during this review, not just claimed.

---

## Decisions recorded

| # | Decision |
|---|---|
| H1 | `dist/` is committed (convenience) **and** regenerable (integrity). Both, not either — same as tutorial #2. |
| H2 | The bilingual-parity rule applies to reader-facing teaching content only. `docs/deck_market_benchmark.md` (an internal business-research memo, not teaching material) is a stated, deliberate exception — not a silent gap. |
| H3 | Every release restates the limitation table. Silence about limits reads as a claim. |
| H4 | Repo self-check runs on every push (`.github/workflows/selfcheck.yml`), now 97 checks. |
| H5 | This ship review itself must check against tutorial #2's actual shipped structure, not just this repo's own prior state — that is how B8 and B9 were found. |

---

## What was NOT reviewed

- Independent macOS/Linux run of the full pipeline (stated gap, not hidden).
- A second, independent Gate T5 review by someone other than this project's
  own author — the fidelity review recorded in the pilot session was
  informal, not a formal `04-qa-report.md`-style record for a full clip.
- Whether `docs/deck_market_benchmark.md`'s market-rate figures still hold —
  it is dated 2026-09-16 and says so; re-verification is the reader's to do,
  same discipline as the translator-availability table.

---

## Not shipped (explicit, not silent)

**No GitHub repository has been created for `gstack-tutorial-3`.** Everything
in this review describes the local repository's state on `main`
(commit history: `28ad907` … through this commit). Publishing — creating the
repo under `mikelix`, pushing, and drafting a release — is a separate,
explicit action requiring the project owner's go-ahead before it happens, not
a default step of `/ship`. Tutorial #2's own `PUBLISH.md` documents the
actual publish sequence (`gh repo create ... --public`, then a proxy-clearing
push workaround) to follow when that go-ahead is given.

---

## Addendum

**2026-09-16, same day — after publishing.** The owner gave the explicit
go-ahead; see `PUBLISH.md` for the full publish record
(<https://github.com/mikelix/gstack-tutorial-3>, `v1.0` released, CI green).
Two follow-ups landed after the initial publish, both audited here rather
than silently folded in:

**Post-publish fix — wrong Chinese name.** The author's name rendered as
`李奕锟` instead of the correct `李贻昆` in the ZH deck and Word document.
The author caught it and initially hand-corrected the shipped `dist/` files
directly; per this repo's own "fix the source, not the output" rule
(`dist/README.md`), the correction was ported to `_build/deck_content.py`
and `_build/doc_content.py` and both formats rebuilt — which also caught
that the hand-edited `.docx` had regressed the `eastAsia`-on-every-run CJK
guarantee (526/880 vs. the generator's clean 283/283). Two of three PPTX
edits the author made by hand were also reconciled against source rather
than assumed: one ("wrong artifact" → "wrong output") was a legitimate,
low-risk wording change and was ported; the other (an executive-summary
title edit that broke grammar — "is Actual skill", missing "the") was
flagged back to the author rather than guessed at, and was not ported.

**Post-publish addition — a rights-clear sample clip (`starter/sample/`).**
The owner's suggestion — ship a short worked example so a reader can see a
real result immediately — was good, but the obvious source (the pilot's own
downloaded interview clip) is not the author's to redistribute: no creator
metadata, and a baked-in caption style typical of third-party recording
software, confirmed during the pilot itself
(`docs/choosing_a_translator.md`'s own pilot notes). Publishing even a
10-second excerpt into this public, CC-BY-licensed repo would have been a
real rights problem, not a hypothetical one, so this was raised explicitly
rather than executed on request — the owner chose a synthetic clip
(generated visual + offline TTS narration, zero rights ambiguity) over the
alternative of shipping the real footage anyway. `starter/sample/README.md`
documents exactly how it was built, reproducibly. The clip was run through
the *actual* documented pipeline (not faked): Gates T1-T4 all PASS, one real
ASR error was hand-corrected ("gestack" → "gstack") exactly as the tutorial
teaches, and Gate T5 was checked by eye (natural, faithful, no
hallucination) before committing it. `reviews/02-spec.md` S1 records this as
a partial supersession, not a silent scope change.

**Post-publish addition — explicit educational-use notice.** The owner asked
for a standing notice, in the key reader-facing documents, that this project
is for educational purposes and grants no rights to third-party footage —
the same caution already applied case-by-case to the sample clip above,
made explicit and permanent rather than left implicit. Added: a new
"Educational use" section in `LICENSE.md`; a status-line notice in
`README.md`; and a matching blockquote near the top of `TUTORIAL.md` and
`TUTORIAL.zh.md` (parity preserved — both are blockquotes, not headers, so
`selfcheck.py`'s H2/H3 parity counts are unaffected). `selfcheck.py`
re-run clean at 113/113 after the change.

**Post-publish addition — `PLAYBOOK.md` for tutorial #4.** The owner asked
for a summary of how this tutorial was actually built, for the next gstack
tutorial project. Modeled on `gstack-tutorial-2/PLAYBOOK.md` (the document
this repo's own `PLAN.md` cites as its own starting point) but written from
what actually happened here rather than restating the predecessor: the
lighter one-domain-agent topology and why (`reviews/01-ceo-review.md`'s S0
question), the `L(en, zh)` single-content-source pattern as a real
improvement over tutorial #2's two-hand-synced-build-scripts approach, the
Gate T3b passthrough-detection lesson generalized beyond this project, and a
13-entry pitfall ledger covering every real defect found this session (the
`spAutoFit` bug, PowerShell/CRT quoting on both Python and git argv, the
hand-edit that regressed the CJK guarantee, and the sample-clip rights
decision). Added to `selfcheck.py`'s required-file list and referenced from
`README.md`'s layout table. `selfcheck.py` re-run clean at 115/115.

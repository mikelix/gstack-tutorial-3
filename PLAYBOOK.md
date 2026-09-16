# PLAYBOOK — how gstack-tutorial-3 was actually built

> **Audience:** whoever authors gstack Tutorial No. 4.
> **What this is:** the worked process behind `gstack-tutorial-3`, written down
> while it is still fresh, in the order the work was actually done — including
> the post-publish corrections, because those are where the real lessons live.
> **What it is not:** a template to fill in. The content changes; the
> *sequence* and the *invariants* do not.
> **Predecessor:** [`gstack-tutorial-2/PLAYBOOK.md`](https://github.com/mikelix/gstack-tutorial-2/blob/main/PLAYBOOK.md)
> — this repo followed its §6 "Adapting this to Tutorial No. 3" almost
> exactly. Where this playbook repeats that one, it's because the invariant
> held. Where it diverges, that divergence is the lesson.

| | |
|---|---|
| Repo | <https://github.com/mikelix/gstack-tutorial-3> |
| Subject | English → 简体中文 video captioning with `videocaptioner` |
| Team | 5 gstack roles × **1** domain agent (down from tutorial #2's 2 — see §2) |
| Gate chain | T1–T4 mechanical + **T3b** (added mid-project, see §4) + T5 (never automated) |
| Deliverables | `TUTORIAL.md`+`.zh.md` (source of truth) → `.docx` ×2 → `.pptx` ×2 (31 slides), McKinsey house style |
| CI | `repo self-check` — 113 checks: required files, markdown links, EN/ZH parity, gate-script contract, BOM-safe reads, generated-not-hand-made |
| Post-publish | 3 follow-up commits: a real Chinese-name fix, a rights-clear sample clip, an educational-use notice — all audited in `reviews/05-ship.md`'s Addendum, none silent |

---

## 0. The one invariant (unchanged from tutorial #2)

```
                ┌─────────────────────────────┐
   you edit ──► │  _build/*_content.py        │  ◄── the ONLY source of truth
                └──────────┬──────────────────┘
                           │  _build/
          ┌────────────────┼──────────────────┐
          ▼                ▼                  ▼
   build_docx.py     build_deck.py       TUTORIAL.md / .zh.md
   (.docx ×2)        (.pptx ×2)          (hand-written, separate source)
```

**Never hand-edit anything in `dist/`.** This got tested for real, not
hypothetically — see §5 "The hand-edit that almost shipped a regression."

```bash
py _build/build_docx.py     # -> dist/gstack-tutorial-3_{EN,ZH}.docx
py _build/build_deck.py     # -> dist/gstack-tutorial-3_{EN,ZH}.pptx
py .github/scripts/selfcheck.py
```

**One improvement over tutorial #2, worth carrying forward:** tutorial #2
kept two parallel ~26KB build scripts (`build_en.py`, `build_zh.py`) that had
to be hand-kept-identical. Tutorial #3 used a single content module per
format (`_build/deck_content.py`, `_build/doc_content.py`) where every string
is an `L(en, zh)` tuple, and **one** builder loop produces both languages:

```python
class L(tuple):
    def __new__(cls, en, zh): return super().__new__(cls, (en, zh))

def pick(v, lang):
    return v[0 if lang == "en" else 1] if isinstance(v, L) else v

for lang in ("en", "zh"):
    build(lang)
```

This makes EN/ZH structural drift **impossible**, not just checked — a
stronger guarantee than tutorial #2's CI parity check, at no extra cost.
Do this from day one on tutorial #4; retrofitting it later means rewriting
every slide/paragraph call site.

---

## 1. The ten steps, in order (same shape as tutorial #2 §1)

### S0 — Frame it with the AI CEO, and size the topology honestly

`reviews/01-ceo-review.md` had to answer the same three questions tutorial #2
did, plus one this project added: **does a lighter subject justify a lighter
team?** Tutorial #2 needed two domain agents (GDS physics + analog IC
architecture) because two genuinely separate expertises were both load-
bearing. Tutorial #3's subject — captioning — has exactly one place where
mechanical verification runs out: translation fidelity. So it got **one**
domain agent (Bilingual Caption QA Specialist), not two by default and not
zero by false economy. Answer this honestly at S0; don't copy the
predecessor's topology unexamined.

### S1 — Decompose with the AI PM

Same discipline as tutorial #2: escalate anything whose *verdict* needs
domain judgment (here: translation fidelity, register, and the sampling
rule for how much of a long transcript a human actually needs to read) by
name to the domain agent, never resolve it in the PM's own voice.

### S2 — Lock the toolchain, but expect it to be less stable than silicon tools

Tutorial #2 pinned three tool versions and never had to touch them again.
Tutorial #3's dependency (free translation services) was **actively
unstable during authoring**: Bing's endpoint 404'd, and Google silently
returned unmodified English while exiting 0. Lesson for tutorial #4: if
your pipeline depends on any third-party free-tier service, budget time to
discover it lying to you, and design the gate chain assuming it will (§4).
`docs/choosing_a_translator.md` exists because "just use the default" is not
a safe instruction when the default can silently fail.

### S3 — Design the gate chain and its exit-code contract (kept identical)

```
T1  transcription produced, non-empty
T2  translator provenance — was the SERVICE YOU ASKED FOR the one that ran
T3  segment parity — same segment count/timestamps, source vs. target
T3b passthrough guard — did translation actually happen, or did it silently
    return the source language back at you (see §4 — this gate didn't
    exist at S3; it exists because of what happened at S7)
T4  ffprobe resolution/duration match, source vs. output video
T5  human/domain fidelity review — never automated, floor-and-scale sample
```

Same four-exit-code contract as tutorial #2 (`0` PASS / `1` FAIL / `2` VOID
/ `3` environment), same reason for VOID existing as its own state:
**"the gate passed" and "the gate was meaningless" must never print the
same thing.**

### S4 — Build the runnable skeleton

`starter/scripts/run_gates.py` is the evidence, same as tutorial #2's
`run_all.sh`. One difference worth naming: tutorial #2's circularity trap
was about *derivation* (don't verify a netlist against a reference derived
from the same GDS). Tutorial #3's version is about *tautology*: Gate T5's
domain-agent review must never be re-derived from the same LLM call that
produced the translation being reviewed — a second, independent read, by a
human or a genuinely separate agent invocation, or the review is theater.

### S5 — Write the tutorial body

Same structure: **Part 0 mental model → install → the five gstack phases →
verification → troubleshooting → appendices**, every part ends in a
Checkpoint with checkboxes. One addition made post-publish, worth doing at
S5 instead of retrofitting: **a "see it work before installing anything"
section** (§6 below) — readers should be able to run the gate chain against
a committed sample before they've installed a single dependency.

### S6 — Give the domain agent its own section (lighter, not absent)

Tutorial #2's Part 9 carried a ~20-phase analog workflow because the domain
genuinely had that much structure. Tutorial #3's domain reference doc
(`docs/expertise_division.md`) is proportionally shorter: a RACI table, the
defer clause, and **one concrete, load-bearing procedure** — the
floor-and-scale sampling rule for how many segments a human actually reads
on a long transcript:

```
sample_size = min(15 + 5 * max(0, (N - 100) // 200), 40)
```

15-segment floor, +5 segments per 200 beyond the first 100, capped at 40.
This is the whole point of S6: don't pad a light domain to look as heavy as
a hard one. A one-page procedure that's actually followed beats a twenty-
page section that isn't.

### S7 — Write the five reviews as you go, and let them catch real defects

The review that carried the most weight, same role as tutorial #2's VOID
discovery: `04-qa-report.md` found that the free Google translator returns
**unmodified English text and exits 0** — four of the five gates (T1, T3,
T4, and a naive T2) all report PASS on a completely untranslated video.
This single finding is why **Gate T3b exists** — a Han-character-ratio +
identity check that specifically catches "the translator ran and reported
success but did nothing." Design your gate chain assuming this class of
failure exists somewhere in your pipeline; it will.

### S8 — Build, then validate mechanically (see §5 for the sharp edges)

```bash
python .github/scripts/selfcheck.py     # 113 checks by ship time
```

Then check the binaries by opening them, not just by the XML passing
`py_compile`. §5 covers why this step alone is not enough for `.pptx`.

### S9 — Ship, then treat "shipped" as a state you keep, not a finish line

```
selfcheck → git add/commit → git push -u origin main → watch CI → gh release create
```

**`gh repo create --source=. --remote=origin` does NOT push.** It creates
the remote and wires it up; `git push -u origin main` is a separate,
required step. Tutorial #2 apparently didn't hit this; tutorial #3 did —
confirm with `git log` on the GitHub web UI after `repo create`, don't
assume.

The part tutorial #2's playbook doesn't cover, because tutorial #3 is where
it actually happened: **three legitimate post-publish commits landed after
"ship."** See §5. Budget for this. A published tutorial is not done the
moment CI goes green on the first push; it's done when the owner has
actually read the shipped artifact and found nothing wrong — which takes
longer than the build.

---

## 2. The authority contract (lighter version)

```
   gstack orchestration              one domain agent
   CEO · PM · Eng · QC · DevOps      Bilingual Caption QA Specialist
   ── process authority ──           ── translation-fidelity authority ──
                    └──────────► gate chain ◄──────────┘
                       (neutral referee: ffprobe / segment diff / Han-ratio)
                     on conflict, the domain agent wins on fidelity ONLY
```

Same defer clause pattern as tutorial #2, scoped to the one thing that's
actually qualitative here:

> CONSULT REQUIRED. Before asserting a translation is faithful, natural, or
> register-appropriate, hand the segment pair to the domain agent and quote
> the reply verbatim. Everything else (segment count, timestamps,
> resolution, translator provenance) is mechanically checkable — do not
> escalate what T1–T4/T3b can already answer.

**Lesson for tutorial #4:** don't copy a two-key contract's *ceremony* onto
a one-key subject. The contract should be exactly as wide as the qualitative
surface actually is — here, that's one gate (T5), not the whole pipeline.

---

## 3. Reusable machinery

### 3.1 `mck.py` — McKinsey-style slide primitives

Canvas 13.333 × 7.5 in. `slide_cover`, `slide_bullets`, `slide_table`,
`slide_code`, `slide_two_col`, `slide_flow`, `slide_quote`, `slide_bignum` —
same idea as tutorial #2's `deck.py`, restyled for a consulting-deck look
(navy `#1F4E78`, action-titles-as-takeaways, kicker/lead/body type scale).
**The one thing every future deck builder must know before writing a single
slide function: read §5.1 first.** It will save you the several hours it
cost here.

### 3.2 `deck_content.py` / `doc_content.py` — the `L()` bilingual pattern

Covered in §0. The one gotcha: run a Unicode-script scanner over the whole
content file before shipping. A single mistyped Cyrillic character
(`работы` typed where a Chinese word was intended, muscle-memory slip) sat
in the deck undetected by every structural check — `selfcheck.py` cannot
catch "wrong script, right position." Script it explicitly:

```python
import re
for text in all_strings:
    if re.search(r'[Ѐ-ӿͰ-Ͽ֐-׿가-힯]', text):
        flag(text)  # Cyrillic / Greek / Hebrew / Hangul in supposedly EN/ZH content
```

### 3.3 `.github/scripts/selfcheck.py`

Grew from tutorial #2's 29-check version to 113: required files, every
relative markdown link resolves, EN/ZH H2/H3/checkbox parity, gate-script
compiles + documents its own exit-code contract, no plain-`utf-8` reads
(BOM lesson, see §5.3), and — new this project — a "generated, not
hand-made" section that checks the *builder source*, not just the output:
does `build_deck.py` import the shared content module, does it loop both
languages, does every slide run set an `eastAsia` font attribute. **Check
the generator's properties, not just the artifact's** — an artifact-only
check can't tell a correctly-generated file from a correctly-hand-patched
one, and only one of those survives the next rebuild.

---

## 4. The T3b lesson, stated once, generally

Every gate chain eventually needs a gate that doesn't check "did the step
run and report success" but **"did the step actually do the thing it
claims, or did it silently no-op and report success anyway."** Tutorial #2
didn't need this (Magic/Netgen either match or don't — there's no silent
passthrough state for DRC). Tutorial #3 needed it because a free-tier
translator can return your own input back to you and exit 0. **Before
trusting any external tool/service's exit code as your source of truth,
ask: what does this tool's silent-no-op look like, and can I detect it
independent of the tool's own self-report?** If the answer is "I don't
know," that's your T3b, and you don't have it yet.

---

## 5. Pitfall ledger

Ordered roughly by how much time each one cost.

| # | Symptom | Cause | Fix |
|---|---|---|---|
| P1 | Slides had persistent, hard-to-diagnose text overlap no hand-calculation explained | `python-pptx`'s `add_textbox` **ignores the height you pass** — `spAutoFit` in the shape's `<a:bodyPr>` makes the shape self-resize to its real content regardless | Set `tf.auto_size = MSO_AUTO_SIZE.NONE` globally in your `textbox()` helper, on every textbox, from the first slide. Diagnosed only by dumping raw slide XML (`shape._element.xml`) after every hand-calculation failed — do that first next time, not last. |
| P2 | Bold titles/bullets reserved too much or too little space depending on direction | Text-width-estimation heuristic used one character-width factor for both bold and regular weight | Calibrate separate factors per weight (and per script — CJK, mono) from *real measured* wrapped output, not from font-metrics tables. Write a script that builds a live `Presentation()`, reads the actual rendered line count, and compares to your predicted count — iterate the constant until they agree. |
| P3 | A code panel's computed height was short by a consistent, per-line amount | Height formula didn't include `space_after` (the 4pt-per-line gap actually applied when writing each line) | Any "estimate block height from N lines × line height" formula must include every per-paragraph spacing property the write path actually applies, not just font size × line count. |
| P4 | `two_col` slides had zero auto-fit while every other slide type had it | Auto-fit margining was added type-by-type as bugs were found in each; this one type was never independently tested | When you add a shared behavior (auto-fit, a safety margin, a font floor) to N slide-type functions, grep for the function names to confirm all N actually got it — don't assume "I did this to the deck" covered every code path. |
| P5 | Ordinary prose starting with "VOID has a distinct..." rendered in FAIL-red | A keyword-coloring regex matched `VOID`/`FAIL`/`PASS` as a bare substring | Require a separator (`—`, `:`, `=`) immediately after a status keyword before treating it as a status badge, not a word that happens to appear in a sentence. |
| P6 | After "fixing" one overflowing slide, several previously-fine slides got needlessly cramped | Overcorrected by lowering the global font floor and safety margin instead of fixing the one slide that actually overflowed | Fix the specific overflowing content (shorten it, or convert bullets → table) before touching a *global* constant. A global knob should be your last resort, not your first attempt. |
| P7 | PowerShell calls to a native `.exe` with a `"` or `\"font_size\":56` embedded silently stripped the quotes, producing garbage args | Windows CRT argv parsing plus PowerShell's own quoting both touch the string before the exe sees it | Backslash-escape embedded quotes **inside a single-quoted PowerShell string**: `'{\"font_size\":56}'`. Confirm with a `python -c "import sys;print(sys.argv)"` probe before trusting any quoting scheme, every time you're unsure. |
| P8 | `git commit -m $multilineMsg` failed with `pathspec '...' did not match any files` — the SAME quoting class as P7, on the git CLI instead of a Python one | Same underlying cause: PowerShell/CRT argv mangling of embedded quotes inside a variable passed to a native exe | Never pass a commit message with embedded quotes via `-m`. Write it to a file and use `git commit -F file.txt`, always, for any multi-line or quote-containing message. |
| P9 | A `git show HEAD:path` piped through PowerShell `Out-File`/`>` corrupted binary content | PowerShell redirection is text-mode by default and re-encodes the stream | For binary blobs, shell out through `cmd /c "git show HEAD:path > tempfile"`, which is byte-safe, instead of native PowerShell redirection. |
| P10 | `ffmpeg` errored "trying to apply an input option to an output file" | `-vf` was placed after *two* `-i` inputs (color source + audio), but `-vf` binds to the single video stream that precedes it | Build the video-only background first (`-vf` on the single color input), then mux audio in a **separate** command with `-c:v copy -c:a aac -shortest`. Don't try to filter and mux audio in one ffmpeg invocation with multiple inputs unless you're explicit about which input each option targets. |
| P11 | `git status` showed an unexplained modified `.pptx` and an untracked `.pdf` no documented step in this session should have produced | Earlier ad-hoc PowerPoint-COM automation (used to visually verify a slide) wrote its PDF export into `dist/` instead of scratch, and opening+closing the `.pptx` via COM triggered a silent resave | **Investigate every unexplained diff before staging — timestamps and `git log -1 --format=%cd` on the file usually pin the cause in under a minute.** When a discard action (`git checkout --`) is blocked by a safety classifier, prefer **regenerating the file from its documented source** (here: re-run `build_deck.py`) over forcing the discard — it's both safer and matches the project's own "never hand-fix `dist/`" rule. |
| P12 | Owner hand-corrected a wrong proper noun directly in the shipped `.docx`/`.pptx` | A generated-content bug (wrong Chinese name) was caught by the owner reading the *output*, not the source | Fixed by porting the correction into `_build/*_content.py` and rebuilding — never by keeping the hand-edit. Doing this **surfaced a second, worse bug**: the hand-edited `.docx` had silently regressed the "every run gets `eastAsia` set" CJK-font guarantee (526/880 correct runs vs. the generator's clean 283/283). A hand-edit doesn't just risk being overwritten later — it can silently break invariants the generator enforces automatically. This is the strongest real-world argument for "never hand-edit `dist/`" this project produced. |
| P13 | A reader-suggested addition (a short worked-example clip from a real downloaded interview) would have been a genuine copyright problem if shipped | The obvious source video had no creator metadata and carried third-party recording-software caption artifacts — not something this project had rights to redistribute into a public, CC-BY-licensed repo | **Raise a rights question explicitly (AskUserQuestion) instead of proceeding on request.** The resolution — a fully synthetic clip (generated background + offline TTS narration) run through the *real* documented pipeline — cost about the same build time as using the real clip would have, and left zero rights ambiguity. Default to synthetic/generated sample media for any public tutorial repo unless the source's rights are unambiguous and documented. |

---

## 6. "See it work before installing anything" — worth doing at S5, not after ship

Added post-publish here; do it during initial authoring on tutorial #4. A
tiny (~10s), purpose-built, rights-clear sample — committed to the repo,
already run through the full pipeline, with its gate-chain command given
verbatim — lets a reader verify a real result and run `run_gates.py` in
under a minute, before installing a single dependency. This is worth more
than a screenshot: it's a live, falsifiable claim the reader can check
themselves on their own machine, immediately.

```gitignore
# Narrow, deliberate exception to a general "no video files" rule:
!/starter/sample/*.mp4
```

Keep the exception narrow and comment *why* right above it — a broad
`.gitignore` carve-out invites the next contributor to assume real footage
is fine to commit elsewhere in the repo. It is not (see P13).

---

## 7. Definition of Done (same shape as tutorial #2, one line added)

- [ ] `reviews/` has all five reviews, written at the time, one-word verdicts
- [ ] every phase has an artifact; every claim has a source or a stated assumption
- [ ] the gate chain's exit-code contract is intact, and includes a check for
      **silent no-op / passthrough failure** in every step that depends on an
      external tool or service (§4) — not just "did the step run"
- [ ] EN and ZH have identical section/checkbox counts; both come from **one**
      content source, not two hand-synced ones (§0)
- [ ] `selfcheck.py` passes locally **and** on GitHub Actions
- [ ] `.docx`/`.pptx` regenerated after the last content edit; opened and
      visually checked (COM automation or by hand), not just XML-validated
- [ ] any sample media committed to the repo is either genuinely
      rights-clear and documented as such, or not committed at all (§5 P13)
- [ ] release/ship review restates known gaps, not just what shipped
- [ ] **the owner has actually opened the shipped deliverable and read it** —
      budget time after "CI is green" for this; it is where the real defects
      surface (§5 P12)

---

## 8. Adapting this to Tutorial No. 4

**Keep unchanged:** the invariant in §0 (single content source, `L()`
pattern), the ten-step order, the authority contract scaled to the subject
(§2), the exit-code contract, the five-review audit trail, `selfcheck.py`,
the "check the generator, not just the artifact" habit.

**Replace:** the subject, the domain agent(s), the gate chain, the pins.

**Ask explicitly at S0, before writing anything:**

| Decision | Question |
|---|---|
| Topology | Does this subject's qualitative surface need one domain agent, two, or genuinely zero? Don't default to the last project's count. |
| Silent-failure gate | What does "this step ran, reported success, and did nothing" look like for *this* pipeline, and how do you detect it independent of the tool's own exit code? (§4) |
| Sample media | If the tutorial benefits from a worked example, can you build one with zero rights ambiguity (synthetic/generated), rather than reaching for real third-party content? (§5 P13) |
| Generated deliverables | Is there a single-source bilingual (or multi-format) content pattern available from day one, or will you be hand-syncing two build scripts again? |

**First 90 minutes, concretely (unchanged from tutorial #2):**

1. `git init -b main`; add `.gitattributes` and `.gitignore`; commit empty skeleton.
2. Write `PLAN.md` — scope, out-of-scope, team topology sized per S0 above.
3. Run `/plan-ceo-review`; land `reviews/01-ceo-review.md` before any prose.
4. Run `/spec`; land `reviews/02-spec.md` with tasks and escalations.
5. Design the gate chain including its silent-failure gate (§4) before writing `run_gates.py`.
6. Set up the `L()` single-source content module before writing slide/doc content, not after.
7. Copy `.github/scripts/selfcheck.py`; edit the required-file list and add a "generated, not hand-made" section from the start.

Everything after that is S3–S9 on repeat, and budget real time for S9's
aftermath — a shipped tutorial keeps generating legitimate follow-up
commits for as long as anyone actually reads it closely.

---

*Licence: prose CC BY 4.0, code Apache-2.0 — Copyright 2026 Prof. Yi-Kuen Lee.*

# Review 02 — Spec (`/spec`)

```
Date:            2026-09-15
Reviewer role:   PM
Command:         /spec
Scope reviewed:  CEO decisions D1-D5 (01-ceo-review.md); work breakdown for Phases 0-5
Verdict:         PASS (with two escalations, see § Escalations; time budget revised)
```

---

## Fixed constraints (given, not negotiable)

- Python `>=3.10,<3.13` · `videocaptioner` (pin whatever version `--version` reports
  at install time — no single upstream commit to lock, see `PLAN.md` § 5)
- Gates **T1-T4** must PASS with evidence captured (command output, `ffprobe` diff);
  Gate **T5** runs the procedure in `docs/expertise_division.md` § 4
- No silent translator fallback — `config show` provenance check is mandatory, not optional
- One domain agent resident: **Bilingual Caption QA Specialist** (Gate T5 only)

---

## Work items

| ID | Work item | Owner | Input | Output | Judged by | Est. | Blocked by |
|---|---|---|---|---|---|---|---|
| W1 | Toolchain install (Python, FFmpeg, `pip install videocaptioner`) | solo/DevOps | `starter/INSTALL.md` | `doctor` clean | Phase 0 exit criterion | 0.5-1.5 h | — |
| W2 | Translator credentials configured | solo/DevOps | API key | `llm.*` set | `config show` | 0.25 h | W1 |
| W3 | Check source video for pre-existing burned-in captions | Engineer | source `.mp4` | 2-3 frame grabs, go/no-go | visual check | 0.25 h | — (parallel with W1-W2) |
| W4 | Transcribe (ASR) | Engineer | source `.mp4` | raw `.srt`, N segments | Gate T1 | 0.1-0.5 h | W1 |
| W5 | Hand-correct transcript | Engineer | raw `.srt` | corrected `.srt`, same N | human read-through | 0.1-0.25 h | W4 |
| W6 | Translate, Chinese-only | Engineer | corrected `.srt` | target `.srt`, same N | Gates T2, T3 | 0.1-1 h (scales with clip length) | W2, W5 |
| W7 | Style config, only if W3 found a conflict | Engineer | W3 result | style JSON / `--style-override` args | preview frame check | 0-0.5 h | W3 |
| W8 | Synthesize (hard-burn) | Engineer | W6 + W7 | captioned video | Gate T4 | 0.1-0.5 h | W6, W7 |
| W9 | Gate T5 fidelity review | **Bilingual Caption QA Specialist** | English `.srt` + Chinese `.srt` (never the video) | PASS / PASS-WITH-FLAG verdict | Gate T5 procedure itself | 0.25-0.5 h | W6 |
| W10 | Bilingual docs + release package | DevOps | all above | EN+ZH `.md`/`.docx`, evidence bundle | Definition of Done (`PLAN.md` § 6) | 1-2 h | W8, W9 |

**Revised total: 2.5-7 h**, not the CEO's flat 2-4 h. This review is not silently
cutting the CEO's number — it's naming why the range is wider: **W1 alone can eat
the entire low end of the CEO's budget if the reader hits the #1-ranked risk from
`01-ceo-review.md` § B3** (the PowerShell `--style-override` quoting failure,
which strikes inside W7, not W1 — so a reader who sails through install can still
lose 30-60 minutes there). `PLAN.md` § 3's "2-4 h" should be read as the
**no-surprises** case; this spec's 2.5-7 h is the honest range including the one
failure mode most likely to actually occur.

---

## Critical path

```
W1 ─► W2 ─► W6 ─► W8 ─► W9 ─► W10
       W4 ─► W5 ──┘
W3 ─────────────► W7 ──┘
```

W3 (burned-in caption check) and W1/W2 (install/config) run in parallel — neither
depends on the other. W7 only exists if W3 finds a conflict; when it doesn't,
skip straight from W3 to W8 with the default style, exactly as this tutorial's
own pilot run did on its second clip (no pre-existing caption found, default
style used, no W7 work at all).

---

## Escalations to the domain agent

Per the defer clause (`docs/expertise_division.md` § 6), the following were
**not** decided by this role:

| # | Question | Referred to | Why this role cannot decide |
|---|---|---|---|
| E1 | What counts as "natural" Chinese for a given register — a casual interview clip vs. a formal presentation clip may have different fluency bars. Does Gate T5's checklist need a register field? | **Bilingual Caption QA Specialist** | Register judgment is exactly the expertise gap this domain agent exists to close; this role has no basis to answer it. |
| E2 | Gate T5 samples segments 1-5 / ~50% / last-5, same as Gate T3's mechanical count check. Is that sampling density sufficient for a long clip (e.g. spaceX1's 1086 segments), or does fidelity review need to scale with length the way translation time (W6) does? | **Bilingual Caption QA Specialist** | Whether a fixed 13-segment sample generalizes to a 1000+ segment clip is a domain judgment about review statistics, not a process question. |

Both are open. This spec proceeds without waiting on them (unlike tutorial #2,
where E1/E2 blocked engineering) because neither blocks W1-W8 — they only affect
how Gate T5 (W9) is run, and W9 is late in the critical path with room to resolve
them before it starts.

---

## Blocking issues

None at filing time. The time-budget revision above is a **note**, not a
blocker — the CEO's scope (D1-D5) stands; only the estimate changed.

---

## Non-blocking notes

- W3 should run **before** W1/W2 if the reader can manage it in parallel — it's
  the cheapest work item (0.25 h) and its result (does a style override even get
  needed) determines whether W7 exists at all. Front-loading it avoids discovering
  late that a style decision was needed.
- W5 (hand-correction) is easy to skip under time pressure. Don't. This tutorial's
  own pilot run caught three real ASR errors (a dropped word, wrong capitalization,
  a garbled compound) at this step — skipping it pushes bad English into W6 and
  the mistake becomes a translation-quality problem instead of a two-minute edit.
- W9 is the one item with no mechanical gate underneath it — same shape as
  tutorial #2's W8 (analog track, "the only item with no gate," a known, stated
  limitation, not a hidden one).

---

## Decisions recorded (do not relitigate in later phases)

| # | Decision |
|---|---|
| S1 | `starter/` ships install instructions and gate-chain scripts. It does not vendor `videocaptioner` itself or any *real* sample video — same "pointer, not payload" principle as tutorial #2 S1. **Superseded in part, 2026-09-16:** `starter/sample/` now ships a small, purpose-built *synthetic* clip (generated visual + offline TTS narration, zero rights ambiguity) so a reader can see a real result and run the gate chain before installing anything — see `starter/sample/README.md`. The constraint against vendoring *real* footage (a reader's or the author's own pilot video, which may carry rights the author cannot redistribute) still stands. |
| S2 | Gates are numbered T1-T5 (Tutorial-3-local numbering) — no relationship to tutorial #2's Gate 5/6/7A/7B-1R2 numbering. Do not try to make the numbers line up across tutorials; the subjects don't share a gate chain. |
| S3 | Sampling for Gate T3 (mechanical count) and Gate T5 (fidelity) both use segments 1-5 / ~50% / last-5 for now. E2 may revise this for long clips — until then, this is the standard. |
| S4 | W7 (style config) is conditional, not mandatory. A clean source video (no pre-existing captions) skips it entirely — do not treat "no style work needed" as an incomplete run. |

---

## What was NOT reviewed

- Whether `docs/expertise_division.md`'s 4-question Gate T5 checklist is the
  *right* four questions — domain-agent territory (E1 touches this).
  Answering it in a later pass, not now.
- `starter/scripts/run_gates.py` — does not exist yet; W1-W9 above are
  reviewed as a work breakdown, not as verified runnable code.
- Licence/attribution text for `videocaptioner` itself in the release package —
  deferred to `/ship` (a future `05-ship.md`), same as tutorial #2's spec review.

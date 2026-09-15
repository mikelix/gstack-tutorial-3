# Review 03 — Engineering (`/plan-eng-review`)

```
Date:            2026-09-15
Reviewer role:   Engineer
Command:         /plan-eng-review
Scope reviewed:  starter/scripts/run_gates.py (Gates T1-T4 + T5 guard); W1-W9 build
Verdict:         PASS
```

---

## Build log

`starter/scripts/run_gates.py` was written and then run against **real
artifacts from this tutorial's own pilot session** — not synthetic test
data — mirroring tutorial #2's S4 discipline: prove the mechanism, don't
just describe it.

**Artifacts used** (from the pilot's `Elon_Musk_make_money_by_time_2026`
run): source video (89.13s, 1080x596), source `.srt` (32 segments, hand-
corrected), target `.srt` (32 segments, Chinese-only, translated via
`llm`), and the final synthesized output video.

**Run 1 — normal invocation:**
```
T1 PASS — Elon_Musk_make_money_by_time_2026.srt: 32 segments
T2 PASS — translate.service = llm
T3 PASS — 32 segments in both source and target
T4 PASS — 1080x596, 89.131s (source) vs 89.131s (output)
T5 NOT AUTO-VERIFIED — run docs/expertise_division.md section 4 by hand ...
Gates T1-T4: PASS. Gate T5: run it by hand before calling this done.
exit code: 0
```

**Run 2 — `--ocr-check` (deliberately triggering the circularity guard):**
```
T5 VOID — OCR-vs-own-srt is circular: it only re-proves synthesis fidelity
(T4), not translation fidelity. ...
exit code: 2
```

**Run 3 — `--translator bing` (a genuine mismatch, translator was actually `llm`):**
```
T1 PASS — ...
T2 FAIL: expected translator 'bing', config show reports 'llm' — check for a silent fallback
exit code: 1
```

All three exit codes (0 PASS, 2 VOID, 1 FAIL) confirmed distinct and
correctly triggered. The exit-code contract from `PLAN.md` § 4 is not
aspirational — it is verified behavior as of this commit.

---

## Escalation responses (answering `reviews/02-spec.md` § Escalations)

**E1 — Does Gate T5 need a register field (casual vs. formal speech)?**

Answered by this role in the Bilingual Caption QA Specialist capacity per
`docs/expertise_division.md`: **yes, as a note field, not a pass/fail axis.**
Adding register as a fifth PASS/FAIL question would overfit a lightweight
gate — most short clips don't need it, and a false "register mismatch FAIL"
on a clip with genuinely mixed registers (a casual aside inside a formal
talk) would train reviewers to ignore the flag. Instead: the reviewer
should note the source's apparent register once, at the top of a Gate T5
pass, as calibration context for the four existing questions (a "natural"
answer in a casual interview reads differently than "natural" in a keynote).
No code change needed — this is a procedural addition to
`docs/expertise_division.md` § 4's instructions, not a new gate.

**E2 — Does the fixed 13-segment sample scale to a 1000+ segment clip
(e.g. spaceX1)?**

Answered: **no, not as-is — it needs a floor-and-scale rule.** A fixed
sample proportionally under-covers a long clip: 13 out of 32 segments
(this pilot's short clip) is ~40% coverage; 13 out of 1086 segments
(spaceX1) is ~1.2% coverage — order-of-magnitude different confidence.
Recommendation for the next pass: keep the 1-5 / middle / last-5 pattern as
the floor for any clip, and add one additional 5-segment block per
additional ~200 segments beyond the first 100, capped at 40 total sampled
segments so review time stays bounded. This is a design change to
`docs/expertise_division.md` § 4, not yet applied — tracked as an open item
below, not silently assumed to already be fixed.

---

## Evidence

| Claim | Evidence |
|---|---|
| Gates T1-T4 pass on real output | Run 1 log above |
| VOID has a genuinely distinct exit code, not just a printed warning | Run 2, exit code 2, confirmed via `$LASTEXITCODE` |
| A real mismatch is caught, not silently passed | Run 3, exit code 1 |
| `run_gates.py` requires no third-party dependencies | stdlib-only (`argparse`, `json`, `re`, `subprocess`, `pathlib`) — matches S1's "pointer, not payload" principle |

---

## Blocking issues

None.

---

## Non-blocking notes

- **T2's real limitation, found while building, not hidden:** Gate T2 reads
  `videocaptioner config show`'s *current* state, not a record made at the
  moment the translate command actually ran. If a reader runs several
  translate commands with different `--translator` flags before checking,
  T2 only reflects whichever ran last — it cannot retroactively audit an
  earlier command. Mitigation, to be added to `starter/INSTALL.md` or the
  full tutorial body: **run the gate check immediately after the one
  translate command you care about**, don't batch multiple translations
  before verifying. This is the same shape of limitation as tutorial #2's
  circularity trap in miniature — a check that looks complete but is only
  checking the *latest* state, not the *relevant* state — worth naming
  explicitly rather than letting a reader discover it by getting burned.
- E2's sampling-scale fix (above) is a real open item, not yet applied to
  `docs/expertise_division.md`. Tracked here so it isn't silently dropped.

---

## Decisions recorded

| # | Decision |
|---|---|
| E1 | Register is a note field in Gate T5's procedure, not a fifth pass/fail question. |
| E2 | Gate T5 sampling needs a floor-and-scale rule for long clips — **not yet implemented**, tracked as an open item for the next pass on `docs/expertise_division.md`. |
| E3 | Gate T2's freshness limitation (reads current config state, not invocation-time state) is a stated limitation, to be documented in the tutorial body, not silently left for a reader to discover. |

---

## What was NOT reviewed

- Gate T5 itself was not run in this pass — only its guard code (the
  refusal to accept `--ocr-check` as evidence) was exercised. An actual
  fidelity review of the Elon Musk clip's translation was done earlier in
  the pilot session (informally), not repeated here as a formal Gate T5
  record — that belongs in a future `04-qa-report.md`.
- E2's floor-and-scale fix was designed, not implemented — `docs/
  expertise_division.md` § 4 still describes the flat sample only.
- Windows-only verification — this run happened on the same Windows 11
  machine `starter/INSTALL.md` was piloted on. No macOS/Linux run of
  `run_gates.py` has happened yet (same stated gap as the install guide).

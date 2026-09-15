# Review 01 — CEO (`/plan-ceo-review`)

```
Date:            2026-09-15
Reviewer role:   owner / CEO
Command:         /plan-ceo-review
Scope reviewed:  PLAN.md (v1, skeleton pass) + README.md positioning
Verdict:         REVISE
```

---

## Blocking issues

**B1 — Gate T5's "domain agent" is named but not operationalized.**
`PLAN.md` § 2 invents a "Bilingual Caption QA Specialist" and gives it
authority over translation fidelity, but unlike tutorial #2's
`docs/expertise_division.md` (a RACI table, three veto rules, and a
verbatim defer clause pasted into every prompt), tutorial #3 has no file
that says what this agent actually *is* — a persona spec, a prompt, a
checklist a human follows standing in for it? Right now "the domain agent
reviews it" is a placeholder for "someone should read the Chinese," which
is not a gate, it's a hope.
*Fixed when:* a `docs/expertise_division.md` equivalent exists naming the
concrete review procedure Gate T5 actually runs (even if the "agent" is
a structured prompt a human runs against an LLM, that structure must be
written down, not implied).

**B2 — The "85-95% production-readiness" number is unverifiable, same
shape as tutorial #2's B1.**
`PLAN.md` § 1 asserts this fraction with no method behind it — no worked
example, no failure-mode count it's derived from. An ungrounded number in
the positioning section makes the rest of the scope section suspect by
association, exactly as tutorial #2's reviewer flagged for the RMB 1.25M
valuation claim.
*Fixed when:* either the number is removed from the headline (replaced
with the concrete claim: "a reader can go from raw clip to verified
captioned output in one sitting"), or it is kept with the two or three
failure modes it's actually netting out against, named.

**B3 — No drop-out analysis.**
Tutorial #2's B3 named the real risk correctly: not a wrong output, a
reader who never finishes installing. Tutorial #3's `PLAN.md` § 7 lists
risks but does not rank them or say which one actually kills a first-time
reader's session. From this session's own pilot run, the two real
drop-out points were: (a) the PowerShell JSON-quoting failure on
`--style-override`, hit twice before being diagnosed, and (b) getting the
LLM translator's `api_base`/`model`/`api_key` right the first time with no
feedback until a translate command is actually run.
*Fixed when:* § 7 states explicitly which risk is the highest-probability
drop-out point and what the tutorial does about it before the reader hits
it (not just a troubleshooting-table entry after the fact).

---

## Non-blocking notes

- The 5-gate design (T1-T5) with a stated VOID condition is the right
  shape and should stay the spine of every document that follows — it is
  the direct, scaled-down analog of tutorial #2's gate chain and carries
  the same intellectual weight (the circularity lesson) in a fraction of
  the words.
- Scoping out byte-for-byte translation determinism, instead of silently
  claiming it, is correct and should be kept exactly as worded.
- The "one-key-and-a-half system" framing (§ 2.1) — honestly weaker than
  tutorial #2's two-key system because the subject is lower-stakes — is a
  good instinct. Keep it; do not inflate the domain-agent framing to
  sound more dramatic than the subject warrants.

---

## Decisions accepted

| # | Decision | Reason |
|---|---|---|
| D1 | Scope = **install → transcribe → translate (Chinese-only) → synthesize → 5-gate verify**. Dubbing and non-Chinese targets are out, stated not hidden. | Matches tutorial #1/#2's discipline of a named, bounded v1. |
| D2 | Windows 11 is the primary, fully-detailed install path; macOS/Linux are secondary and may be less exhaustively tested. | Matches this tutorial's actual pilot environment; tutorial #2 did the same (Windows primary, VM/other platforms secondary). |
| D3 | Ship **bilingual** (EN + 简体中文), Markdown as source of truth, Word/PPTX generated from it. | Same reasoning as tutorial #2 D3 — one conceptual change touches 4 files; make the generation mechanical, not hand-maintained. |
| D4 | One domain agent (Bilingual Caption QA Specialist), not two. | The subject has exactly one genuine expertise gap (translation fidelity judgment); inventing a second agent would be decoration, not authority. |
| D5 | LLM translation determinism is explicitly out of scope, stated as a limitation rather than a claim. | Same honesty discipline as tutorial #2's stated PEX/RCX gap — a stated limitation teaches; a silent one is later discovered by a disappointed reader. |

---

## Decisions rejected (with reason)

| # | Rejected proposal | Why |
|---|---|---|
| R1 | "Give this tutorial two domain agents like #2, for narrative symmetry." | Manufactured authority nobody needs is worse than none — see D4. The subject has one expertise gap, not two. |
| R2 | "Claim the pipeline is fully reproducible, like tutorial #2's GDS SHA." | False by construction — an LLM translator is not deterministic across runs. Claiming it would be the exact B1-shaped mistake this review exists to catch. |
| R3 | "Skip the macOS/Linux install sections since the pilot only ran on Windows." | Stating a secondary, less-tested path honestly (as done) is better than omitting platforms entirely — the tool itself is genuinely cross-platform; only test depth differs. |

---

## Scope cut list (cut in this order when time runs short)

1. macOS/Linux install depth — keep the sections, but they may stay
   secondary/untested-in-depth if time runs out; Windows must stay fully
   verified.
2. The bilingual docx/pptx exports — Markdown alone is sufficient to *use*
   the tutorial, same reasoning as tutorial #2's cut list item 3.
3. Assessment/next-steps material, if a Part N for it is ever added —
   enrichment, not proof.
4. **Never cut:** Gates T1-T4 (the mechanical chain), the VOID condition
   and its worked example, or the install guide's PowerShell-quoting
   section — that section is not filler, it is the single highest-value
   paragraph in the tutorial given B3 above.

---

## Open questions (deliberately unanswered at this stage)

1. What does Gate T5 concretely look like as a runnable (or at least
   scriptable-checklist) step, not just a named responsibility? **Referred
   to the Bilingual Caption QA Specialist** — this role cannot invent that
   agent's own procedure; that is exactly the kind of question this CEO
   review is not equipped to answer, per B1.
2. Is 2-4 hours a realistic time budget for a first-time reader including
   the PowerShell troubleshooting from B3, or does that number need to
   come down (or up)? Unknown until someone times a cold run against
   `starter/INSTALL.md` as written.

> Note question 1 is marked **referred**, not answered — same defer-clause
> discipline tutorial #2 modeled: this role names the gap, it does not
> guess the domain answer.

---

## What was NOT reviewed

- `starter/INSTALL.md`'s technical accuracy beyond spot-checking against
  this session's live `videocaptioner doctor`/`config show` output — no
  independent macOS/Linux install was actually run.
- Any gate-chain *code* — `starter/scripts/run_gates.py` does not exist
  yet, so T1-T5 are reviewed as a design, not as verified behavior.
- `TUTORIAL.md` body content — does not exist yet at time of this review.

---

## Addendum

**2026-09-15, same session — after applying fixes.**
B1 resolved: added `docs/expertise_division.md` naming the concrete Gate T5
procedure. B2 resolved: replaced the ungrounded "85-95%" headline number in
`README.md`/`PLAN.md` with the concrete, falsifiable claim and moved the
qualitative estimate into an appendix-style note with its basis stated.
B3 resolved: `PLAN.md` § 7 now ranks the PowerShell-quoting failure as the
highest-probability drop-out point and points to `starter/INSTALL.md` § 6
*before* the reader can hit it, not only in the troubleshooting table.
Verdict upgraded to **PASS**.

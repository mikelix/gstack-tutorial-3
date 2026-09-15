# gstack-tutorial-3 — English → Chinese Video Captioning with videocaptioner

> **Status: skeleton.** This is the "first 90 minutes" scaffold per
> [`gstack-tutorial-2/PLAYBOOK.md`](https://github.com/mikelix/gstack-tutorial-2/blob/main/PLAYBOOK.md)
> § 6 — scope, gate-chain design, and the install guide are locked; the full
> step-by-step `TUTORIAL.md`, the five audit-trail reviews (`reviews/`), and
> the bilingual docx/pptx exports have not been written yet.

**What this is.** A hands-on tutorial: use the **gstack** agent workflow plus
one domain agent (a Bilingual Caption QA Specialist) to build and verify a
real English→Chinese video-captioning pipeline with `videocaptioner` — ASR
transcription, LLM translation, hard-burn synthesis, and a 5-gate
verification chain that catches the two failure modes that actually happened
piloting this tutorial: a silent translator fallback, and mistaking
synthesis fidelity for translation fidelity.

**What this is not.** Not a linguistics course. Not a claim that LLM
translation is deterministic — see `PLAN.md` § 1 for the honest scope line.

---

## 0. Why a third tutorial

| | Tutorial #1 | Tutorial #2 | Tutorial #3 |
|---|---|---|---|
| Carrier | `hello_world.py` | RTL→GDS EDA system | English→Chinese video captions |
| Team | 5 gstack roles | 5 roles × 2 domain agents | 5 roles × 1 domain agent |
| Proof of done | review notes merge | gate chain PASS + GDS SHA match | gate chain PASS (T1-T4) + fidelity review (T5) |
| Environment | none | multi-GB open EDA + open PDK | one `pip install` + FFmpeg |
| Setup time | minutes | 10-14 h | 2-4 h (see `PLAN.md` § 3) |

Tutorial #2 proved the "gstack + domain agent(s) + gate chain" pattern on a
genuinely hard subject (silicon). Tutorial #3 asks the opposite question:
**does the same pattern still pay for itself on an easy subject?** The
answer, worked out in `PLAN.md` § 2.1: yes, but the authority split is
lighter — one domain agent, not two, and its veto only fires on the one gate
(T5) that is inherently qualitative.

---

## 1. Repository layout (current)

| Path | Purpose |
|---|---|
| [`PLAN.md`](PLAN.md) | Scope, team topology, 5-gate verification chain, Definition of Done |
| [`starter/INSTALL.md`](starter/INSTALL.md) | **Step-by-step videocaptioner install** — Windows 11 (primary, fully detailed), macOS, Linux |

**Not yet written** (next pass, per the scope decision that produced this
skeleton): `TUTORIAL.md` (+ `.zh.md`), `reviews/` (five audit-trail records),
`starter/scripts/run_gates.py` (the T1-T5 verification chain as runnable
code), `docs/`, `dist/` (bilingual docx/pptx), `.github/workflows/selfcheck.yml`.

---

## 2. Licence

Prose under **CC BY 4.0**, code under **Apache-2.0** — Copyright 2026 Prof.
Yi-Kuen Lee. (Matches tutorial #1 and #2.)

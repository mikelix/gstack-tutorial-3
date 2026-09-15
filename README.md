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
| Setup time | minutes | 10-14 h | 2-4 h best case / 2.5-7 h honest range (see `reviews/02-spec.md`) |

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
| [`PLAN.md`](PLAN.md) | Scope, team topology, 5-gate verification chain, ranked risks, Definition of Done |
| [`starter/INSTALL.md`](starter/INSTALL.md) | **Step-by-step videocaptioner install** — Windows 11 (primary, fully detailed), macOS, Linux |
| [`docs/expertise_division.md`](docs/expertise_division.md) | **The Gate T5 procedure** — what the Bilingual Caption QA Specialist concretely does, RACI, defer clause |
| [`reviews/01-ceo-review.md`](reviews/01-ceo-review.md) | First audit-trail record — a real REVISE→PASS review of this repo's own `PLAN.md`, blocking issues and all |
| [`reviews/02-spec.md`](reviews/02-spec.md) | W1-W10 work breakdown, critical path, two escalations to the domain agent, and a revised (honest) time budget |
| [`starter/scripts/run_gates.py`](starter/scripts/run_gates.py) | **Gates T1-T4 as runnable code**, plus a mechanised VOID guard against the T5 circularity trap. Verified against this tutorial's own pilot artifacts — see `reviews/03-eng-review.md` (next pass) for the run log. |
| [`starter/versions.lock.template`](starter/versions.lock.template) | Per-run evidence template (Python/videocaptioner/ffmpeg versions, LLM provider, run date) — copy to `versions.lock` (gitignored) before your first real run |
| [`reviews/03-eng-review.md`](reviews/03-eng-review.md) | `run_gates.py` proven against real pilot artifacts (PASS/VOID/FAIL all confirmed distinct); both spec-review escalations answered |

**Not yet written** (next pass): `TUTORIAL.md` (+ `.zh.md`), `reviews/04-qa-report.md`
and `reviews/05-ship.md`, `dist/` (bilingual docx/pptx),
`.github/workflows/selfcheck.yml`. Also open: the E2 sampling floor-and-scale
fix designed in review 03 but not yet applied to `docs/expertise_division.md`.

---

## 2. Licence

Prose under **CC BY 4.0**, code under **Apache-2.0** — Copyright 2026 Prof.
Yi-Kuen Lee. (Matches tutorial #1 and #2.)

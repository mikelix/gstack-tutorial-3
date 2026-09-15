# gstack-tutorial-3 — English → Chinese Video Captioning with videocaptioner

> **Status: complete in Markdown, bilingual, self-checked.** Tutorial body
> (EN + 简体中文), gate chain as runnable code, four audit-trail reviews, and
> a CI self-check (63 checks) are all in place. Remaining: `reviews/05-ship.md`
> and the `dist/` docx/pptx exports.

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
| **[`TUTORIAL.md`](TUTORIAL.md)** | **The step-by-step course — start here.** Part 0 mental model → install → translator choice → the five gstack phases → verification → troubleshooting → appendices |
| [`TUTORIAL.zh.md`](TUTORIAL.zh.md) | 简体中文版，与英文版逐节对应（parity enforced in CI） |
| [`PLAN.md`](PLAN.md) | Scope, team topology, 5-gate verification chain, ranked risks, Definition of Done |
| [`starter/INSTALL.md`](starter/INSTALL.md) | **Step-by-step videocaptioner install** — Windows 11 (primary, fully detailed), macOS, Linux |
| [`docs/expertise_division.md`](docs/expertise_division.md) | **The Gate T5 procedure** — what the Bilingual Caption QA Specialist concretely does, RACI, defer clause |
| [`reviews/01-ceo-review.md`](reviews/01-ceo-review.md) | First audit-trail record — a real REVISE→PASS review of this repo's own `PLAN.md`, blocking issues and all |
| [`reviews/02-spec.md`](reviews/02-spec.md) | W1-W10 work breakdown, critical path, two escalations to the domain agent, and a revised (honest) time budget |
| [`starter/scripts/run_gates.py`](starter/scripts/run_gates.py) | **Gates T1-T4 as runnable code**, plus a mechanised VOID guard against the T5 circularity trap. Verified against this tutorial's own pilot artifacts — see `reviews/03-eng-review.md` (next pass) for the run log. |
| [`starter/versions.lock.template`](starter/versions.lock.template) | Per-run evidence template (Python/videocaptioner/ffmpeg versions, LLM provider, run date) — copy to `versions.lock` (gitignored) before your first real run |
| [`reviews/03-eng-review.md`](reviews/03-eng-review.md) | `run_gates.py` proven against real pilot artifacts (PASS/VOID/FAIL all confirmed distinct); both spec-review escalations answered |
| [`docs/choosing_a_translator.md`](docs/choosing_a_translator.md) | **Which translator for YOUR machine/network/budget** — decision guide, observed availability, and a 2-minute probe to run before committing to a long clip |
| [`reviews/04-qa-report.md`](reviews/04-qa-report.md) | Five findings, one critical: a free translator that silently emits untranslated English and exits 0, defeating four of five gates. Drove Gate T3b. |
| [`dist/`](dist/README.md) | **Generated deliverables** — bilingual `.pptx` (31 slides) and `.docx` (15/17 pp.) in McKinsey house style. Never hand-edit; rebuild from `_build/`. |
| `_build/` | Exporters: `mck.py` slide primitives, `deck_content.py` / `doc_content.py` (single bilingual source), builders, `verify_docx.py` |
| `.github/scripts/selfcheck.py` | 87 checks: required files, every markdown link, EN/ZH parity, gate-script compile + exit-code contract, BOM-safe reads, deliverable integrity |
| `.github/workflows/selfcheck.yml` | CI — runs the self-check and asserts `run_gates.py` exits 3 on missing input rather than passing vacuously |

### Deliverables

| Format | English | 简体中文 |
|---|---|---|
| Markdown (source of truth) | [`TUTORIAL.md`](TUTORIAL.md) | [`TUTORIAL.zh.md`](TUTORIAL.zh.md) |
| PowerPoint (31 slides) | `dist/gstack-tutorial-3_EN.pptx` | `dist/gstack-tutorial-3_ZH.pptx` |
| MS Word | `dist/gstack-tutorial-3_EN.docx` | `dist/gstack-tutorial-3_ZH.docx` |

Both editions of both formats generate from **one** content structure in
which every string is an `L(en, zh)` pair, so EN and ZH cannot drift apart
in structure. Style follows `MCKINSEY_DOCX_PLAYBOOK.docx`: navy `#1F4E78`,
Calibri body, Consolas code, Microsoft YaHei for Chinese with `eastAsia` set
on every run. The deck adds **action titles** — every slide title is the
takeaway as a sentence, so reading titles alone gives the whole argument.

**Not yet written:** `reviews/05-ship.md`. Also open: the E2 sampling
floor-and-scale fix designed in review 03 but not yet applied to
`docs/expertise_division.md`.

---

## 2. Licence

Prose under **CC BY 4.0**, code under **Apache-2.0** — Copyright 2026 Prof.
Yi-Kuen Lee. (Matches tutorial #1 and #2.)

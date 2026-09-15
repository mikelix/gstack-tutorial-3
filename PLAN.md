# PLAN — gstack-tutorial-3

Scope, phases, team topology and the Definition of Done.
Authored following [`gstack-tutorial-2/PLAYBOOK.md`](https://github.com/mikelix/gstack-tutorial-2/blob/main/PLAYBOOK.md)
§6 "Adapting this to Tutorial No. 3" — this is the "first 90 minutes" skeleton;
the full step-by-step `TUTORIAL.md`, the five audit reviews, and the bilingual
docx/pptx exports follow in a later pass once this scope is confirmed.

---

## 1. Scope

**Subject.** Build and verify an English → Chinese (简体中文) video-caption
pipeline using the `videocaptioner` CLI: transcribe (ASR) → translate (LLM,
Chinese-only) → synthesize (hard-burn the caption into the video) → verify.

**The one thing a reader can do afterwards that they could not before:** take
any English-speaking video clip and produce a video with clean, correctly
positioned, verifiably-accurate Chinese hard-subtitles — and know, with
evidence rather than a glance, that the translation actually ran on the
translator they asked for and that the output video was not silently
re-encoded, cropped, or retimed.

**In scope**
- `videocaptioner` install on Windows 11 (primary — see `starter/INSTALL.md`),
  with macOS and Linux covered as secondary paths
- ASR transcription (free `bijian` engine, English source)
- Manual transcript correction pass (the tutorial teaches *why*, not just *how*)
- LLM-backed translation to Chinese, target-only layout, with an explicit
  no-silent-fallback rule (never Bing/Google unless asked for)
- Hard-burn synthesis with style control (font size, vertical position)
- A 5-gate verification chain (§ below) with a stated **VOID** condition
- Bilingual (EN + 简体中文) tutorial deliverables, mirroring tutorial #1/#2

**Out of scope (stated, not hidden)**
- Byte-for-byte reproducibility of the *translated text* — an LLM translator
  is not guaranteed deterministic run-to-run (temperature / sampling), unlike
  tutorial #2's GDS SHA. What *is* held to strict determinism: segment count,
  timestamps, and output video resolution/duration (see Gate T3/T4). This
  honest distinction is itself a lesson worth teaching, not a gap to hide.
- Dubbing / TTS (`videocaptioner dub`) — videocaptioner supports it, this
  tutorial does not cover it. Stated as v1.1+ roadmap, not silently dropped.
- Non-Chinese target languages — the pipeline generalizes (38 BCP-47 codes
  supported by the tool) but this tutorial pins EN→zh-Hans throughout.
- Removing pre-existing burned-in captions from the *source* video (a pixel
  problem, not a subtitle problem — see the playbook's own lesson on this,
  carried over from the pilot run this tutorial is based on).

**Positioning (honest numbers)**
This is a content-production workflow tutorial, not a linguistics or ASR
research project. Teaching/production-readiness objective: high (~85-95%) —
the pipeline is simple enough to actually reach "done, verified" within one
sitting, unlike tutorial #2's EDA toolchain. The harder part is not the
mechanics, it's building the habit of *verifying* each stage before trusting
it — that is the actual content of this tutorial.

---

## 2. Team topology

| gstack role | Command | Duty | Domain agent invoked |
|---|---|---|---|
| CEO / owner | `/plan-ceo-review` | scope, positioning, honest boundaries | — |
| PM | `/spec` | decompose into install / transcribe / translate / synthesize / verify | — |
| Engineer | `/plan-eng-review` | run the pipeline, own the verification scripts | **Bilingual Caption QA Specialist** |
| QA | `/qa-only` | verify Gates T1-T5, check for VOID conditions | **Bilingual Caption QA Specialist** (fidelity review) |
| DevOps | `/ship` | package, bilingual docs, release | — |

### 2.1 Why a domain agent is still needed here (smaller version of #2's argument)

The five gstack roles are process experts and domain generalists. They can
run `ffprobe`, diff a segment count, and confirm a translator's `api_base` —
all of that is mechanical and gstack can own it outright. **What gstack
cannot do is read the Chinese output and judge whether it is a faithful,
natural translation** — that requires actual bilingual fluency, the same way
"LVS passed" required semiconductor physics in tutorial #2.

> **Process authority sits with gstack. Translation-fidelity authority sits
> with the Bilingual Caption QA Specialist. On conflict — a mechanical gate
> passes but the domain agent flags a mistranslation — the domain agent wins,
> and the gate chain's PASS is downgraded to PASS-WITH-FLAG until a human
> resolves it.**

This is a **one-key-and-a-half system**, not a full two-key system like
tutorial #2 — the mechanical gates (T1-T4) are sufficient on their own to
prevent the worst failure modes (silent fallback, dropped segments, corrupted
video). The domain agent's veto only fires on Gate T5 (fidelity), which is
qualitative. Worth stating plainly: this is a lighter-weight authority split
than tutorial #2's, because the subject is lower-stakes than silicon.

**Two rules, restated for this subject:**
1. A translator's exit code / `✓ Done` message is not evidence — always
   cross-check `videocaptioner config show` for which `service` actually ran.
2. A gate can pass and the translation still be wrong — checking that the
   burned-in Chinese text matches the `.srt` file used to synthesize it only
   proves **synthesis fidelity**, not **translation fidelity**. Those are two
   different gates (T4 vs T5) and must never be collapsed into one — this is
   this tutorial's version of tutorial #2's LVS circularity pitfall (see § 4).

---

## 3. Phases

| Phase | Owner | Output | Exit criterion |
|---|---|---|---|
| **0 — Environment** | solo | `videocaptioner` installed, translator API key configured | `videocaptioner doctor` clean; `videocaptioner config show` shows the intended translator |
| **1 — CEO review** | owner | scope + positioning locked | `/plan-ceo-review` signed off |
| **2 — Spec** | collaborator | task breakdown | `/spec` filed |
| **3 — Engineering** | owner + Bilingual Caption QA Specialist | captioned video produced | Gates T1-T4 pass |
| **4 — QA** | collaborator + gate chain | verification evidence + fidelity review | Gate T5 pass, no unresolved fidelity flags |
| **5 — Ship** | owner | packaged release + bilingual docs | `/ship` complete |

Time budget: **2-4 h** for a first run on a short clip (under 5 min), including
install time. Materially less than tutorial #2's 10-14 h — the toolchain is a
single `pip install`, not a multi-gigabyte EDA compile.

---

## 4. The 5-gate verification chain

Modeled on tutorial #2's gate chain (`Gate 5/6/7A/7B-1R2` → `run_all.sh` exit
codes), scaled to this subject. Full script: `starter/scripts/run_gates.py`
(to be written in the next pass).

| Gate | Name | Referee | What it checks |
|---|---|---|---|
| **T1** | Transcription completeness | `videocaptioner transcribe` exit status + segment count | Output `.srt` exists, segment count > 0 |
| **T2** | Translator provenance | `videocaptioner config show` | `translate.service` matches the translator requested (e.g. `llm`) — catches a silent Bing/Google fallback |
| **T3** | Segment parity | line-count diff | Target `.srt` segment count == source `.srt` segment count (no dropped/merged lines) |
| **T4** | Synthesis fidelity | `ffprobe` diff | Captioned output's resolution + duration == source video's, exactly |
| **T5** | Translation fidelity (domain) | Bilingual Caption QA Specialist | Spot-checked segments (start/middle/end) are natural, accurate Chinese — not literal/garbled, not a hallucination |

**Exit-code contract** (mirroring tutorial #2's `run_all.sh`):

| Code | Meaning |
|---|---|
| `0` | Gates T1-T4 PASS, T5 not yet reviewed or PASS |
| `1` | A mechanical gate (T1-T4) FAILED |
| `2` | **VOID** — a check was self-referential (see below) |
| `3` | Environment error (tool not installed, no API key configured) |

**The VOID condition.** A "translation fidelity" check is VOID — not PASS —
if it only compares the burned-in video's rendered Chinese text back against
the `.srt` file that was fed into `synthesize`. That loop only proves the
`synthesize` step didn't corrupt the text (a real thing worth checking — it's
Gate T4/T5's rendering half) — it proves nothing about whether the Chinese is
a correct translation of the *original English audio*. A non-circular Gate T5
must compare the Chinese output against the English source transcript (or
better, the original audio) — never against its own translated output.

---

## 5. Pinned versions (do not drift)

| Component | Version constraint | Notes |
|---|---|---|
| Python | `>=3.10,<3.13` | `videocaptioner` 1.4.1 requirement; 3.12 recommended |
| `videocaptioner` | pin the exact version installed (`videocaptioner --version`) | record in `versions.lock` per run |
| FFmpeg | any recent build with `ffprobe` | required for synthesis and all verification gates |
| LLM translator backend | record `api_base` + `model` from `config show` | e.g. DeepSeek `deepseek-chat` — record whichever you actually configure |

Unlike tutorial #2, there is no single upstream commit hash to pin — pin the
package version and record it in every run's evidence, same spirit as
tutorial #2's `VERSIONS.lock`.

---

## 6. Definition of Done

- [ ] Gates T1-T4 all PASS (mechanical)
- [ ] Gate T5 reviewed by the Bilingual Caption QA Specialist, no unresolved flags
- [ ] `videocaptioner config show` evidence captured proving the intended translator ran (no silent fallback)
- [ ] Output video's resolution + duration verified identical to source via `ffprobe`
- [ ] At least one rendered frame visually inspected for caption legibility and placement
- [ ] Source video checked for pre-existing burned-in captions *before* any "overlap" is diagnosed as a bug
- [ ] Bilingual (EN + 简体中文) install guide and tutorial manual shipped
- [ ] Windows install path fully detailed, step by step; macOS/Linux paths stated (need not be as exhaustively tested)

If any line fails, the tutorial is not finished. No "mostly done" — same rule
as tutorial #2.

---

## 7. Known risks

| Risk | Mitigation |
|---|---|
| Reader assumes `✓ Done` means the right translator ran | Gate T2 makes provenance-checking a named, mandatory step |
| Reader collapses Gate T4 and T5 into one check (the circularity pitfall, § 4) | Called out explicitly, with the worked example from the pilot run |
| Windows PowerShell mangles `--style-override` JSON silently (real pitfall hit while building the pilot for this tutorial) | Documented verbatim in `starter/INSTALL.md` and the troubleshooting section, with the exact backslash-escaping fix |
| Source video has pre-existing burned-in captions, reader misdiagnoses it as a videocaptioner bug | Dedicated troubleshooting section: check 2-3 source frames before assuming any overlap is the tool's fault |
| LLM translation is non-deterministic run-to-run | Stated as an explicit, honest out-of-scope item (§ 1) rather than silently claimed as reproducible |

---

*Licence: prose CC BY 4.0, code Apache-2.0 — Copyright 2026 Prof. Yi-Kuen Lee.*

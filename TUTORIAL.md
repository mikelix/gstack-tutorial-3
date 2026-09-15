# gstack Tutorial #3 — English → Chinese Video Captioning, Verified

**What you will be able to do afterwards:** take any English-speaking video
clip and produce a version with clean, correctly-positioned Chinese
subtitles burned in — and have concrete evidence the output is right, rather
than having watched it once and liked the look of it.

**Time:** 2-4 hours in the no-surprises case, 2.5-7 hours honestly (see
[`reviews/02-spec.md`](reviews/02-spec.md) for why the range is wide).

**Prerequisites:** a computer running Windows 11, macOS, or Linux; an
English-speaking video clip; and a decision about translation access that
Part 2 walks you through.

中文版：[`TUTORIAL.zh.md`](TUTORIAL.zh.md)

---

## Part 0 — The mental model

### 0.1 What the pipeline actually is

```
  your .mp4  ──► [transcribe] ──►  English .srt
                                        │
                                   [you read it]      ← do not skip
                                        │
                                        ▼
                                  corrected .srt
                                        │
                                   [translate]
                                        ▼
                                  Chinese .srt
                                        │
                                   [synthesize]
                                        ▼
                              captioned .mp4  ──► [verify: 5 gates]
```

Four commands, one human read-through, and a verification chain. The
commands are the easy part. **The tutorial is about the verification.**

### 0.2 Why verification is the subject

Every stage of this pipeline can fail while reporting success:

| Stage | How it fails quietly |
|---|---|
| Transcribe | ASR mishears a word and writes something plausible |
| Translate | The service rate-limits, swallows the error, and returns your **English** as the "translation" — exit code 0, cheerful success message |
| Synthesize | Captions render off-frame, or overlap text already burned into the source |

The middle row is not hypothetical. It happened while building this
tutorial, and it defeated four of the five gates that existed at the time.
See [`reviews/04-qa-report.md`](reviews/04-qa-report.md), Finding 1.

> **The one sentence to carry through this whole tutorial:**
> **`✓ Done` is a string. The output file is the evidence.**

This is tutorial #2's lesson (`"PASS" is a string, the log is the evidence`)
in a different domain. The pattern generalizes; that is why it is worth
learning on an easy subject before you need it on a hard one.

### 0.3 The five gates

| Gate | Checks | Mechanical? |
|---|---|---|
| **T1** | Transcription produced segments | Yes |
| **T2** | The translator you asked for is the one that ran | Yes |
| **T3** | No segments dropped or merged in translation | Yes |
| **T3b** | Translation *actually happened* (not English passthrough) | Yes |
| **T4** | Output video matches source resolution and duration exactly | Yes |
| **T5** | The Chinese is a faithful, natural translation | **No — human/agent judgment** |

T1-T4 run as code: [`starter/scripts/run_gates.py`](starter/scripts/run_gates.py).
T5 is a procedure a bilingual reviewer follows:
[`docs/expertise_division.md`](docs/expertise_division.md) § 4.

### 0.4 Why one gate cannot be automated

gstack's process roles can count segments, diff durations, and grep a config
file. **None of them can read Chinese and judge whether it carries the
meaning of the English.** That is the single expertise gap in this project,
and Gate T5 exists to close it deliberately rather than pretend it isn't
there.

Tutorial #2 called this a **two-key system** (process authority vs. physics
authority). This tutorial is a lighter version: one domain reviewer, whose
veto fires on exactly one gate. Full contract:
[`docs/expertise_division.md`](docs/expertise_division.md).

### 0.5 The circularity trap (read before you invent your own check)

Suppose you want to verify the translation. A tempting idea: OCR the
burned-in captions from the finished video, and compare that text to the
`.srt` you used to make it.

**That check is worthless for translation fidelity.** It compares the output
to itself. It proves synthesis didn't corrupt the text (which Gate T4
already covers) and says nothing about whether the Chinese is a correct
translation of the English audio.

`run_gates.py` refuses this explicitly — pass `--ocr-check` and it exits
with code **2 (VOID)**, not 0, not 1. VOID has its own exit code so that
"the gate passed" and "the gate was meaningless" can never print the same
thing.

This is tutorial #2's LVS circularity lesson, transplanted. If you learn one
transferable idea from this tutorial, make it this one.

### Checkpoint 0

- [ ] I can name the four pipeline stages without looking
- [ ] I can state why `✓ Done` is not evidence
- [ ] I can explain why OCR-vs-own-srt is a circular check
- [ ] I know which single gate is not mechanical, and why

---

## Part 1 — Install

Full step-by-step, all three platforms:
**[`starter/INSTALL.md`](starter/INSTALL.md)**

Summary of what you are installing:

| Component | Constraint | Why |
|---|---|---|
| Python | **>= 3.10, < 3.13** | `videocaptioner` requirement. 3.13 is not supported; check before installing. |
| FFmpeg (`ffmpeg` + `ffprobe`) | any recent build | Audio extraction, caption burn-in, and every verification gate |
| `videocaptioner` | `pip install videocaptioner` | The pipeline itself |

Then:

```bash
videocaptioner --version
videocaptioner doctor
```

`doctor` checks Python, FFmpeg, and your config in one shot. A `WARN` about
`dubbing.api_key` is expected and harmless — dubbing is out of scope here.

> **Windows readers:** `starter/INSTALL.md` § 6 documents a PowerShell
> quoting trap that will bite you in Part 5 if you skip it. Read it now, not
> when the error appears. It is the single highest-value paragraph in the
> install guide.

### Checkpoint 1

- [ ] `videocaptioner --version` prints a version
- [ ] `videocaptioner doctor` shows `OK` for python, ffmpeg, ffprobe
- [ ] I ran all three checks from a **freshly opened** terminal
- [ ] (Windows) I have read INSTALL.md § 6 about quote-stripping

---

## Part 2 — Choose your translator (do not skip, do not copy mine)

This is the part most likely to differ between you and every other reader.

**Read: [`docs/choosing_a_translator.md`](docs/choosing_a_translator.md).**

The short version:

| Option | Cost | Key needed | EN→ZH quality |
|---|---|---|---|
| `llm` | Paid, ~cents per hour of speech | Yes | Best — context-aware |
| `bing` | Free | No | Mechanical (and currently broken upstream — see the doc) |
| `google` | Free | No | Mechanical (and can silently pass English through) |

Three things that surprise people:

1. **`--translator` defaults to `bing`**, not `llm`. Omit the flag and you
   silently get Bing. Every command below names it explicitly.
2. **Free translator still needs an LLM key** unless you also pass
   `--no-optimize --no-split` — those two steps are LLM-powered regardless
   of your translator choice.
3. **Your access is not my access.** The pilot used DeepSeek because it is
   reachable from Hong Kong and cheap. If you are elsewhere, behind a
   firewall, on an institutional OpenAI allocation, or have no budget at all,
   the right answer differs. The decision guide is keyed to your situation.

### Probe your access before committing to a long clip

Make a two-segment `probe.srt` and translate it:

```bash
videocaptioner subtitle probe.srt --translator llm \
    --target-language zh-Hans --layout target-only -o probe_out.srt
```

Then **open `probe_out.srt` and look at it**. Chinese text means you are
good. A loud error means try another option. **English text with a `✓ Done`
message means silent passthrough — that translator is not working for you,
regardless of what it claims.**

Two minutes here saves an hour later.

### Checkpoint 2

- [ ] I chose a translator based on *my* access, not the tutorial's default
- [ ] I ran the probe and **visually confirmed** Chinese in the output
- [ ] I recorded my choice (and `api_base`/`model`) in `starter/versions.lock`

---

## Part 3 — Phase 1-2: Scope and spec (`/plan-ceo-review`, `/spec`)

Before touching a video, lock what "done" means.

Worked examples shipped with this tutorial, both real runs on this repo:
- [`reviews/01-ceo-review.md`](reviews/01-ceo-review.md) — found three
  blocking issues in this tutorial's own plan, verdict REVISE, upgraded to
  PASS only after fixes
- [`reviews/02-spec.md`](reviews/02-spec.md) — W1-W10 breakdown, and it
  **raised** the CEO's time estimate rather than silently accepting it

Two properties worth copying:

1. **Every work item names the gate that judges it.** An item no gate can
   judge is a wish, not a task.
2. **Questions the role cannot answer are marked "referred", not guessed.**
   Both reviews do this. It is the defer clause working.

### Checkpoint 3

- [ ] My scope names what is deliberately **out**, not just what is in
- [ ] Every work item names its gate
- [ ] Anything needing bilingual judgment is referred, not guessed

---

## Part 4 — Phase 3: Transcribe and correct

### 4.1 Transcribe

```bash
videocaptioner transcribe myclip.mp4 --asr bijian --language en -o myclip.srt
```

`bijian` is free, needs no setup, and handles English well. For other source
languages use `--asr whisper-api` with `--whisper-api-key`.

Note the segment count in the output — you will check it at every later step.

### 4.2 Read the transcript (the step everyone skips)

**Open `myclip.srt` and read it.** ASR makes small errors that are two-minute
fixes in English and become translation-quality problems if you let them
through.

Real examples from this tutorial's pilot run, all three caught at this step:

| ASR wrote | Should be |
|---|---|
| `ai` | `AI` |
| `home humanoid robots` | `humanoid robots` |
| `neural netells me` | `neural network tells me` |

Edit the text lines only. **Do not touch the segment indices or timestamps** —
Gate T3 checks that the count is unchanged.

### Checkpoint 4

- [ ] Transcript exists, segment count noted
- [ ] I read the whole thing and fixed ASR errors
- [ ] Segment count and timestamps are unchanged after my edits

---

## Part 5 — Phase 3 continued: Translate and synthesize

### 5.1 Check the source for pre-existing burned-in captions

Do this *before* translating — it decides whether you need caption
positioning work at all.

```bash
ffmpeg -y -ss 30 -i myclip.mp4 -frames:v 1 -update 1 frame30.png
ffmpeg -y -ss 60 -i myclip.mp4 -frames:v 1 -update 1 frame60.png
```

Grab 2-3 frames spread across the clip (a caption may only appear sometimes)
and look at them.

**If you find burned-in text:** it is fused into the pixels. No subtitle tool
can see or remove it — to `ffmpeg` it is indistinguishable from someone's
face. Your options are: find a clean source export, use AI video inpainting
(complex, often blurry), crop that region, or **position your Chinese
captions clear of it** (§ 5.3). The pilot's first clip had this; the second
did not.

### 5.2 Translate, Chinese-only

```bash
videocaptioner subtitle myclip.srt --translator llm \
    --target-language zh-Hans --layout target-only -o myclip_zh.srt
```

`--layout target-only` gives Chinese with no English line. Go straight here;
the default (`target-above`) produces a bilingual file, and discovering you
wanted Chinese-only *after* burning it in means re-running synthesis.

Then immediately:

```bash
videocaptioner config show     # Gate T2 — confirm which service actually ran
```

Run this right after the translate command you care about. It reports
*current* config state, not per-invocation history, so batching several
translations before checking makes it useless (see
[`reviews/03-eng-review.md`](reviews/03-eng-review.md), non-blocking notes).

### 5.3 Position the captions (only if § 5.1 found a conflict)

```bash
videocaptioner style     # list presets and their fields
```

Fields: `font_name`, `font_size`, `primary_color`, `outline_color`,
`outline_width`, `bold`, `spacing`, `margin_bottom`. Raise `margin_bottom` to
lift Chinese captions clear of existing bottom-of-frame text.

### 5.4 Synthesize

```bash
videocaptioner synthesize myclip.mp4 -s myclip_zh.srt \
    --subtitle-mode hard --style default -o myclip_captioned_v1.mp4
```

`hard` burns captions into the frames; `soft` adds a toggleable track
instead. Version-suffix the output (`_v1`, `_v2`) so you can compare
attempts rather than overwrite them.

**To change style without making a preset** (e.g. bigger text — the default
42 can read small on a 1080-wide frame; 54-56 works well):

```bash
videocaptioner synthesize myclip.mp4 -s myclip_zh.srt --subtitle-mode hard \
    --style default --style-override '{"font_size":56}' -o myclip_captioned_v2.mp4
```

> **Windows PowerShell users — this will fail as written.** PowerShell strips
> the double quotes before the argument reaches the program, and you get
> `Invalid --style-override JSON: Expecting property name enclosed in double
> quotes` even though the command looks correct on screen. Backslash-escape
> every quote inside a single-quoted string:
> ```powershell
> --style-override '{\"font_size\":56}'
> ```
> Verify with: `python -c "import sys; print(sys.argv)" '{\"font_size\":56}'`
> — it should print `['{"font_size":56}']`. Full explanation:
> [`starter/INSTALL.md`](starter/INSTALL.md) § 6.

### Checkpoint 5

- [ ] I checked 2-3 source frames for pre-existing captions
- [ ] Translation used `--layout target-only` and my chosen translator
- [ ] I ran `config show` immediately after translating
- [ ] Output video is version-suffixed

---

## Part 6 — Phase 4: Verify (the actual point of this tutorial)

### 6.1 Run the mechanical gates

```bash
python starter/scripts/run_gates.py \
    --source-video   myclip.mp4 \
    --source-srt     myclip.srt \
    --target-srt     myclip_zh.srt \
    --output-video   myclip_captioned_v2.mp4 \
    --translator     llm \
    --target-language zh-Hans
```

Expected on a good run:

```
T1 PASS — myclip.srt: 32 segments
T2 PASS — translate.service = llm
T3 PASS — 32 segments in both source and target
T3b PASS — target is genuinely translated, not source passthrough
T4 PASS — 1080x596, 89.131s (source) vs 89.131s (output)
T5 NOT AUTO-VERIFIED — run docs/expertise_division.md section 4 by hand
```

**Exit codes:**

| Code | Meaning |
|---|---|
| `0` | T1-T4 PASS |
| `1` | A mechanical gate FAILED |
| `2` | **VOID** — a check was self-referential and was refused |
| `3` | Environment error (tool or file missing) |

Make any automation fail on `!= 0`, and alert *separately* on `== 2`. A VOID
run is not a failure to retry — it means the check you attempted could not
prove what you wanted it to prove.

### 6.2 Run Gate T5 by hand

The script prints `T5 NOT AUTO-VERIFIED` and means it. Follow
[`docs/expertise_division.md`](docs/expertise_division.md) § 4:

**Inputs:** the English `.srt` and the Chinese `.srt` — **never the video**.
**Sample:** segments 1-5, a block at ~50%, and the last 5.
**Per segment, four questions:** meaning-preserving? natural rather than
literal? nothing hallucinated or dropped? proper nouns and idioms right?

Verdict is PASS, or **PASS-WITH-FLAG** with the segment named. A flagged run
is not done until a human resolves each flag.

### 6.3 Look at a frame

Gates prove the file is structurally right. Only your eyes prove it is
*legible*.

```bash
ffmpeg -y -ss 30 -i myclip_captioned_v2.mp4 -frames:v 1 -update 1 check30.png
```

Check: text readable against the background, not clipped at frame edges, not
overlapping burned-in source text, font size comfortable.

### Checkpoint 6

- [ ] `run_gates.py` exits 0
- [ ] Gate T5 run against the **`.srt` pair**, not the video
- [ ] Every T5 flag resolved in writing
- [ ] At least one output frame visually inspected

---

## Part 7 — Phase 5: Ship

- Evidence bundle: gate output, `config show` excerpt, filled-in
  `starter/versions.lock`, and the frame you inspected
- Release notes state **known gaps**, not just features
- Regenerate any derived documents from Markdown; never hand-edit generated
  binaries

### Checkpoint 7

- [ ] Evidence bundle assembled
- [ ] Known gaps stated in writing
- [ ] `versions.lock` filled in with versions, provider, model, and run date

---

## Part 8 — Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `--style-override` JSON error that looks correct on screen | PowerShell stripped the quotes | Backslash-escape: `'{\"font_size\":56}'` |
| Translation "succeeded" but output is English | Free translator swallowed a rate-limit error | Gate T3b catches this. Switch translators — `docs/choosing_a_translator.md` |
| `Failed to init Bing session: 404` | Upstream endpoint moved | Use `llm` or `google`; see the translator guide |
| Gate T1 counts one fewer segment than expected | UTF-8 BOM on the first line | Fixed in `run_gates.py` (reads `utf-8-sig`). If you wrote your own tooling, read with `utf-8-sig` |
| Chinese captions overlap existing on-screen text | Source has burned-in captions | § 5.1 — raise `margin_bottom`; the source text cannot be removed |
| `videocaptioner: command not found` after successful `pip install` | Scripts dir not on PATH | `python -c "import sysconfig; print(sysconfig.get_path('scripts'))"`, add to PATH |
| Chinese looks garbled in PowerShell | Console codepage, not the file | Open in a UTF-8-aware editor; the file is fine |
| `pip install` fails building a dependency | Python outside `>=3.10,<3.13` | Install 3.12; don't fight a 3.13 interpreter |

---

## Part 9 — The disciplines worth keeping

Five habits that transfer to any pipeline, not just this one.

1. **Check the output, not the exit code.** Every failure in this tutorial's
   pitfall ledger reported success at least once.
2. **Never verify an artifact against itself.** OCR-vs-own-srt, LVS against
   a netlist derived from the GDS under test — same mistake, different field.
3. **Give "meaningless" its own signal.** VOID has a distinct exit code so it
   can never be mistaken for PASS.
4. **Name the gap you cannot close.** Gate T5 is not automated, and the docs
   say so plainly rather than implying full coverage.
5. **The reader's environment is not yours.** Part 2 exists because the first
   draft handed down the author's API setup as a universal rule.

---

## Appendix A — Command reference

```bash
# Install check
videocaptioner --version
videocaptioner doctor
videocaptioner config show

# Configure an LLM translator
videocaptioner config set llm.api_key  "sk-..."
videocaptioner config set llm.api_base "https://api.deepseek.com"
videocaptioner config set llm.model    "deepseek-chat"

# Pipeline
videocaptioner transcribe clip.mp4 --asr bijian --language en -o clip.srt
videocaptioner subtitle clip.srt --translator llm --target-language zh-Hans \
    --layout target-only -o clip_zh.srt
videocaptioner synthesize clip.mp4 -s clip_zh.srt --subtitle-mode hard \
    --style default -o clip_captioned_v1.mp4

# Verify
python starter/scripts/run_gates.py --source-video clip.mp4 \
    --source-srt clip.srt --target-srt clip_zh.srt \
    --output-video clip_captioned_v1.mp4 --translator llm

# Frame grab
ffmpeg -y -ss 30 -i clip.mp4 -frames:v 1 -update 1 frame.png
```

## Appendix B — Glossary

| Term | Meaning |
|---|---|
| **ASR** | Automatic Speech Recognition — audio to text |
| **SRT** | SubRip subtitle format: index, timestamp range, text |
| **Hard subtitles** | Burned into the video pixels; cannot be turned off |
| **Soft subtitles** | A separate track the player can toggle |
| **Passthrough** | Translator returns the source text unchanged while claiming success |
| **VOID** | A check that ran but proved nothing — distinct from pass or fail |
| **Circular check** | Verifying an artifact against something derived from itself |
| **BCP 47** | Language tag standard. `zh-Hans` = Simplified Chinese |

## Appendix C — Definition of Done

- [ ] Gates T1-T4 PASS (`run_gates.py` exits 0)
- [ ] Gate T5 reviewed, no unresolved flags
- [ ] `config show` evidence captured proving the intended translator ran
- [ ] Output resolution and duration verified identical to source
- [ ] At least one frame visually inspected
- [ ] Source checked for pre-existing burned-in captions
- [ ] `versions.lock` filled in
- [ ] Known gaps stated in writing

Anything less is a draft.

---

*Licence: prose CC BY 4.0, code Apache-2.0 — Copyright 2026 Prof. Yi-Kuen Lee.*

# starter/sample/ — a real, tiny, rights-clear worked example

A ~12-second clip run through the *actual* documented pipeline, so a reader
can see real results — and run the actual verification gates — in under a
minute, without waiting to install anything first.

## Why this exists, and why it isn't a real interview clip

The pilot runs behind this tutorial (`reviews/03-eng-review.md`,
`reviews/04-qa-report.md`) used a real downloaded podcast/interview clip.
That clip's rights are not the author's to redistribute, so committing even
a short excerpt of it into this public, CC-BY-licensed repository would have
been a real problem, not a hypothetical one — the source has no creator
metadata pointing back to this project, and its baked-in caption style is a
live-recording artifact from third-party recording software, not something
produced here.

**This sample is purpose-built instead**, with zero rights ambiguity:

- **Video:** a solid navy background (`#143552`, this deck's own palette)
  with white/cyan text overlay, generated with `ffmpeg`'s `drawtext` filter.
  No footage of any person.
- **Audio:** English narration generated with the Windows built-in offline
  text-to-speech engine (`System.Speech.Synthesis`, "Microsoft Zira
  Desktop" voice) — no third-party API, no recording of any real person's
  voice.
- **Script (verbatim):** "Hello, this is a short sample clip for gstack
  Tutorial three. We test the pipeline: transcribe, translate, and burn in
  Chinese captions."

## How it was built (reproducible)

```bash
# 1. TTS narration (PowerShell, Windows built-in, offline)
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice("Microsoft Zira Desktop")
$synth.SetOutputToWaveFile("sample_audio.wav")
$synth.Speak("Hello, this is a short sample clip for gstack Tutorial three. " +
             "We test the pipeline: transcribe, translate, and burn in Chinese captions.")

# 2. Branded background video (matches this deck's navy/cyan palette)
ffmpeg -f lavfi -i "color=c=0x143552:s=1080x596:d=11.6" -vf "drawtext=...:text='GSTACK TUTORIAL NO. 3'..." bg_only.mp4

# 3. Mux narration onto the background
ffmpeg -i bg_only.mp4 -i sample_audio.wav -c:v copy -c:a aac -shortest sample_clip.mp4

# 4. The actual documented pipeline (Parts 4-5 of TUTORIAL.md), unchanged
videocaptioner transcribe sample_clip.mp4 --asr bijian --language en -o sample_clip.srt
#   -> hand-corrected one real ASR error: "gestack" -> "gstack" (see sample_clip.srt)
videocaptioner subtitle sample_clip.srt --translator llm --target-language zh-Hans \
    --layout target-only -o sample_clip_zh.srt
videocaptioner synthesize sample_clip.mp4 -s sample_clip_zh.srt \
    --subtitle-mode hard --style default -o sample_clip_captioned.mp4
```

## Try the gate chain right now, before installing anything

`run_gates.py` only needs Python and `ffmpeg` — not `videocaptioner` itself
— so you can verify a real result immediately:

```bash
python ../scripts/run_gates.py \
    --source-video sample_clip.mp4 --source-srt sample_clip.srt \
    --target-srt sample_clip_zh.srt --output-video sample_clip_captioned.mp4 \
    --translator llm --target-language zh-Hans
```

Expected: `T1 PASS`, `T2 PASS`, `T3 PASS`, `T3b PASS`, `T4 PASS`, and a
reminder that Gate T5 is never automated — run it by hand against
`sample_clip.srt` / `sample_clip_zh.srt` per `docs/expertise_division.md` §4.

## Files

| File | What it is |
|---|---|
| `sample_clip.mp4` | The synthetic source clip (video + TTS narration) |
| `sample_clip_preview.png` | A frame of the source, before captioning |
| `sample_clip.srt` | English transcript, hand-corrected (one real ASR error fixed) |
| `sample_clip_zh.srt` | Chinese translation, target-only, via `llm` |
| `sample_clip_captioned.mp4` | The final Chinese-captioned output |
| `sample_clip_captioned_preview.png` | A frame of the captioned output |

## Licence

Same as the rest of this repository — CC BY 4.0 (prose/audio/video),
Apache-2.0 (code) — Copyright 2026 Prof. Yi-Kuen Lee. Unlike the pilot
clips referenced in the reviews, every byte of this sample was generated
for this project and is genuinely covered by that licence.

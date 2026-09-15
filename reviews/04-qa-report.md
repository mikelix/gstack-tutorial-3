# Review 04 — QA (`/qa-only`)

```
Date:            2026-09-15
Reviewer role:   QA
Command:         /qa-only
Scope reviewed:  translator options (llm / bing / google); gate chain coverage
Verdict:         REVISE → PASS after adding Gate T3b
```

> **Origin.** This review was not scheduled. It happened because the project
> owner, reviewing `01-ceo-review.md` and `02-spec.md`, observed that both
> documents told the reader to use `--translator llm` and never fall back to
> Bing or Google — which was the author's own setup restated as a rule, not
> guidance a student with different machine, network, or API access could
> follow. Probing that question found a defect in the gate chain itself.

---

## Finding 1 (critical) — `google` silently emits untranslated source and exits 0

**Severity: critical.** A reader can ship an English-captioned video
believing the verification chain approved it.

**Reproduction.** A 2-segment English `probe.srt`, `videocaptioner` 1.4.2,
Windows 11, Hong Kong network, 2026-09-15:

```
videocaptioner subtitle probe.srt --translator google \
    --target-language zh-Hans --layout target-only -o probe_google.srt
```

Observed: two `429 Too Many Requests` errors logged to stderr, then:

```
✓ Done -> probe_google.srt (2 segments)
exit code: 0
```

`probe_google.srt` contained the **original English**, unchanged. The tool
swallowed the rate-limit failure, passed the source through as the
"translation", reported success, and exited clean.

**Why this defeated the gate chain as designed:**

| Gate | Verdict on the passthrough file | Why it missed |
|---|---|---|
| T1 transcription completeness | PASS | Source `.srt` was fine |
| T2 translator provenance | PASS | The service genuinely *was* `google` |
| T3 segment parity | PASS | 2 segments in, 2 segments out |
| T4 synthesis fidelity | PASS | Video would be structurally perfect, just with English on it |

Four gates, all green, output wrong. **The chain verified everything except
whether translation occurred.**

**Fix.** Added **Gate T3b** to `starter/scripts/run_gates.py`: for a `zh-*`
target it requires Han characters in ≥80% of segments, and independently
flags any segment byte-identical to its source (catching partial passthrough
where only some batches failed). Verified both directions:

```
# Real DeepSeek-translated file (32 segments)
T3b PASS — target is genuinely translated, not source passthrough   → exit 0

# The google passthrough file
T3b FAIL: target language is 'zh-Hans' but probe_google.srt contains no Han
characters at all — the translator almost certainly passed the source through
untranslated ...                                                     → exit 1
```

---

## Finding 2 (high) — `bing`, the documented free default, is currently broken

```
Failed to init Bing session: 404 Client Error: Not Found for url:
https://edge.microsoft.com/translate/auth
exit code: 5
```

The upstream auth endpoint moved or was withdrawn. **This is the less
dangerous of the two free-translator failures** because it fails loudly —
no one ships a bad artifact from it, they just lose time. Documented in
`docs/choosing_a_translator.md` § 2 with the date and environment, and with
an explicit instruction for readers to re-test rather than trust the table.

---

## Finding 3 (high) — `--translator` defaults to `bing`, not `llm`

```
--translator {llm,bing,google}
        Translation service (default: bing)
```

Every draft document assumed `llm`. A reader who omits the flag gets Bing
silently — which, per Finding 2, currently fails outright, and per Finding 1
the other free option can fail invisibly. Fixed by naming the translator
explicitly in every command in the tutorial and stating the default in
`docs/choosing_a_translator.md` § 1.

---

## Finding 4 (medium) — free translation still needs an LLM key unless steps are disabled

`videocaptioner subtitle` runs Split → Optimize → Translate; the first two
are LLM-powered *regardless of `--translator`*. "Use the free translator"
therefore does not imply "no API key needed" — a keyless reader also needs
`--no-optimize --no-split`. Documented in `docs/choosing_a_translator.md` § 1.

---

## Finding 5 (medium) — BOM bug in our own gate script

`starter/scripts/run_gates.py` read `.srt` files with `encoding="utf-8"`.
A file saved by PowerShell's `Out-File -Encoding utf8` (or by many Windows
editors) carries a UTF-8 BOM, making the first segment's index line
`"﻿1"` — which fails `.isdigit()`, so **the first segment was silently
not counted**. Observed as `T1 PASS — probe.srt: 1 segments` on a 2-segment
file.

A gate that undercounts is worse than no gate: T3 parity could pass or fail
for the wrong reason. Fixed by reading with `utf-8-sig` throughout (strips
the BOM if present, harmless if not). Re-verified: now reports 2 segments.

**This one is self-inflicted and worth stating plainly** — the gate chain
had a defect in the same release where it was introduced, found only because
a test file happened to be written by PowerShell rather than by
`videocaptioner` itself. Test your gates with files from a *different*
producer than the one they normally consume.

---

## Decisions recorded

| # | Decision |
|---|---|
| Q1 | Gate T3b is mandatory, not optional, and is **never** skipped on a free translator. |
| Q2 | Translator choice is a taught decision with its own document (`docs/choosing_a_translator.md`), keyed to the reader's environment — not a rule inherited from the author's setup. |
| Q3 | Observed translator behavior is recorded **with date, version, and network location**, and readers are told to re-verify rather than trust the table. Availability is environmental and will drift. |
| Q4 | All `.srt` reads use `utf-8-sig`. Windows toolchains produce BOMs routinely. |

---

## What was NOT reviewed

- Whether `bing` works from other networks/regions — only one location
  tested. The 404 may or may not be global.
- Whether `google` passthrough is rate-limit-specific or happens on other
  failures too. Gate T3b catches the symptom regardless of cause, which is
  the point of checking output rather than trusting exit codes.
- Gate T5 (translation fidelity) was still not formally run — it remains the
  one gate with no mechanical backing, as stated since `02-spec.md`.
- Non-Chinese target languages: T3b's Han-character check only applies to
  `zh-*` targets. The byte-identity check is language-agnostic and still
  applies, but a `zh`-specific gate is a stated limitation.

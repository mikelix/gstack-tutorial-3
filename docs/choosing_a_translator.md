# Choosing Your Translator — Read This Before Phase 2

**Why this page exists.** Earlier drafts of this tutorial simply told you
"use `--translator llm`, never fall back to Bing or Google." That was the
author's setup being handed down as a rule. It is not a rule you can follow
blindly, because **which translators are actually available to you depends
on your machine, your network, your country, and whether you have a paid API
key** — and those differ for every postgraduate student reading this.

This page helps you decide. It also documents a failure mode found while
testing these options that the earlier gate chain would not have caught.

---

## 1. The three options, as the tool actually presents them

`videocaptioner subtitle --translator {llm,bing,google}`

| Option | Cost | Needs API key | Quality for EN→ZH |
|---|---|---|---|
| `llm` | Paid (per token) | **Yes** | Best — context-aware, handles idiom and register |
| `bing` | Free | No | Mechanical, segment-by-segment |
| `google` | Free | No | Mechanical, segment-by-segment |

### The default is NOT what this tutorial assumes

```
--translator {llm,bing,google}
        Translation service (default: bing)
```

**`--translator` defaults to `bing`, not `llm`.** If you omit the flag, you
silently get Bing. Every command in this tutorial names the translator
explicitly for exactly this reason. Do not drop the flag to save typing.

### A second trap: `optimize` and `split` are LLM steps too

`videocaptioner subtitle` runs up to three steps: **Split** (re-segment by
semantic boundaries), **Optimize** (fix ASR errors and punctuation), and
**Translate**. The first two are LLM-powered *regardless of which translator
you choose*. So "I'll use the free Bing translator" does not mean "I need no
API key at all" — you also need `--no-optimize --no-split`, or an LLM key
for those steps. Decide this deliberately, don't discover it mid-run.

---

## 2. What we actually observed when testing the free options

Tested 2026-09-15, Windows 11, from Hong Kong, `videocaptioner` 1.4.2.
**Your results may differ — that is the whole point of this page.** Re-run
the check in § 4 yourself rather than trusting this table.

| Translator | Result on our test | Notes |
|---|---|---|
| `bing` | **Failed outright** | `Failed to init Bing session: 404 Client Error: Not Found for url: https://edge.microsoft.com/translate/auth` — the upstream auth endpoint moved or was withdrawn. Exit code 5. At least this failure is loud. |
| `google` | **Silently produced untranslated English** | Hit `429 Too Many Requests`, logged the error, then emitted the original English as the "translation" and **exited 0** with `✓ Done -> file.srt (2 segments)`. |
| `llm` (DeepSeek) | Worked | Fluent, natural Chinese across a 32-segment and a 1086-segment clip. |

### The `google` result is the important one

Read that row again. The command **reported success**. Segment count was
correct. The output file existed and was well-formed. The only thing wrong
with it was that it contained no Chinese.

A student who trusted `✓ Done` would burn English captions into their video
and ship it. And the gate chain as originally designed **would not have
caught it**:

- Gate T2 (translator provenance) — PASS. The service really was `google`.
- Gate T3 (segment parity) — PASS. Source and target both had 2 segments.
- Gate T4 (synthesis fidelity) — PASS. The video was fine; it just had the
  wrong words on it.

This is why **Gate T3b** now exists (`starter/scripts/run_gates.py`): it
checks that the target file actually contains Han characters and that no
segment is byte-identical to its source. It was added *because* of this
finding, not anticipated in advance. See `reviews/04-qa-report.md`.

> **The general lesson, which outlives this tool:** a free service that
> silently degrades is more dangerous than one that fails loudly. Bing's
> 404 wastes your afternoon. Google's 429-then-passthrough could waste your
> submission.

---

## 3. Decision guide

Work down this list and stop at the first row that describes you.

| If you… | Use | Because |
|---|---|---|
| Have (or can get) an API key for any OpenAI-compatible provider | **`llm`** | Best quality by a wide margin for EN→ZH, and it fails loudly rather than silently. This is what the tutorial's pilot runs used. |
| Are in mainland China or behind a restrictive firewall | **`llm` with a domestically reachable provider** (DeepSeek, Moonshot, Zhipu, Qwen — all OpenAI-compatible) | Google and Bing endpoints are frequently unreachable; a domestic LLM endpoint usually is not. DeepSeek is what this tutorial pinned. |
| Have no budget at all and cannot obtain any key | `google` or `bing`, **plus `--no-optimize --no-split`**, **plus mandatory Gate T3b** | Free, but see § 2 — verify the output actually contains Chinese before trusting it. Never skip T3b on a free translator. |
| Are on a university/institutional account with an OpenAI or Azure allocation | **`llm`** pointed at that endpoint | Already paid for. Use `--api-base` to point at your institution's gateway. |
| Are just smoke-testing the pipeline mechanics on a 30-second clip | `google` is acceptable | Quality does not matter yet; you are testing plumbing. Switch to `llm` before any real output. |

### Cost, so the paid option is a real choice and not a vague worry

The pilot's 41-minute clip was 1086 segments. At DeepSeek's pricing this is
a fraction of a US dollar — translation of an hour of speech costs less than
a cup of coffee. **For most students the real barrier is obtaining a key and
a payment method, not the per-run cost.** Budget your effort accordingly:
the setup is the hard part, the usage is cheap.

---

## 4. Verify your own access before Phase 2 (do not skip)

Run this on a tiny throwaway file rather than discovering the problem on a
41-minute clip. Create `probe.srt`:

```
1
00:00:00,000 --> 00:00:02,000
hello this is a short test

2
00:00:02,000 --> 00:00:04,000
of the translation pipeline
```

Then try your intended translator:

```bash
videocaptioner subtitle probe.srt --translator llm \
    --target-language zh-Hans --layout target-only -o probe_out.srt
```

**Now actually open `probe_out.srt` and look at it.** Three outcomes:

1. **Chinese text** → your translator works. Record which one in
   `starter/versions.lock` and proceed.
2. **A loud error** (non-zero exit, a traceback, a 404) → that translator is
   unavailable to you. Try the next row of § 3's table.
3. **English text, with `✓ Done`** → silent passthrough. The translator is
   *not* working despite claiming success. Do not proceed; pick another.

Outcome 3 is the one that costs people a day. Look at the file.

---

## 5. Record your decision

Whichever you choose, write it into `starter/versions.lock` (copy from
`versions.lock.template`) along with the `api_base` and `model` if you used
`llm`. Two reasons: Gate T2 checks it, and a future reader of your work
(including future you) needs to know what produced a given translation.
LLM providers change model behavior over time even at a fixed model name,
which is why the template also asks for the run date.

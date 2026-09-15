# The Expertise Gap and the Authority Contract

**Why gstack process roles cannot certify translation quality — and what
Gate T5 concretely does about it.**

Part of `gstack-tutorial-3`. Written to resolve Blocking issue B1 in
[`../reviews/01-ceo-review.md`](../reviews/01-ceo-review.md): a domain agent
named but not operationalized is not a gate, it is a hope. This file is the
operationalization.

---

## 1. The claim in one paragraph

The five gstack roles are process experts and domain generalists. They can
run `ffprobe`, diff a segment count, and grep a config file for which
translator service actually ran — all of Gates T1-T4 are mechanical and
gstack owns them outright. **None of them can read Chinese and judge whether
it faithfully carries the meaning of the English source.** That is the one
expertise gap this tutorial has, and Gate T5 exists to close it with a
named, followable procedure — not an appeal to an undefined "specialist."

---

## 2. What each layer actually knows

| Layer | Knows well | Does NOT know |
|---|---|---|
| gstack orchestration | Segment counting, exit-code checking, `ffprobe` diffing, packaging, release | Whether 你是想，你想用钱来换取商品和服务？ is a faithful, natural rendering of "Are you want, you want money for goods and services" |
| Bilingual Caption QA Specialist (Gate T5 procedure, § 4) | Meaning-preservation, register/naturalness, hallucination and drop detection | Sprint structure, packaging, release mechanics |
| The toolchain (Layer 3) | Neutral referee for T1-T4: transcription completed, translator service matches, segment counts match, resolution/duration match | Nothing about meaning — it can prove the pixels and the file match; it cannot prove the *translation* is right |

---

## 3. The authority contract (RACI)

R = responsible, A = accountable, C = consulted, I = informed,
**X = not permitted to decide**

| Decision | AI CEO | AI PM | AI Eng | AI QC | AI DevOps | Bilingual QA | Human |
|---|---|---|---|---|---|---|---|
| Scope and positioning | A | R | C | I | I | C | approves |
| Which translator/API is configured | C | records | R | I | I | — | I |
| Segment-count / ffprobe verification (T1-T4) | X | X | R | **A** | X | — | I |
| Translation fidelity verdict (T5) | X | X | X | reports | X | **A** | I |
| Whether a flagged translation ships anyway | X | X | X | X | X | vets | **signs** |
| Caption style/position choices | C | C | R | I | I | — | approves |
| Release content and version | C | C | I | C | **A** | I | approves |

Read the **X** column first: gstack is not permitted to adjudicate a
translation-fidelity dispute on its own, the same discipline tutorial #2
applied to physics claims.

---

## 4. Gate T5, concretely — the procedure

This is the fix for B1. "The domain agent reviews it" now means: run this
checklist, against these inputs, producing this output.

**Inputs.** The original English `.srt` (post hand-correction, per
`PLAN.md` § 1) and the target Chinese `.srt` — **never** the burned-in video.
Comparing the video's rendered text back to the `.srt` used to synthesize it
only re-proves Gate T4 (synthesis didn't corrupt the text); it says nothing
about translation fidelity and is the exact circularity this tutorial's VOID
condition exists to catch.

**Sample.** Segments 1-5 (opening), a contiguous block from the ~50% mark,
and the last 5 segments (closing) — same sampling rule already used for
Gate T3's mechanical count check, reused here for the qualitative pass.

**Per sampled segment, answer four questions:**

1. **Meaning-preserving?** Does the Chinese say what the English said, not
   a plausible-sounding paraphrase that drifted?
2. **Natural, not literal?** Would a native speaker actually say it this
   way, or does it read as word-for-word machine translation?
3. **No hallucination or drop?** Nothing added that wasn't in the source;
   nothing meaningful silently dropped.
4. **Proper nouns / idioms correct?** Names, acronyms, and idioms rendered
   correctly, not transliterated nonsensically.

**Verdict per segment:** PASS, or FLAG with a one-line reason.

**Aggregate verdict:**
- Zero flags across the sample → Gate T5 **PASS**.
- One or more flags → **PASS-WITH-FLAG**. The overall pipeline is not
  Definition-of-Done until a human resolves each flag (accept as-is with a
  written reason, or re-translate that segment).

This is deliberately lightweight compared to tutorial #2's log-reading
discipline — there is no separate "log" beneath a translation the way there
is beneath an LVS run. The `.srt` pair **is** the evidence; reading it
carefully, side by side, is the entire procedure.

---

## 5. Two rules

1. **A translator's exit code is not evidence of which service ran.**
   `videocaptioner config show` after every translate command is mandatory
   (Gate T2) — carried over from this tutorial's own pilot lesson.
2. **Gate T5 never compares the output against itself.** See "Inputs"
   above. This is this tutorial's version of tutorial #2's LVS circularity
   trap, restated at the top of every QA pass, not buried in a footnote.

---

## 6. The defer clause (copy-paste)

### English

```text
CONSULT REQUIRED. Before asserting that a translation is accurate or
natural, run the Gate T5 procedure (docs/expertise_division.md §4) against
the English source and the Chinese target directly — never against the
burned-in video. If any sampled segment fails, report PASS-WITH-FLAG, not
PASS, and name the segment and the reason.
```

### 中文

```text
需先核验。在断言某段翻译准确或地道之前，请依照 Gate T5 流程
（docs/expertise_division.md §4）直接比对英文原文与中文译文——
绝不可比对已烧录字幕的视频画面。若抽样中任何一段未通过，
应报告为「PASS-WITH-FLAG」而非「PASS」，并注明具体段落与原因。
```

Attach to every `/plan-eng-review` and `/qa-only` prompt used in this
tutorial's Phases 3-4.

---

## 7. Checklist

- [ ] Every translate command's output is cross-checked with `config show` (Gate T2)
- [ ] Gate T5 was run against the `.srt` pair, never against the rendered video
- [ ] Every flagged segment has a written resolution before shipping
- [ ] No tolerance was relaxed (e.g. "close enough" translation) to turn a check green

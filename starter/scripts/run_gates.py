#!/usr/bin/env python3
"""Gates T1-T4 (mechanical) for gstack-tutorial-3, plus a mechanised guard
against the T5 circularity trap. See ../../docs/expertise_division.md and
../../PLAN.md section 4 for what each gate means and why VOID has its own
exit code.

Exit codes (mirrors gstack-tutorial-2's run_all.sh contract):
    0  Gates T1-T4 PASS. (T5 is never auto-verified here — see --ocr-check.)
    1  A mechanical gate (T1-T4) FAILED.
    2  VOID — a check was self-referential and was refused before running.
    3  Environment error (missing tool, missing file, bad arguments).

Stdlib only. No third-party dependencies, to match tutorial #2's own
"starter is a pointer, not a payload" principle (PLAN.md S1) — do not add
a requirements.txt for a script this small.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


class GateError(Exception):
    """Raised for a gate FAIL (exit 1). VOID and env errors exit directly."""


def _run(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError as e:
        print(f"ENV ERROR: command not found: {cmd[0]} ({e})", file=sys.stderr)
        sys.exit(3)
    if result.returncode != 0 and not result.stdout:
        print(f"ENV ERROR: {' '.join(cmd)} failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(3)
    return result.stdout


def count_srt_segments(path: Path) -> int:
    """An SRT segment is a block whose first non-blank line is a bare
    integer index, followed by a '-->' timestamp line. Counting index
    lines is more robust than counting blank-line-separated blocks alone
    (trailing whitespace / CRLF quirks vary across editors and tools)."""
    if not path.exists():
        print(f"ENV ERROR: srt file not found: {path}", file=sys.stderr)
        sys.exit(3)
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.isdigit() and i + 1 < len(lines) and "-->" in lines[i + 1]:
            count += 1
    return count


def gate_t1_transcription(source_srt: Path) -> int:
    """Gate T1 — transcription completeness. Output exists, segment count > 0."""
    n = count_srt_segments(source_srt)
    if n == 0:
        raise GateError(f"T1 FAIL: {source_srt} has 0 parseable segments")
    print(f"T1 PASS — {source_srt.name}: {n} segments")
    return n


def gate_t2_translator_provenance(expected_service: str) -> None:
    """Gate T2 — translator provenance. `videocaptioner config show` must
    report the translator you asked for, not a silent fallback."""
    out = _run(["videocaptioner", "config", "show"])
    m = re.search(r"^translate:\s*\n((?:^[ \t]+.*\n?)*)", out, re.MULTILINE)
    if not m:
        raise GateError("T2 FAIL: no 'translate:' block found in config show output")
    block = m.group(1)
    svc = re.search(r"service\s*=\s*(\S+)", block)
    if not svc:
        raise GateError("T2 FAIL: no 'service' field under 'translate:' block")
    actual = svc.group(1)
    if actual != expected_service:
        raise GateError(
            f"T2 FAIL: expected translator '{expected_service}', "
            f"config show reports '{actual}' — check for a silent fallback"
        )
    print(f"T2 PASS — translate.service = {actual}")


def gate_t3_segment_parity(source_srt: Path, target_srt: Path) -> None:
    """Gate T3 — segment parity. Target segment count must equal source."""
    n_src = count_srt_segments(source_srt)
    n_tgt = count_srt_segments(target_srt)
    if n_src != n_tgt:
        raise GateError(
            f"T3 FAIL: source has {n_src} segments, target has {n_tgt} "
            f"(dropped or merged lines during translation)"
        )
    print(f"T3 PASS — {n_src} segments in both source and target")


def _srt_text_blocks(path: Path) -> list[str]:
    """Return each segment's text body (timestamp and index lines removed)."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    blocks, current = [], []
    for i, line in enumerate(lines):
        s = line.strip()
        if s.isdigit() and i + 1 < len(lines) and "-->" in lines[i + 1]:
            if current:
                blocks.append("\n".join(current).strip())
            current = []
            continue
        if "-->" in s:
            continue
        if s:
            current.append(s)
    if current:
        blocks.append("\n".join(current).strip())
    return blocks


def gate_t3b_translation_actually_happened(source_srt: Path, target_srt: Path,
                                           target_language: str) -> None:
    """Gate T3b — untranslated-passthrough detection.

    Found the hard way (see reviews/04-qa-report.md): the `google` translator
    can hit a 429 rate limit, log the error, emit the ORIGINAL ENGLISH as the
    "translation", and still exit 0 with a cheerful `✓ Done (N segments)`.
    T2 passes (the service really was google), T3 passes (segment counts
    match) — and a reader ships an English-captioned video believing the
    chain verified it.

    Two independent checks, because either alone has a blind spot:
      1. CJK presence — for a Chinese target, a translated file must contain
         Han characters. Catches wholesale passthrough.
      2. Per-segment identity — flags segments byte-identical to their source.
         Catches partial passthrough, where only some batches failed.
    """
    src_blocks = _srt_text_blocks(source_srt)
    tgt_blocks = _srt_text_blocks(target_srt)

    if target_language.lower().startswith("zh"):
        han = re.compile(r"[一-鿿]")
        translated = sum(1 for b in tgt_blocks if han.search(b))
        if translated == 0:
            raise GateError(
                f"T3b FAIL: target language is '{target_language}' but "
                f"{target_srt.name} contains no Han characters at all — the "
                f"translator almost certainly passed the source through "
                f"untranslated (check its log for swallowed rate-limit or "
                f"auth errors, even if it exited 0)"
            )
        ratio = translated / len(tgt_blocks) if tgt_blocks else 0
        if ratio < 0.8:
            raise GateError(
                f"T3b FAIL: only {translated}/{len(tgt_blocks)} segments "
                f"({ratio:.0%}) contain Han characters — partial passthrough, "
                f"likely some batches failed silently"
            )

    if len(src_blocks) == len(tgt_blocks):
        identical = sum(1 for s, t in zip(src_blocks, tgt_blocks) if s == t and s)
        if identical:
            raise GateError(
                f"T3b FAIL: {identical}/{len(src_blocks)} segments are "
                f"byte-identical to the source — untranslated passthrough"
            )

    print(f"T3b PASS — target is genuinely translated, not source passthrough")


def _ffprobe_json(video: Path) -> dict:
    if not video.exists():
        print(f"ENV ERROR: video not found: {video}", file=sys.stderr)
        sys.exit(3)
    out = _run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-show_entries", "stream=width,height",
            "-of", "json",
            str(video),
        ]
    )
    return json.loads(out)


def gate_t4_synthesis_fidelity(source_video: Path, output_video: Path) -> None:
    """Gate T4 — synthesis fidelity. Resolution and duration must match the
    source exactly; synthesis should only overlay subtitles, never re-time,
    crop, or resize."""
    src = _ffprobe_json(source_video)
    out = _ffprobe_json(output_video)

    def video_stream(probe: dict) -> dict:
        for s in probe.get("streams", []):
            if "width" in s and "height" in s:
                return s
        raise GateError("T4 FAIL: no video stream with width/height found")

    src_stream, out_stream = video_stream(src), video_stream(out)
    if (src_stream["width"], src_stream["height"]) != (out_stream["width"], out_stream["height"]):
        raise GateError(
            f"T4 FAIL: resolution mismatch — source "
            f"{src_stream['width']}x{src_stream['height']}, output "
            f"{out_stream['width']}x{out_stream['height']}"
        )

    src_dur = float(src["format"]["duration"])
    out_dur = float(out["format"]["duration"])
    # 10ms tolerance for float/container rounding — not a "close enough on
    # content" tolerance. A gate that widens this to hide a real retime
    # defeats the point of having it; see docs/expertise_division.md rule 2.
    if abs(src_dur - out_dur) > 0.01:
        raise GateError(f"T4 FAIL: duration mismatch — source {src_dur}s, output {out_dur}s")

    print(
        f"T4 PASS — {src_stream['width']}x{src_stream['height']}, "
        f"{src_dur:.3f}s (source) vs {out_dur:.3f}s (output)"
    )


def gate_t5_guard(ocr_check: bool) -> None:
    """Gate T5 is NEVER auto-verified by this script. The mechanised part
    of this gate is refusing the one circular shortcut someone will
    eventually try: OCR-ing the burned-in video text and diffing it
    against the same .srt file used to synthesize it. That only proves
    Gate T4 (synthesis didn't corrupt the text) a second time — it proves
    nothing about whether the Chinese is a faithful translation of the
    English source. Run the real procedure by hand or by agent:
    docs/expertise_division.md section 4.
    """
    if ocr_check:
        print(
            "T5 VOID — OCR-vs-own-srt is circular: it only re-proves "
            "synthesis fidelity (T4), not translation fidelity. Compare the "
            "English source .srt against the target .srt directly instead "
            "(docs/expertise_division.md section 4), never the rendered video "
            "against its own subtitle file.",
            file=sys.stderr,
        )
        sys.exit(2)
    print(
        "T5 NOT AUTO-VERIFIED — run docs/expertise_division.md section 4 "
        "by hand (or via the Bilingual Caption QA Specialist) against the "
        "source and target .srt files before treating this run as done."
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source-video", required=True, type=Path)
    p.add_argument("--source-srt", required=True, type=Path)
    p.add_argument("--target-srt", required=True, type=Path)
    p.add_argument("--output-video", required=True, type=Path)
    p.add_argument("--translator", default="llm", help="expected translate.service (default: llm)")
    p.add_argument("--target-language", default="zh-Hans",
                   help="BCP 47 target language, used by Gate T3b (default: zh-Hans)")
    p.add_argument(
        "--ocr-check", action="store_true",
        help="deliberately trigger the T5 circularity guard (VOID) — for demonstrating the trap, not for real use",
    )
    args = p.parse_args()

    try:
        gate_t1_transcription(args.source_srt)
        gate_t2_translator_provenance(args.translator)
        gate_t3_segment_parity(args.source_srt, args.target_srt)
        gate_t3b_translation_actually_happened(args.source_srt, args.target_srt, args.target_language)
        gate_t4_synthesis_fidelity(args.source_video, args.output_video)
        gate_t5_guard(args.ocr_check)
    except GateError as e:
        print(str(e), file=sys.stderr)
        return 1

    print("\nGates T1-T4: PASS. Gate T5: run it by hand before calling this done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

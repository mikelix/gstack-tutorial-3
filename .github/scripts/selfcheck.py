#!/usr/bin/env python3
"""Repo self-check for gstack-tutorial-3.

Mirrors gstack-tutorial-2's .github/scripts/selfcheck.py in spirit: a check
that catches one real defect per run is worth more than a page of prose.

Checks:
  1. Required files exist
  2. Every relative markdown link resolves to a real file
  3. EN/ZH structural parity (H2/H3 counts, checkbox counts)
  4. run_gates.py compiles and its exit-code contract is documented
  5. No file is read with plain utf-8 in run_gates.py (BOM lesson, QA finding 5)

Run:  python .github/scripts/selfcheck.py
Exit: 0 all good, 1 one or more checks failed.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "README.md",
    "LICENSE.md",
    "PLAN.md",
    "TUTORIAL.md",
    "TUTORIAL.zh.md",
    "docs/expertise_division.md",
    "docs/expertise_division.zh.md",
    "docs/choosing_a_translator.md",
    "docs/choosing_a_translator.zh.md",
    "reviews/01-ceo-review.md",
    "reviews/02-spec.md",
    "reviews/03-eng-review.md",
    "reviews/04-qa-report.md",
    "starter/INSTALL.md",
    "starter/versions.lock.template",
    "starter/scripts/run_gates.py",
    ".gitattributes",
    ".gitignore",
    "_build/mck.py",
    "_build/deck_content.py",
    "_build/build_deck.py",
    "_build/doc_content.py",
    "_build/build_docx.py",
    "_build/verify_docx.py",
    "dist/README.md",
    "dist/gstack-tutorial-3_EN.pptx",
    "dist/gstack-tutorial-3_ZH.pptx",
    "dist/gstack-tutorial-3_EN.docx",
    "dist/gstack-tutorial-3_ZH.docx",
    "docs/deck_market_benchmark.md",
    "reviews/05-ship.md",
    "PUBLISH.md",
]

failures: list[str] = []
checks_run = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global checks_run
    checks_run += 1
    if ok:
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}" + (f" — {detail}" if detail else ""))
        failures.append(label)


print("1. Required files")
for rel in REQUIRED:
    check(rel, (ROOT / rel).exists())

print("\n2. Markdown link resolution")
link_re = re.compile(r"\[[^\]]*\]\((?!https?:|#)([^)]+)\)")
for md in sorted(ROOT.rglob("*.md")):
    if ".git" in md.parts:
        continue
    text = md.read_text(encoding="utf-8-sig")
    for target in link_re.findall(text):
        target = target.split("#")[0].strip()
        if not target:
            continue
        resolved = (md.parent / target).resolve()
        rel_label = f"{md.relative_to(ROOT)} -> {target}"
        check(rel_label, resolved.exists())

print("\n3. EN/ZH parity (TUTORIAL.md only -- see below for scope)")
en = (ROOT / "TUTORIAL.md").read_text(encoding="utf-8-sig")
zh = (ROOT / "TUTORIAL.zh.md").read_text(encoding="utf-8-sig")
for label, pattern in [
    ("H2 section count", r"^## "),
    ("H3 section count", r"^### "),
    ("checkbox count", r"- \[ \]"),
]:
    n_en = len(re.findall(pattern, en, re.M))
    n_zh = len(re.findall(pattern, zh, re.M))
    check(f"{label} ({n_en} vs {n_zh})", n_en == n_zh, f"EN={n_en} ZH={n_zh}")

print("\n4. Gate script integrity")
gates_src = (ROOT / "starter/scripts/run_gates.py").read_text(encoding="utf-8-sig")
import py_compile

try:
    py_compile.compile(str(ROOT / "starter/scripts/run_gates.py"), doraise=True)
    check("run_gates.py compiles", True)
except py_compile.PyCompileError as e:
    check("run_gates.py compiles", False, str(e))

for code, meaning in [("0", "PASS"), ("1", "FAIL"), ("2", "VOID"), ("3", "environment")]:
    check(f"exit code {code} documented", f"    {code}  " in gates_src or f"`{code}`" in gates_src)

print("\n5. BOM-safe reads (QA report finding 5)")
bad = re.findall(r'encoding="utf-8"', gates_src)
check("no plain utf-8 reads in run_gates.py", not bad,
      f"{len(bad)} occurrence(s) — use utf-8-sig, Windows tools emit BOMs")

print("\n6. Deliverables are generated, not hand-made")
# Both editions must come from the SAME content module — the guarantee that
# EN and ZH cannot drift apart in structure (dist/README.md).
for builder, content in [("_build/build_deck.py", "deck_content"),
                         ("_build/build_docx.py", "doc_content")]:
    src = (ROOT / builder).read_text(encoding="utf-8-sig")
    check(f"{builder} imports {content}", f"from {content} import" in src)
    check(f"{builder} builds both languages", 'for lang in ("en", "zh")' in src)

deck_src = (ROOT / "_build/deck_content.py").read_text(encoding="utf-8-sig")
doc_src = (ROOT / "_build/doc_content.py").read_text(encoding="utf-8-sig")
check("doc_content reuses the deck's L() marker", "from deck_content import L" in doc_src)
mck_src = (ROOT / "_build/mck.py").read_text(encoding="utf-8-sig")
check("every slide run sets an eastAsia font", "a:ea" in mck_src)
docx_src = (ROOT / "_build/build_docx.py").read_text(encoding="utf-8-sig")
check("every docx run sets w:eastAsia", "w:eastAsia" in docx_src)

for f in ("dist/gstack-tutorial-3_EN.pptx", "dist/gstack-tutorial-3_ZH.pptx",
          "dist/gstack-tutorial-3_EN.docx", "dist/gstack-tutorial-3_ZH.docx"):
    p = ROOT / f
    check(f"{f} is a non-trivial file", p.exists() and p.stat().st_size > 20_000,
          f"{p.stat().st_size if p.exists() else 0} bytes")

print(f"\n{'=' * 50}")
if failures:
    print(f"FAILED — {len(failures)} of {checks_run} checks failed:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print(f"PASSED — all {checks_run} checks green.")
sys.exit(0)

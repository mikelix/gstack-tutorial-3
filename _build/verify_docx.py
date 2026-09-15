# -*- coding: utf-8 -*-
"""Mandatory 3-part docx verification from MCKINSEY_DOCX_PLAYBOOK.docx Section 5.

Run BEFORE opening anything in Word. A file can be a perfectly valid ZIP with
well-formed XML and still be broken in ways only structure inspection catches.

  Check 1 — body structure: last child is w:sectPr, zero stray w:r at body level
  Check 2 — no duplicate consecutive text runs (the text:+children: bug)
  Check 3 — ZIP integrity and content type
  Check 4 — (ZH only) eastAsia font set on every run

Exit 0 all clean, 1 if any document fails.
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

failures = []


def check(label, ok, detail=""):
    print(f"  {'OK  ' if ok else 'FAIL'} {label}" + (f" — {detail}" if not ok and detail else ""))
    if not ok:
        failures.append(label)


def verify(path: Path, expect_cjk: bool):
    print(f"\n{path.name}")
    # ---- Check 3 first: if the ZIP is bad nothing else is meaningful
    try:
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            check("ZIP integrity", bad is None, f"corrupt member: {bad}")
            xml = z.read("word/document.xml").decode("utf-8")
            names = z.namelist()
    except Exception as e:  # noqa: BLE001
        check("ZIP integrity", False, str(e))
        return
    check("has [Content_Types].xml", "[Content_Types].xml" in names)

    # ---- Check 1: body structure
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    body = root.find(f"{W}body")
    children = list(body)
    check("body last child is w:sectPr",
          children and children[-1].tag == f"{W}sectPr",
          f"last is {children[-1].tag if children else 'nothing'}")
    strays = [c for c in children if c.tag == f"{W}r"]
    check("zero stray w:r at body level", not strays,
          f"{len(strays)} stray run(s)")

    # ---- Check 2: no duplicate consecutive text runs
    texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)
    dupes = [texts[i] for i in range(len(texts) - 1)
             if texts[i] == texts[i + 1] and len(texts[i].strip()) > 1]
    check("no duplicate consecutive text runs", not dupes,
          f"{len(dupes)} duplicate(s), first: {dupes[0][:40] if dupes else ''!r}")

    # ---- Check 4: eastAsia on every run (playbook Section 6)
    run_count = xml.count("<w:rFonts")
    ea_count = xml.count('w:eastAsia=')
    check("eastAsia font set on every rFonts", run_count == ea_count,
          f"{ea_count} eastAsia vs {run_count} rFonts")

    if expect_cjk:
        has_han = bool(re.search(r"[一-鿿]", xml))
        check("contains Han characters", has_han)
        check("eastAsia is Microsoft YaHei",
              'w:eastAsia="Microsoft YaHei"' in xml)

    # informational
    print(f"       {len(texts)} text runs, {run_count} rFonts elements")


if __name__ == "__main__":
    verify(ROOT / "dist" / "gstack-tutorial-3_EN.docx", expect_cjk=False)
    verify(ROOT / "dist" / "gstack-tutorial-3_ZH.docx", expect_cjk=True)

    print("\n" + "=" * 52)
    if failures:
        print(f"FAILED — {len(failures)} check(s) failed. Do NOT hand off these files;")
        print("fix the generator script, not the output.")
        sys.exit(1)
    print("PASSED — all documents clean. Safe to open in Word.")
    sys.exit(0)

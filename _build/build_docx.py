# -*- coding: utf-8 -*-
"""Generate the gstack Tutorial No.3 Word documents (EN + ZH).

Style follows MCKINSEY_DOCX_PLAYBOOK.docx exactly:
  - Navy #1F4E78 headings, body #000000, caption #595959, muted #808080,
    code/zebra fill #F2F2F2
  - Calibri 11pt body; H1 14pt bold navy with a bottom border rule;
    H2 12pt bold navy; captions 10pt italic grey; code Consolas 10pt shaded
  - US Letter, 1in margins, page break before each H1
  - Cover -> Executive Summary -> Table of Contents -> numbered sections
  - Metrics table near the top of Section 1
  - CJK: eastAsia font set on EVERY run (playbook Section 6)

The playbook's two gotchas are docx-js specific (PageBreak wrapping and
text:+children: duplication). python-docx cannot express either, but the
VERIFICATION it mandates still applies and runs in verify_docx.py — a valid
ZIP with well-formed XML can still be wrong in ways only structure
inspection catches.

Usage:  python _build/build_docx.py
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).parent))
from doc_content import DOC, pick

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

NAVY = RGBColor(0x1F, 0x4E, 0x78)
BLACK = RGBColor(0x00, 0x00, 0x00)
CAPTION = RGBColor(0x59, 0x59, 0x59)
MUTED = RGBColor(0x80, 0x80, 0x80)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FILL = "F2F2F2"
NAVY_HEX = "1F4E78"

LATIN = "Calibri"
MONO = "Consolas"
CJK = "Microsoft YaHei"


def style_run(r, size=11, bold=False, color=BLACK, mono=False, italic=False):
    """Set fonts on a run, ALWAYS including eastAsia.

    Playbook Section 6: Word stores East Asian glyphs under a separate
    w:rFonts/@w:eastAsia attribute. Leave it unset and some Word builds
    substitute a default serif for Chinese while Latin text looks fine.
    """
    name = MONO if mono else LATIN
    ea = MONO if mono else CJK
    r.font.name = name
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    rPr = r._r.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rPr.append(rf)
    rf.set(qn('w:ascii'), name)
    rf.set(qn('w:hAnsi'), name)
    rf.set(qn('w:eastAsia'), ea)
    rf.set(qn('w:cs'), name)
    return r


def shade(el, hex_fill):
    pr = el._p.get_or_add_pPr() if hasattr(el, "_p") else el._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear')
    sh.set(qn('w:fill'), hex_fill)
    pr.append(sh)


def bottom_border(p, hex_color=NAVY_HEX, size=12):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), str(size))
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), hex_color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def para(doc, text="", size=11, bold=False, color=BLACK, mono=False,
         italic=False, space_before=0, space_after=6, align=None, indent=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.15
    if align is not None:
        p.alignment = align
    if indent is not None:
        pf.left_indent = Inches(indent)
    if text:
        style_run(p.add_run(text), size, bold, color, mono, italic)
    return p


def h1(doc, text, first=False):
    if not first:
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    style_run(p.add_run(text), 14, True, NAVY)
    bottom_border(p)
    return p


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    style_run(p.add_run(text), 12, True, NAVY)
    return p


def bullet(doc, label, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.3)
    pf.space_after = Pt(5)
    pf.line_spacing = 1.15
    style_run(p.add_run("•  "), 11, False, NAVY)
    if label:
        style_run(p.add_run(label + "  "), 11, True, NAVY)
    style_run(p.add_run(text), 11, False, BLACK)
    return p


def code_block(doc, lines):
    for i, ln in enumerate(lines):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Inches(0.25)
        pf.space_before = Pt(6 if i == 0 else 0)
        pf.space_after = Pt(6 if i == len(lines) - 1 else 0)
        pf.line_spacing = 1.0
        style_run(p.add_run(ln if ln else " "), 10, False, BLACK, mono=True)
        shade(p, FILL)


def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0].cells
    for i, htxt in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        style_run(p.add_run(htxt), 10, True, WHITE)
        shade(hdr[i], NAVY_HEX)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci, val in enumerate(row):
            cells[ci].text = ""
            p = cells[ci].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            is_mono = val.startswith("`") and val.endswith("`")
            style_run(p.add_run(val.strip("`")), 10, False, BLACK, mono=is_mono)
            if ri % 2 == 1:
                shade(cells[ci], FILL)
    if widths:
        total = sum(widths)
        avail = 6.5
        for ci, w in enumerate(widths):
            for row in t.rows:
                row.cells[ci].width = Inches(avail * w / total)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def build(lang: str) -> Path:
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)      # US Letter
    sec.page_height = Inches(11)
    sec.left_margin = sec.right_margin = Inches(1)
    sec.top_margin = sec.bottom_margin = Inches(1)

    st = doc.styles['Normal']
    st.font.name = LATIN
    st.font.size = Pt(11)

    d = pick(DOC, lang)

    # ---------------------------------------------------------- cover
    for _ in range(6):
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
    para(doc, d["kicker"].upper(), 12, True, NAVY, space_after=10)
    para(doc, d["title"], 26, True, NAVY, space_after=8)
    para(doc, d["subtitle"], 13, False, CAPTION, italic=True, space_after=26)
    p = doc.add_paragraph()
    bottom_border(p, NAVY_HEX, 6)
    for m in d["meta"]:
        para(doc, m, 10, False, MUTED, space_after=3)

    # ------------------------------------------------- executive summary
    h1(doc, d["exec_heading"])
    for t in d["exec_paras"]:
        para(doc, t, 11, space_after=8)

    h2(doc, d["metrics_heading"])
    para(doc, d["metrics_caption"], 10, False, CAPTION, italic=True,
         space_after=6)
    table(doc, d["metrics_headers"], d["metrics_rows"], widths=[3, 3.5])

    # ------------------------------------------------------------ TOC
    h1(doc, d["toc_heading"])
    for i, entry in enumerate(d["toc"], 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.15)
        style_run(p.add_run(f"{i}.  "), 11, True, NAVY)
        style_run(p.add_run(entry), 11, False, BLACK)

    # ------------------------------------------------------- sections
    for si, sec_d in enumerate(d["sections"], 1):
        h1(doc, f"{si}.  {sec_d['title']}")
        for block in sec_d["blocks"]:
            kind = block[0]
            if kind == "p":
                para(doc, block[1], 11, space_after=8)
            elif kind == "caption":
                para(doc, block[1], 10, False, CAPTION, italic=True,
                     space_after=8)
            elif kind == "h2":
                h2(doc, block[1])
            elif kind == "bullets":
                for label, text in block[1]:
                    bullet(doc, label, text)
                doc.add_paragraph().paragraph_format.space_after = Pt(2)
            elif kind == "code":
                code_block(doc, block[1])
            elif kind == "table":
                _, headers, rows, widths = block
                table(doc, headers, rows, widths)
            elif kind == "callout":
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.2)
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(8)
                style_run(p.add_run(block[1]), 11, True, NAVY)
                shade(p, FILL)
            else:
                raise ValueError(f"unknown block kind: {kind}")

    DIST.mkdir(exist_ok=True)
    out = DIST / f"gstack-tutorial-3_{lang.upper()}.docx"
    doc.save(str(out))
    return out


if __name__ == "__main__":
    for lang in ("en", "zh"):
        p = build(lang)
        print(f"  wrote {p.relative_to(ROOT)}")

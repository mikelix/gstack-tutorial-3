# -*- coding: utf-8 -*-
"""McKinsey-style slide primitives for gstack Tutorial No.3.

Palette follows MCKINSEY_DOCX_PLAYBOOK.docx (the house style used for the
gstack tutorial series), extended from documents to slides. Type scale is
tuned for a room, not a desk: the project owner tested v1 (title 21pt, body
14pt) and found it too small even at the previously-"fixed" 18pt; the
working floor is 30pt for anything meant to be read as prose. See "Type
scale" below for what that forces, and the auto-fit / WARN mechanism for
the one place (dense table cells) where 30pt and the content don't
simultaneously fit without rewriting the content.

The defining convention here is the ACTION TITLE: every content slide's
title is a full sentence stating the takeaway ("Four gates pass mechanically;
the fifth needs a human"), not a topic label ("Gates"). A reader flipping
only the titles must get the whole argument.

Design rules enforced by these helpers:
  - 16:9, 13.333 x 7.5in, consistent 0.75in left/right margin grid
  - Action title top-left, thin navy rule beneath, takeaway-first, its own
    height computed from actual wrapped line count (a long title at 32pt
    needs more room than a short one — fixed-height title boxes silently
    clip long titles)
  - Generous whitespace; no drop shadows, no gradients, no clip art
  - Source/footnote line bottom-left, page number bottom-right
  - Every text run carries an explicit eastAsia font (CJK rule from the
    playbook Section 6 — without it Word/PowerPoint substitute a serif
    for Chinese glyphs on some builds)
"""
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
import re

# ---------------------------------------------------------------- palette
# Straight from MCKINSEY_DOCX_PLAYBOOK.docx Color Palette table.
NAVY = RGBColor(0x1F, 0x4E, 0x78)   # primary: headings, rules, key numbers
NAVY_DK = RGBColor(0x14, 0x35, 0x52)  # deeper navy for full-bleed dividers
BLACK = RGBColor(0x00, 0x00, 0x00)   # body text
CAPTION = RGBColor(0x59, 0x59, 0x59)  # subtitles, labels
MUTED = RGBColor(0x80, 0x80, 0x80)   # dates, footnotes, page numbers
FILL = RGBColor(0xF2, 0xF2, 0xF2)   # code blocks, zebra rows
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RULE = RGBColor(0xD8, 0xDE, 0xE4)   # hairline separators
# Accents used sparingly and only to carry meaning (pass/fail/warn).
GOOD = RGBColor(0x1E, 0x7A, 0x4D)
BAD = RGBColor(0xA3, 0x1D, 0x1D)
WARN = RGBColor(0xB0, 0x6A, 0x00)

LATIN = "Calibri"
MONO = "Consolas"

W = Inches(13.333)
H = Inches(7.5)
MARGIN = Inches(0.75)
CONTENT_W = W - 2 * MARGIN
TITLE_Y = Inches(0.5)
FOOT_Y = Inches(6.95)

# ---------------------------------------------------------------- type scale
# The floor the project owner tested and asked for: 30pt for anything meant
# to be read as prose (body text, table cells, flow-step copy). Chrome
# (kicker eyebrow labels, footer source lines, page numbers) is exempt by
# universal presentation convention — it is never meant to be read from the
# back of the room, only found by someone tracing a claim — but is still
# roughly doubled from the original sizes so it is not squinting-small.
TITLE_SIZE = 32
KICKER_SIZE = 16
LEAD_SIZE = 19
BULLET_TARGET = 30
BULLET_FLOOR = 22
TABLE_HEADER_SIZE = 17
TABLE_TARGET = 26
TABLE_FLOOR = 18
CODE_TARGET = 20
CODE_FLOOR = 16
FLOW_LABEL_SIZE = 20
FLOW_BODY_SIZE = 17
TWOCOL_HEAD_SIZE = 18
TWOCOL_LINE_SIZE = 22
BIGNUM_SIZE = 48
BIGNUM_LABEL_SIZE = 18
BIGNUM_SUB_SIZE = 15
QUOTE_SIZE = 32
QUOTE_ATTRIB_SIZE = 16
CHROME_SIZE = 12
COVER_KICKER_SIZE = 18
COVER_TITLE_SIZE = 40
COVER_SUBTITLE_SIZE = 20
COVER_META_SIZE = 14
DIVIDER_NUM_SIZE = 64
DIVIDER_TITLE_SIZE = 34
DIVIDER_BLURB_SIZE = 18


def sf(run, size=14, bold=False, color=BLACK, name=LATIN, ea=None, mono=False,
       italic=False):
    """Style a run and ALWAYS set the eastAsia font.

    Playbook Section 6: Word and PowerPoint store East Asian glyphs under a
    separate font attribute (w:eastAsia / a:ea). Leave it unset and some
    builds silently substitute a serif for Chinese text while Latin text
    renders correctly. Set it on every run, not just headings.
    """
    if mono:
        name = MONO
    if ea is None:
        ea = "Microsoft YaHei" if not mono else MONO
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    latin = rPr.find(qn('a:latin'))
    if latin is None:
        latin = OxmlElement('a:latin')
        rPr.append(latin)
    latin.set('typeface', name)
    for tag in ('a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            rPr.append(el)
        el.set('typeface', ea)


# A cell colored as a status word only when the status token is the whole
# cell, or is immediately followed by a separator (— = :) — never when it's
# merely the first word of an ordinary sentence ("VOID has a distinct exit
# code..." is prose about VOID, not a VOID status cell, and coloring it red
# misleadingly reads as an actual failure marker).
_STATUS_RE = re.compile(r'^(PASS|FAIL|VOID|通过|失败|无效)(\s*[—=:]|$)')


def _status_color(txt):
    m = _STATUS_RE.match(txt)
    if not m:
        return None
    tok = m.group(1)
    if tok in ("PASS", "通过"):
        return GOOD
    if tok in ("FAIL", "VOID", "失败", "无效"):
        return BAD
    return None


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(0.75)
    s.shadow.inherit = False   # no shadows, ever
    return s


def textbox(slide, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    # python-pptx's default for a new textbox is spAutoFit — PowerPoint
    # independently resizes the SHAPE to fit its real text content,
    # regardless of the height passed to add_textbox(). Every subsequent
    # element's y-position in this file is computed from OUR estimated
    # box height, not PowerPoint's real (autofit) one — any gap between the
    # two silently became a visual overlap or a dead gap. Disabling autofit
    # makes our height estimates authoritative: the box is exactly the size
    # we say, so our own layout math stays internally consistent even when
    # the character-width estimate itself isn't perfectly calibrated.
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.paragraphs[0].alignment = align
    return tb, tf


def _para(tf, first=False):
    return tf.paragraphs[0] if first else tf.add_paragraph()


def write(tf, text, first=False, size=14, bold=False, color=BLACK, mono=False,
          italic=False, align=PP_ALIGN.LEFT, space_after=0, line=None):
    p = _para(tf, first)
    p.alignment = align
    if space_after:
        p.space_after = Pt(space_after)
    if line:
        p.line_spacing = line
    r = p.add_run()
    r.text = text
    sf(r, size, bold, color, mono=mono, italic=italic)
    return p


# ------------------------------------------------------------ text metrics
# python-pptx has no font-metrics API, so line-wrap estimates here are a
# deliberately conservative approximation (not real glyph measurement) used
# only to budget layout — decide font sizes and box heights before content
# is placed. A CJK character renders roughly square (~1.0x its point size);
# a Latin character averages narrower. The 0.90 safety factor on capacity
# accounts for word-boundary wrapping being less efficient than raw
# character packing.
def _is_cjk(text):
    return any('一' <= ch <= '鿿' for ch in text)


def _line_capacity(width_emu, size_pt, bold=False, cjk=False, mono=False):
    # Calibrated against real rendered output (see mck.py history / the
    # session that fixed the autofit bug): a 65-char bold 32pt title
    # measured on-slide as fitting a single line at 11.833in width implies
    # a real average character width of ~0.41 em for Calibri Bold, not the
    # originally-guessed 0.56 — the earlier factor was overestimating
    # required line counts everywhere bold text appears (titles, table
    # headers, bignum labels), which mattered more than it should have
    # because of a since-fixed autofit bug, but still wastes vertical
    # budget if left uncorrected.
    width_in = width_emu / 914400
    if mono:
        factor = 0.60   # Consolas fixed-width; close to measured Segoe/Consolas metrics
    elif cjk:
        factor = 1.05
    elif bold:
        factor = 0.46
    else:
        factor = 0.42
    char_w_in = (size_pt * factor) / 72
    return max(1, int(width_in / char_w_in * 0.90))


def _wrapped_lines(text, width_emu, size_pt, bold=False, mono=False):
    if not text:
        return 1
    cap = _line_capacity(width_emu, size_pt, bold, _is_cjk(text), mono)
    return max(1, -(-len(text) // cap))  # ceil division


def _line_height_in(size_pt, spacing=1.22):
    return size_pt * spacing / 72


def _fit_size(candidates, fits_fn, label, warn_below):
    """Try candidate sizes largest-first; return the first that fits.

    Falls back to the smallest candidate if none fit outright (better to
    slightly overflow at the smallest allowed size than to silently pick an
    even-smaller size that was never actually offered). Prints a WARN line
    whenever the chosen size lands below `warn_below`, so a build makes its
    own compromises visible instead of hiding them.
    """
    chosen = candidates[-1]
    for size in candidates:
        if fits_fn(size):
            chosen = size
            break
    if chosen < warn_below:
        print(f"  WARN  {label}: sized to {chosen}pt (target {candidates[0]}pt) "
              f"to fit — consider shortening the content")
    return chosen


# ------------------------------------------------------------ chrome
def chrome(slide, page, source=None, dark=False):
    """Page number bottom-right, optional source note bottom-left.

    A source line on every slide carrying a claim is standard consulting
    practice: the reader can always trace a number back. Deliberately the
    smallest text on the page (CHROME_SIZE) — universal convention, and the
    one place a strict 30pt floor would look absurd (a citation is not
    meant to be read from the back of the room).
    """
    col = MUTED if not dark else RGBColor(0x9A, 0xA8, 0xB4)
    if source:
        _, tf = textbox(slide, MARGIN, FOOT_Y, Inches(10.5), Inches(0.3))
        write(tf, source, first=True, size=CHROME_SIZE, color=col, italic=True)
    _, tf = textbox(slide, W - MARGIN - Inches(1.0), FOOT_Y, Inches(1.0),
                    Inches(0.3), align=PP_ALIGN.RIGHT)
    write(tf, str(page), first=True, size=CHROME_SIZE, color=col)


def action_title(slide, title, kicker=None):
    """The action title: a full sentence carrying the takeaway.

    Returns the y-coordinate (Emu) where body content should start. Title
    height is computed from the actual wrapped line count at TITLE_SIZE —
    a fixed-height box would either clip a long title or waste space under
    a short one, and titles vary a lot in length because they are full
    sentences, not topic labels.
    """
    y = TITLE_Y
    if kicker:
        _, tf = textbox(slide, MARGIN, y, CONTENT_W, Inches(0.3))
        write(tf, kicker.upper(), first=True, size=KICKER_SIZE, bold=True, color=NAVY)
        y = y + Inches(0.36)

    lines = _wrapped_lines(title, CONTENT_W, TITLE_SIZE, bold=True)
    box_h = Inches(_line_height_in(TITLE_SIZE) * lines + 0.05)
    _, tf = textbox(slide, MARGIN, y, CONTENT_W, box_h)
    write(tf, title, first=True, size=TITLE_SIZE, bold=True, color=NAVY, line=1.08)
    y = y + box_h + Inches(0.12)
    rect(slide, MARGIN, y, CONTENT_W, Emu(9525), fill=NAVY)
    return y + Inches(0.16)


# ------------------------------------------------------------ slide types
def slide_cover(prs, kicker, title, subtitle, meta):
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=NAVY_DK)
    rect(s, 0, 0, Inches(0.13), H, fill=RGBColor(0x00, 0xA6, 0xC9))
    _, tf = textbox(s, Inches(1.0), Inches(1.85), Inches(11.2), Inches(0.45))
    write(tf, kicker.upper(), first=True, size=COVER_KICKER_SIZE, bold=True,
          color=RGBColor(0x7F, 0xC4, 0xE8))
    _, tf = textbox(s, Inches(1.0), Inches(2.4), Inches(11.2), Inches(1.6))
    write(tf, title, first=True, size=COVER_TITLE_SIZE, bold=True, color=WHITE, line=1.08)
    _, tf = textbox(s, Inches(1.0), Inches(4.25), Inches(10.6), Inches(1.1))
    write(tf, subtitle, first=True, size=COVER_SUBTITLE_SIZE,
          color=RGBColor(0xC9, 0xD6, 0xE0), line=1.3)
    rect(s, Inches(1.0), Inches(5.6), Inches(1.6), Emu(19050), fill=RGBColor(0x00, 0xA6, 0xC9))
    _, tf = textbox(s, Inches(1.0), Inches(5.9), Inches(10.6), Inches(1.3))
    for i, m in enumerate(meta):
        write(tf, m, first=(i == 0), size=COVER_META_SIZE,
              color=RGBColor(0x9A, 0xA8, 0xB4), space_after=4)
    return s


def slide_divider(prs, num, title, blurb, page):
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=NAVY_DK)
    _, tf = textbox(s, Inches(1.0), Inches(2.55), Inches(1.9), Inches(1.5))
    write(tf, num, first=True, size=DIVIDER_NUM_SIZE, bold=True,
          color=RGBColor(0x00, 0xA6, 0xC9))
    rect(s, Inches(2.75), Inches(2.75), Emu(9525), Inches(1.3),
         fill=RGBColor(0x3E, 0x5A, 0x72))
    _, tf = textbox(s, Inches(3.2), Inches(2.7), Inches(9.0), Inches(1.0))
    write(tf, title, first=True, size=DIVIDER_TITLE_SIZE, bold=True, color=WHITE, line=1.1)
    _, tf = textbox(s, Inches(3.2), Inches(3.75), Inches(8.6), Inches(0.9))
    write(tf, blurb, first=True, size=DIVIDER_BLURB_SIZE,
          color=RGBColor(0xB6, 0xC5, 0xD2), line=1.3)
    chrome(s, page, dark=True)
    return s


def pick_text(b):
    return b[1] if isinstance(b, tuple) else b


def _place_lead(slide, body_y, lead):
    """Render the italic 'lead' caption line and return the y-coordinate
    after it, sized from its REAL wrapped line count. A fixed reservation
    here caused the same class of bug found repeatedly elsewhere in this
    file: a lead longer than one line silently overlapped the content
    placed right after it."""
    if not lead:
        return body_y
    lines = _wrapped_lines(lead, CONTENT_W, LEAD_SIZE, bold=False)
    h = Inches(_line_height_in(LEAD_SIZE, 1.3) * lines + 0.08)
    _, tf = textbox(slide, MARGIN, body_y, CONTENT_W, h)
    write(tf, lead, first=True, size=LEAD_SIZE, color=CAPTION, italic=True, line=1.3)
    return body_y + h + Inches(0.14)


def slide_bullets(prs, title, bullets, page, kicker=None, source=None, lead=None):
    s = blank(prs)
    body_y = action_title(s, title, kicker)
    text_w = CONTENT_W - Inches(0.32)
    body_y = _place_lead(s, body_y, lead)
    avail_in = (FOOT_Y - Inches(0.25) - body_y) / 914400

    def total_height_in(size):
        gap_in = 0.14
        total = 0.0
        for b in bullets:
            bold_txt, rest = (b if isinstance(b, tuple) else (None, b))
            full = (bold_txt + "  " if bold_txt else "") + rest
            # A bullet mixing a bold label with regular text wraps according
            # to whichever run is on a given line — estimating the WHOLE
            # string as regular-weight underestimates required lines (bold
            # glyphs are wider) and was causing real overflow into the
            # footer. Estimating as bold is conservative (a few bullets get
            # slightly more room than strictly needed) instead of wrong.
            lines = _wrapped_lines(full, text_w, size, bold=bool(bold_txt))
            total += lines * _line_height_in(size) + gap_in
        return total

    # Safety margin against PowerPoint's real rendered height repeatedly
    # exceeding this estimate (see mck.py's font-size-fix history).
    size = _fit_size(list(range(BULLET_TARGET, BULLET_FLOOR - 1, -2)),
                     lambda sz: total_height_in(sz) * 1.15 <= avail_in,
                     f"bullets '{title[:50]}'", BULLET_TARGET)

    slack_in = max(0.0, avail_in - total_height_in(size))
    pad_in = min(0.4, slack_in / max(len(bullets), 1))

    y = body_y
    for b in bullets:
        bold_txt, rest = (b if isinstance(b, tuple) else (None, b))
        full = (bold_txt + "  " if bold_txt else "") + rest
        lines = _wrapped_lines(full, text_w, size, bold=bool(bold_txt))
        box_h_in = lines * _line_height_in(size) + 0.06

        rect(s, MARGIN + Inches(0.02), y + Inches(size / 72 * 0.45), Inches(0.09),
             Inches(0.09), fill=NAVY)
        _, tf = textbox(s, MARGIN + Inches(0.32), y, text_w, Inches(box_h_in))
        p = tf.paragraphs[0]
        p.line_spacing = 1.22
        if bold_txt:
            r = p.add_run(); r.text = bold_txt + "  "
            sf(r, size, True, NAVY)
        r = p.add_run(); r.text = rest
        sf(r, size, False, BLACK)
        y = y + Inches(box_h_in + 0.14 + pad_in)
    chrome(s, page, source)
    return s


def slide_table(prs, title, headers, rows, page, kicker=None, source=None,
                widths=None, emphasis_col=None, lead=None):
    """Zebra table, navy header, no vertical rules (data-ink discipline).

    Font size is chosen once for the whole table (not per-cell) so the grid
    reads as one visual system, by trying TABLE_TARGET down to TABLE_FLOOR
    and picking the largest size at which every row's tallest cell still
    fits the row's computed height. A table that still needs TABLE_FLOOR is
    dense — the WARN from `_fit_size` is the build-time signal to shorten
    that table's cell text or split it across two slides, not a silent
    permanent compromise.
    """
    s = blank(prs)
    body_y = action_title(s, title, kicker)
    body_y = _place_lead(s, body_y, lead)

    n = len(headers)
    if widths:
        total_w = sum(widths)
        cols = [Emu(int(CONTENT_W * w / total_w)) for w in widths]
    else:
        cols = [Emu(int(CONTENT_W / n))] * n

    hdr_h = Inches(_line_height_in(TABLE_HEADER_SIZE) + 0.2)
    avail_in = (FOOT_Y - Inches(0.25) - body_y - hdr_h) / 914400

    def rows_height_in(size):
        total = 0.0
        for row in rows:
            max_lines = 1
            for ci, cell in enumerate(row):
                txt = cell.strip("`")
                lines = _wrapped_lines(txt, cols[ci] - Inches(0.24), size,
                                       bold=(emphasis_col is not None and ci == emphasis_col))
                max_lines = max(max_lines, lines)
            total += max_lines * _line_height_in(size) + 0.14
        return total

    size = _fit_size(list(range(TABLE_TARGET, TABLE_FLOOR - 1, -2)),
                     lambda sz: rows_height_in(sz) <= avail_in,
                     f"table '{title[:50]}'", TABLE_TARGET - 4)

    y = body_y
    rect(s, MARGIN, y, CONTENT_W, hdr_h, fill=NAVY)
    x = MARGIN
    for i, htxt in enumerate(headers):
        _, tf = textbox(s, x + Inches(0.14), y + Inches(0.08),
                        cols[i] - Inches(0.24), hdr_h - Inches(0.12))
        write(tf, htxt, first=True, size=TABLE_HEADER_SIZE, bold=True, color=WHITE)
        x = x + cols[i]
    y = y + hdr_h

    for ri, row in enumerate(rows):
        max_lines = 1
        for ci, cell in enumerate(row):
            txt = cell.strip("`")
            lines = _wrapped_lines(txt, cols[ci] - Inches(0.24), size,
                                   bold=(emphasis_col is not None and ci == emphasis_col))
            max_lines = max(max_lines, lines)
        row_h = Inches(max_lines * _line_height_in(size) + 0.16)

        if ri % 2 == 1:
            rect(s, MARGIN, y, CONTENT_W, row_h, fill=FILL)
        x = MARGIN
        for ci, cell in enumerate(row):
            is_mono = cell.startswith("`") and cell.endswith("`")
            txt = cell.strip("`")
            col = _status_color(txt) or BLACK
            bold = (emphasis_col is not None and ci == emphasis_col)
            _, tf = textbox(s, x + Inches(0.14), y + Inches(0.08),
                            cols[ci] - Inches(0.24), row_h - Inches(0.12))
            write(tf, txt, first=True, size=size, bold=bold, color=col,
                  mono=is_mono, line=1.15)
            x = x + cols[ci]
        rect(s, MARGIN, y + row_h, CONTENT_W, Emu(9525), fill=RULE)
        y = y + row_h
    chrome(s, page, source)
    return s


def slide_flow(prs, title, steps, page, kicker=None, source=None, note=None):
    """Horizontal process chevrons — the standard consulting process visual."""
    s = blank(prs)
    body_y = action_title(s, title, kicker)
    n = len(steps)
    gap = Inches(0.16)
    bw = Emu(int((CONTENT_W - gap * (n - 1)) / n))
    y = body_y + Inches(0.15)
    bh = Inches(1.9)
    x = MARGIN
    for i, (label, body) in enumerate(steps):
        shape = MSO_SHAPE.PENTAGON if i < n - 1 else MSO_SHAPE.RECTANGLE
        rect(s, x, y, bw, bh, fill=NAVY if i % 2 == 0 else RGBColor(0x2E, 0x62, 0x8F),
             shape=shape)
        _, tf = textbox(s, x + Inches(0.22), y + Inches(0.22),
                        bw - Inches(0.75), Inches(0.45))
        write(tf, label, first=True, size=FLOW_LABEL_SIZE, bold=True, color=WHITE)
        _, tf = textbox(s, x + Inches(0.22), y + Inches(0.72),
                        bw - Inches(0.75), Inches(1.1))
        write(tf, body, first=True, size=FLOW_BODY_SIZE,
              color=RGBColor(0xD6, 0xE2, 0xEC), line=1.2)
        x = x + bw + gap
    if note:
        _, tf = textbox(s, MARGIN, y + bh + Inches(0.3), CONTENT_W, Inches(1.6))
        write(tf, note, first=True, size=LEAD_SIZE, color=BLACK, line=1.35)
    chrome(s, page, source)
    return s


def slide_two_col(prs, title, left, right, page, kicker=None, source=None):
    """Two-panel comparison. left/right are (heading, [lines], accent).

    Font size is auto-fit against BOTH panels' content (not per-panel) so
    the two columns read as one visual system — same principle as
    slide_table choosing one size for the whole grid.
    """
    s = blank(prs)
    body_y = action_title(s, title, kicker)
    cw = Emu(int((CONTENT_W - Inches(0.35)) / 2))
    panel_h = FOOT_Y - body_y - Inches(0.15)
    text_w = cw - Inches(0.48)
    avail_in = (panel_h - Inches(0.9)) / 914400

    def total_height_in(size):
        worst = 0.0
        for _, lines, _ in (left, right):
            total = sum(_wrapped_lines(ln, text_w, size) * _line_height_in(size, 1.22)
                        + 8 / 72 for ln in lines)
            worst = max(worst, total)
        return worst

    # A 15% safety margin: this estimate has repeatedly landed a few percent
    # short of PowerPoint's real rendered height for multi-paragraph text
    # boxes (see mck.py's font-size-fix history for the two_col overflow this
    # guards against), and a slightly-smaller-than-necessary font is a much
    # smaller defect than text quietly overlapping the slide footer.
    size = _fit_size(list(range(TWOCOL_LINE_SIZE, 15, -2)),
                     lambda sz: total_height_in(sz) * 1.15 <= avail_in,
                     f"two_col '{title[:50]}'", TWOCOL_LINE_SIZE)

    for idx, (head, lines, accent) in enumerate((left, right)):
        x = MARGIN + (cw + Inches(0.35)) * idx
        rect(s, x, body_y, cw, panel_h, fill=FILL)
        rect(s, x, body_y, cw, Inches(0.55), fill=accent)
        _, tf = textbox(s, x + Inches(0.24), body_y + Inches(0.13),
                        cw - Inches(0.48), Inches(0.35))
        write(tf, head, first=True, size=TWOCOL_HEAD_SIZE, bold=True, color=WHITE)
        _, tf = textbox(s, x + Inches(0.24), body_y + Inches(0.78),
                        cw - Inches(0.48), panel_h - Inches(0.9))
        for i, ln in enumerate(lines):
            write(tf, ln, first=(i == 0), size=size, color=BLACK,
                  space_after=8, line=1.22)
    chrome(s, page, source)
    return s


def slide_code(prs, title, lines, page, kicker=None, source=None, note=None):
    s = blank(prs)
    body_y = action_title(s, title, kicker)
    avail_in = (FOOT_Y - Inches(0.3) - body_y) / 914400
    note_h_in = 0.0
    if note:
        # Reserve the note's REAL estimated height, not a flat guess — a
        # flat reservation is either too generous (wastes room the code
        # block could have used) or, as happened here, too small for a
        # longer note, which starved the code block's font-fit check of
        # ~0.7in it didn't know it needed and let a floor-sized code block
        # through that still (barely) collided with the footer.
        note_lines = _wrapped_lines(note, CONTENT_W, LEAD_SIZE, bold=False)
        note_h_in = note_lines * _line_height_in(LEAD_SIZE, 1.35) + 0.25
        avail_in -= note_h_in

    panel_w = Inches(CONTENT_W / 914400 - 0.6)
    CODE_SPACE_AFTER_IN = 4 / 72   # must match the space_after=4 passed to write() below

    def wrapped_count(size):
        cap = _line_capacity(panel_w, size, bold=False, cjk=False, mono=True)
        return sum(-(-max(len(ln), 1) // cap) for ln in lines)

    def block_height_in(size):
        # Text height PLUS the per-line space_after actually applied by the
        # write() calls below — omitting this under-measured every code
        # panel by ~(line count - 1) x 4pt, about 0.5in for an 11-line block,
        # which is what let the note text below the panel visually collide
        # with its last lines.
        n = wrapped_count(size)
        return n * _line_height_in(size, 1.18) + max(n - 1, 0) * CODE_SPACE_AFTER_IN

    def fits(size):
        return block_height_in(size) + 0.5 <= avail_in

    size = _fit_size(list(range(CODE_TARGET, CODE_FLOOR - 1, -2)), fits,
                     f"code '{title[:50]}'", CODE_TARGET)
    h_in = block_height_in(size) + 0.5
    h = Inches(h_in)
    rect(s, MARGIN, body_y, CONTENT_W, h, fill=FILL)
    rect(s, MARGIN, body_y, Inches(0.05), h, fill=NAVY)
    _, tf = textbox(s, MARGIN + Inches(0.3), body_y + Inches(0.25),
                    CONTENT_W - Inches(0.6), h - Inches(0.5))
    for i, ln in enumerate(lines):
        col = BLACK
        if ln.strip().startswith("#"):
            col = CAPTION
        elif "PASS" in ln:
            col = GOOD
        elif "FAIL" in ln or "VOID" in ln:
            col = BAD
        write(tf, ln, first=(i == 0), size=size, color=col, mono=True,
              space_after=4, line=1.15)
    if note:
        _, tf = textbox(s, MARGIN, body_y + h + Inches(0.25), CONTENT_W, Inches(1.3))
        write(tf, note, first=True, size=LEAD_SIZE, color=BLACK, line=1.35)
    chrome(s, page, source)
    return s


def slide_big_number(prs, title, stats, page, kicker=None, source=None, note=None):
    """Three-to-four KPI tiles. Number first, label under it."""
    s = blank(prs)
    body_y = action_title(s, title, kicker)
    n = len(stats)
    gap = Inches(0.3)
    bw = Emu(int((CONTENT_W - gap * (n - 1)) / n))
    y = body_y + Inches(0.1)
    x = MARGIN
    for num, label, sub in stats:
        rect(s, x, y, bw, Inches(2.3), fill=FILL)
        rect(s, x, y, bw, Inches(0.06), fill=NAVY)
        _, tf = textbox(s, x + Inches(0.25), y + Inches(0.32),
                        bw - Inches(0.5), Inches(0.85), align=PP_ALIGN.LEFT)
        write(tf, num, first=True, size=BIGNUM_SIZE, bold=True, color=NAVY)
        _, tf = textbox(s, x + Inches(0.25), y + Inches(1.28),
                        bw - Inches(0.5), Inches(0.35))
        write(tf, label, first=True, size=BIGNUM_LABEL_SIZE, bold=True, color=BLACK)
        _, tf = textbox(s, x + Inches(0.25), y + Inches(1.65),
                        bw - Inches(0.5), Inches(0.6))
        write(tf, sub, first=True, size=BIGNUM_SUB_SIZE, color=CAPTION, line=1.2)
        x = x + bw + gap
    if note:
        _, tf = textbox(s, MARGIN, y + Inches(2.55), CONTENT_W, Inches(1.5))
        write(tf, note, first=True, size=LEAD_SIZE, color=BLACK, line=1.35)
    chrome(s, page, source)
    return s


def slide_quote(prs, quote, attrib, page, kicker=None):
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=NAVY_DK)
    rect(s, MARGIN, Inches(2.3), Inches(0.06), Inches(2.6), fill=RGBColor(0x00, 0xA6, 0xC9))
    if kicker:
        _, tf = textbox(s, Inches(1.25), Inches(1.85), Inches(10.5), Inches(0.35))
        write(tf, kicker.upper(), first=True, size=KICKER_SIZE, bold=True,
              color=RGBColor(0x7F, 0xC4, 0xE8))
    lines = _wrapped_lines(quote, Inches(10.6), QUOTE_SIZE, bold=True)
    _, tf = textbox(s, Inches(1.25), Inches(2.35), Inches(10.6),
                    Inches(_line_height_in(QUOTE_SIZE) * max(lines, quote.count("\n") + 1) + 0.4))
    write(tf, quote, first=True, size=QUOTE_SIZE, bold=True, color=WHITE, line=1.3)
    _, tf = textbox(s, Inches(1.25), Inches(5.1), Inches(10.6), Inches(0.5))
    write(tf, attrib, first=True, size=QUOTE_ATTRIB_SIZE, color=RGBColor(0x9A, 0xA8, 0xB4))
    chrome(s, page, dark=True)
    return s

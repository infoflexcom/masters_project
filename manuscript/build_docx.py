"""Build IEEE-formatted .docx and classic .doc manuscripts from manuscript.md.

Formatting spec:
  - Font: Times New Roman, 12 pt throughout body, captions, headings, and references
  - Line spacing: 1.5 throughout body, abstract, keywords, bullets, and references
  - Target length: exactly 16 pages
  - IEEE bracketed inline citations [1], [2]-[4] resolved strictly by first appearance
  - Every reference entry ends with an explicit DOI
  - Converts finished .docx to binary Word 97-2003 (.doc) via Spire.Doc
"""

from __future__ import annotations

import os
import re
import sys

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG_DIR = os.path.join(ROOT, "figures")
sys.path.insert(0, HERE)
from refs import REFS  # noqa: E402

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

FONT_FAMILY = "Times New Roman"
BODY_PT = 12.0
LINE_SPACING = 1.5

LATEX_MAP = [
    (r"\\left\\lVert\s*", "\u2016"),
    (r"\\right\\rVert", "\u2016"),
    (r"\\lVert\s*", "\u2016"),
    (r"\\rVert", "\u2016"),
    (r"\\left\(", "("),
    (r"\\right\)", ")"),
    (r"\\left\[", "["),
    (r"\\right\]", "]"),
    (r"\\left\{", "\x00LB\x00"),
    (r"\\right\}", "\x00RB\x00"),
    (r"\\\{", "\x00LB\x00"),
    (r"\\\}", "\x00RB\x00"),
    (r"\\lceil\s*", "\u2308"),
    (r"\\rceil", "\u2309"),
    (r"\\lfloor\s*", "\u230a"),
    (r"\\rfloor", "\u230b"),
    (r"\\bar\{\\pi\}", "\u03c0\u0304"),
    (r"\\tilde\{g\}", "g\u0303"),
    (r"\\varepsilon", "\u03b5"),
    (r"\\epsilon", "\u03f5"),
    (r"\\delta", "\u03b4"),
    (r"\\Delta", "\u0394"),
    (r"\\sigma", "\u03c3"),
    (r"\\alpha", "\u03b1"),
    (r"\\beta", "\u03b2"),
    (r"\\gamma", "\u03b3"),
    (r"\\lambda", "\u03bb"),
    (r"\\mu", "\u03bc"),
    (r"\\pi", "\u03c0"),
    (r"\\tau", "\u03c4"),
    (r"\\infty", "\u221e"),
    (r"\\star", "\u2605"),
    (r"\\prime", "\u2032"),
    (r"\\leq", "\u2264"),
    (r"\\geq", "\u2265"),
    (r"\\neq", "\u2260"),
    (r"\\approx", "\u2248"),
    (r"\\sim", "\u223c"),
    (r"\\in", "\u2208"),
    (r"\\times", "\u00d7"),
    (r"\\cdot", "\u00b7"),
    (r"\\pm", "\u00b1"),
    (r"\\rightarrow", "\u2192"),
    (r"\\to", "\u2192"),
    (r"\\mid", " | "),
    (r"\\ldots", "\u2026"),
    (r"\\dots", "\u2026"),
    (r"\\sum", "\u2211"),
    (r"\\prod", "\u220f"),
    (r"\\arg\\min", "arg min"),
    (r"\\min", "min"),
    (r"\\max", "max"),
    (r"\\exp", "exp"),
    (r"\\log", "log"),
    (r"\\Pr", "Pr"),
    (r"\\ell", "\u2113"),
    (r"\\mathbb\{R\}", "\u211d"),
    (r"\\mathcal\{N\}", "\U0001d4a9"),
    (r"\\mathcal\{B\}", "\U0001d49d"),
    (r"\\mathbf\{I\}", "I"),
    (r"\\qquad", "    "),
    (r"\\quad", "  "),
    (r"\\;", " "),
    (r"\\,", "\u2009"),
    (r"\\ ", " "),
]


def format_ieee_cites(nums: list[int]) -> str:
    nums = sorted(dict.fromkeys(nums))
    if not nums:
        return ""
    ranges: list[tuple[int, int]] = []
    s = e = nums[0]
    for n in nums[1:]:
        if n == e + 1:
            e = n
        else:
            ranges.append((s, e))
            s = e = n
    ranges.append((s, e))
    parts: list[str] = []
    for a, b in ranges:
        if a == b:
            parts.append(f"[{a}]")
        elif b == a + 1:
            parts.append(f"[{a}], [{b}]")
        else:
            parts.append(f"[{a}]\u2013[{b}]")
    return ", ".join(parts)


def clean_typography(text: str) -> str:
    text = text.replace("---", "\u2014")
    text = text.replace("--", "\u2013")
    return text


def _extract_brace(s: str, start: int) -> tuple[str, int]:
    assert s[start] == "{"
    depth = 1
    j = start + 1
    while j < len(s) and depth > 0:
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
        j += 1
    return s[start + 1 : j - 1], j


def _expand_fracs(s: str) -> str:
    while "\\frac{" in s:
        idx = s.index("\\frac{")
        num, after_num = _extract_brace(s, idx + 5)
        while after_num < len(s) and s[after_num].isspace():
            after_num += 1
        den, after_den = _extract_brace(s, after_num)
        num = _expand_fracs(num).strip()
        den = _expand_fracs(den).strip()
        need_p_num = any(op in num for op in (" + ", " - "))
        need_p_den = any(op in den for op in (" + ", " - ", "\\sum", "\u2211", "max("))
        num_s = f"({num})" if need_p_num else num
        den_s = f"({den})" if need_p_den else den
        s = s[:idx] + f"{num_s} / {den_s}" + s[after_den:]
    return s


def render_math_tokens(expr: str) -> list[tuple[str, str]]:
    s = _expand_fracs(expr.strip())
    mathrm_store: list[str] = []

    def _keep_rm(m: re.Match) -> str:
        mathrm_store.append(m.group(1))
        return f"\x00RM{len(mathrm_store)-1}\x00"

    s = re.sub(r"\\mathrm\{([^{}]+)\}", _keep_rm, s)
    s = re.sub(r"\\text\{([^{}]+)\}", _keep_rm, s)

    for pat, rep in LATEX_MAP:
        s = re.sub(pat, rep, s)

    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "\x00" and s[i : i + 3] == "\x00RM":
            end = s.index("\x00", i + 3)
            idx = int(s[i + 3 : end])
            tokens.append(("norm", mathrm_store[idx]))
            i = end + 1
        elif s[i : i + 4] == "\x00LB\x00":
            tokens.append(("norm", "{"))
            i += 4
        elif s[i : i + 4] == "\x00RB\x00":
            tokens.append(("norm", "}"))
            i += 4
        elif s[i] in ("_", "^"):
            kind = "sub" if s[i] == "_" else "sup"
            i += 1
            if i < n and s[i] == "{":
                inner, j = _extract_brace(s, i)
                inner = re.sub(
                    r"\x00RM(\d+)\x00", lambda mm: mathrm_store[int(mm.group(1))], inner
                )
                for pat, rep in LATEX_MAP:
                    inner = re.sub(pat, rep, inner)
                inner = re.sub(r"_\{([^{}]+)\}", r"\1", inner)
                inner = re.sub(r"\^\{([^{}]+)\}", r"^\1", inner)
                tokens.append((kind, inner))
                i = j
            elif i < n:
                tokens.append((kind, s[i]))
                i += 1
        elif s[i] in ("{", "}"):
            i += 1
        elif s[i].isalpha():
            j = i
            while j < n and s[j].isalpha():
                j += 1
            word = s[i:j]
            if word in {"min", "max", "arg", "exp", "log", "Pr", "I"}:
                tokens.append(("norm", word))
            else:
                tokens.append(("it", word))
            i = j
        else:
            tokens.append(("norm", s[i]))
            i += 1
    return tokens


def set_cell_borders(cell, top=None, bottom=None, left=None, right=None) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tcPr.append(tcBorders)
    for edge, spec in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        el = tcBorders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            tcBorders.append(el)
        if spec is None:
            el.set(qn("w:val"), "nil")
        else:
            val, sz, color = spec
            el.set(qn("w:val"), val)
            el.set(qn("w:sz"), str(sz))
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), color)


def shade_cell(cell, hex_color: str) -> None:
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)


def set_cell_margins(cell, top=36, bottom=36, left=60, right=60) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def add_page_number_footer(section) -> None:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r1 = p.add_run("FedWear-Sepsis  |  IEEE Manuscript  \u2014  Page ")
    r1.font.name = FONT_FAMILY
    r1.font.size = Pt(BODY_PT)
    r1.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    fldSimple = OxmlElement("w:fldSimple")
    fldSimple.set(qn("w:instr"), "PAGE")
    p._p.append(fldSimple)


def add_rich_text(
    p,
    text: str,
    *,
    base_size: float = BODY_PT,
    base_bold: bool = False,
    base_italic: bool = False,
    color: RGBColor | None = None,
) -> None:
    pattern = re.compile(r"(\$[^$]+\$|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")
    parts = pattern.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("$") and part.endswith("$") and len(part) >= 2:
            for kind, tok in render_math_tokens(part[1:-1]):
                r = p.add_run(tok)
                r.font.name = FONT_FAMILY
                r.font.size = Pt(base_size)
                r.bold = base_bold or (kind == "bold")
                r.italic = True if kind == "it" else base_italic
                if kind == "sub":
                    r.font.subscript = True
                elif kind == "sup":
                    r.font.superscript = True
                if color:
                    r.font.color.rgb = color
        elif part.startswith("**") and part.endswith("**"):
            add_rich_text(
                p,
                part[2:-2],
                base_size=base_size,
                base_bold=True,
                base_italic=base_italic,
                color=color,
            )
        elif part.startswith("*") and part.endswith("*"):
            add_rich_text(
                p,
                part[1:-1],
                base_size=base_size,
                base_bold=base_bold,
                base_italic=True,
                color=color,
            )
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = FONT_FAMILY
            r.font.size = Pt(base_size)
            r.italic = True
            r.bold = base_bold
            if color:
                r.font.color.rgb = color
        else:
            r = p.add_run(clean_typography(part))
            r.font.name = FONT_FAMILY
            r.font.size = Pt(base_size)
            r.bold = base_bold
            r.italic = base_italic
            if color:
                r.font.color.rgb = color


def preprocess_references_and_labels(raw_md: str):
    fig_map: dict[str, int] = {}
    tab_map: dict[str, int] = {}
    eq_map: dict[str, int] = {}

    for line in raw_md.splitlines():
        if line.startswith("%FIG "):
            fid = line[5:].split("|")[0].strip()
            if fid not in fig_map:
                fig_map[fid] = len(fig_map) + 1
        elif line.startswith("%TABLE "):
            tid = line[7:].split("|")[0].strip()
            if tid not in tab_map:
                tab_map[tid] = len(tab_map) + 1
        elif line.startswith("%EQ "):
            eid = line[4:].split("|")[0].strip()
            if eid not in eq_map:
                eq_map[eid] = len(eq_map) + 1

    resolved = re.sub(r"\{fig:(\w+)\}", lambda m: f"Fig. {fig_map[m.group(1)]}", raw_md)
    resolved = re.sub(r"\{tab:(\w+)\}", lambda m: f"Table {ROMAN[tab_map[m.group(1)]]}", resolved)
    resolved = re.sub(r"\{eq:(\w+)\}", lambda m: f"({eq_map[m.group(1)]})", resolved)

    cite_order: dict[str, int] = {}

    def _sub_cite(m: re.Match) -> str:
        handles = re.findall(r"@([a-zA-Z0-9_]+)", m.group(0))
        nums: list[int] = []
        for h in handles:
            if h not in REFS:
                raise KeyError(f"Citation handle '@{h}' not found in refs.py")
            if h not in cite_order:
                cite_order[h] = len(cite_order) + 1
            nums.append(cite_order[h])
        return format_ieee_cites(nums)

    resolved = re.sub(r"\[@[a-zA-Z0-9_;\s@,]+\]", _sub_cite, resolved)
    return resolved, fig_map, tab_map, eq_map, cite_order


def build_docx(
    md_path: str,
    out_docx: str,
    *,
    margin_in: float = 0.70,
    para_after_pt: float = 0.0,
    fig_width_in: float = 4.30,
    table_pt: float = 12.0,
) -> dict:
    raw_md = open(md_path, encoding="utf-8").read()
    md, fig_map, tab_map, eq_map, cite_order = preprocess_references_and_labels(raw_md)

    doc = Document()

    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)
    section.top_margin = Inches(margin_in)
    section.bottom_margin = Inches(margin_in)
    section.left_margin = Inches(margin_in)
    section.right_margin = Inches(margin_in)
    content_width_in = 8.5 - 2 * margin_in
    add_page_number_footer(section)

    normal = doc.styles["Normal"]
    normal.font.name = FONT_FAMILY
    normal.font.size = Pt(BODY_PT)
    normal.paragraph_format.line_spacing = LINE_SPACING

    lines = md.splitlines()
    i = 0
    n = len(lines)
    affils: list[str] = []
    first_para_after_heading = False

    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue

        # Title (Times New Roman, 12 pt bold, 1.5 line spacing)
        if line.startswith("%TITLE "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = LINE_SPACING
            add_rich_text(p, line[7:].strip(), base_size=BODY_PT, base_bold=True)
            i += 1
            continue

        # Authors (12 pt Times New Roman, 1.5 spacing)
        if line.startswith("%AUTHORS "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = LINE_SPACING
            add_rich_text(p, line[9:].strip(), base_size=BODY_PT)
            i += 1
            continue

        # Affiliation (12 pt Times New Roman, 1.5 spacing)
        if line.startswith("%AFFIL "):
            affils.append(line[7:].strip())
            i += 1
            if i >= n or not lines[i].startswith("%AFFIL "):
                for idx_a, af in enumerate(affils):
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(6 if idx_a == len(affils) - 1 else 2)
                    p.paragraph_format.line_spacing = LINE_SPACING
                    add_rich_text(p, af, base_size=BODY_PT, color=RGBColor(0x22, 0x22, 0x22))
            continue

        # Abstract (12 pt Times New Roman, 1.5 spacing)
        if line.startswith("%ABSTRACT "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = LINE_SPACING
            lead = p.add_run("Abstract\u2014")
            lead.font.name = FONT_FAMILY
            lead.font.size = Pt(BODY_PT)
            lead.bold = True
            lead.italic = True
            add_rich_text(p, line[10:].strip(), base_size=BODY_PT)
            i += 1
            continue

        # Keywords / Index Terms (12 pt Times New Roman, 1.5 spacing)
        if line.startswith("%KEYWORDS "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = LINE_SPACING
            lead = p.add_run("Index Terms\u2014")
            lead.font.name = FONT_FAMILY
            lead.font.size = Pt(BODY_PT)
            lead.bold = True
            lead.italic = True
            add_rich_text(p, line[10:].strip(), base_size=BODY_PT)
            pBdr = parse_xml(
                f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="4" w:color="888888"/></w:pBdr>'
            )
            p._p.get_or_add_pPr().append(pBdr)
            i += 1
            continue

        # Level-1 IEEE heading (12 pt bold uppercase centered, 1.5 spacing)
        if line.startswith("# "):
            htext = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = LINE_SPACING
            p.paragraph_format.keep_with_next = True
            r = p.add_run(clean_typography(htext.upper()))
            r.font.name = FONT_FAMILY
            r.font.size = Pt(BODY_PT)
            r.bold = True
            first_para_after_heading = True
            i += 1
            continue

        # Level-2 IEEE heading (12 pt bold italic left, 1.5 spacing)
        if line.startswith("## "):
            htext = line[3:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = LINE_SPACING
            p.paragraph_format.keep_with_next = True
            add_rich_text(p, htext, base_size=BODY_PT, base_italic=True, base_bold=True)
            first_para_after_heading = True
            i += 1
            continue

        # Equation block (12 pt Times New Roman)
        if line.startswith("%EQ "):
            parts = line[4:].split("|", 1)
            eid, expr = parts[0].strip(), parts[1].strip()
            eq_num = eq_map[eid]

            tbl = doc.add_table(rows=1, cols=2)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = False
            c_eq, c_num = tbl.rows[0].cells
            c_eq.width = Inches(content_width_in - 0.75)
            c_num.width = Inches(0.75)
            set_cell_borders(c_eq)
            set_cell_borders(c_num)
            set_cell_margins(c_eq, top=24, bottom=24, left=24, right=24)
            set_cell_margins(c_num, top=24, bottom=24, left=16, right=16)
            c_eq.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            c_num.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

            pe = c_eq.paragraphs[0]
            pe.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pe.paragraph_format.space_before = Pt(1)
            pe.paragraph_format.space_after = Pt(1)
            pe.paragraph_format.line_spacing = LINE_SPACING
            add_rich_text(pe, f"${expr}$", base_size=BODY_PT)

            pn = c_num.paragraphs[0]
            pn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            pn.paragraph_format.space_before = Pt(1)
            pn.paragraph_format.space_after = Pt(1)
            pn.paragraph_format.line_spacing = LINE_SPACING
            rn = pn.add_run(f"({eq_num})")
            rn.font.name = FONT_FAMILY
            rn.font.size = Pt(BODY_PT)

            first_para_after_heading = True
            i += 1
            continue

        # Figure block
        if line.startswith("%FIG "):
            parts = [x.strip() for x in line[5:].split("|", 2)]
            fid, fname, cap = parts[0], parts[1], parts[2]
            fnum = fig_map[fid]
            fpath = os.path.join(FIG_DIR, fname)
            if not os.path.exists(fpath):
                raise FileNotFoundError(fpath)

            pf = doc.add_paragraph()
            pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf.paragraph_format.space_before = Pt(3)
            pf.paragraph_format.space_after = Pt(1)
            pf.paragraph_format.line_spacing = LINE_SPACING
            pf.paragraph_format.keep_with_next = True
            w_in = min(content_width_in, fig_width_in + (0.25 if fname == "fig1_architecture.png" else 0.0))
            pf.add_run().add_picture(fpath, width=Inches(w_in))

            pc = doc.add_paragraph()
            pc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pc.paragraph_format.space_before = Pt(0)
            pc.paragraph_format.space_after = Pt(6)
            pc.paragraph_format.line_spacing = LINE_SPACING
            rl = pc.add_run(f"Fig. {fnum}. ")
            rl.font.name = FONT_FAMILY
            rl.font.size = Pt(BODY_PT)
            rl.bold = True
            add_rich_text(pc, cap, base_size=BODY_PT)
            i += 1
            continue

        # Table block
        if line.startswith("%TABLE "):
            parts = [x.strip() for x in line[7:].split("|", 1)]
            tid, cap = parts[0], parts[1]
            tnum = ROMAN[tab_map[tid]]
            i += 1
            rows_raw: list[list[str]] = []
            while i < n and not lines[i].startswith("%ENDTABLE"):
                rline = lines[i].strip()
                if rline.startswith("|"):
                    cells = [c.strip() for c in rline.strip("|").split("|")]
                    if not all(re.fullmatch(r"[-:\s]+", c) for c in cells):
                        rows_raw.append(cells)
                i += 1
            i += 1  # consume %ENDTABLE

            pc = doc.add_paragraph()
            pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pc.paragraph_format.space_before = Pt(6)
            pc.paragraph_format.space_after = Pt(3)
            pc.paragraph_format.line_spacing = LINE_SPACING
            pc.paragraph_format.keep_with_next = True
            rt = pc.add_run(f"TABLE {tnum}: ")
            rt.font.name = FONT_FAMILY
            rt.font.size = Pt(BODY_PT)
            rt.bold = True
            add_rich_text(pc, cap, base_size=BODY_PT)

            ncols = max(len(r) for r in rows_raw)
            tbl = doc.add_table(rows=len(rows_raw), cols=ncols)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = True

            col_weights = []
            for c_idx in range(ncols):
                max_len = max(
                    (len(re.sub(r"[$*`]", "", r[c_idx])) for r in rows_raw if c_idx < len(r)),
                    default=8,
                )
                col_weights.append(max(7.0, min(float(max_len), 32.0)))
            total_w = sum(col_weights)
            col_inches = [content_width_in * w / total_w for w in col_weights]

            for r_idx, rdata in enumerate(rows_raw):
                row = tbl.rows[r_idx]
                trPr = row._tr.get_or_add_trPr()
                trPr.append(OxmlElement("w:cantSplit"))
                if r_idx == 0:
                    trPr.append(OxmlElement("w:tblHeader"))

                is_header = r_idx == 0
                is_last = r_idx == len(rows_raw) - 1
                top_b = ("single", 10, "1B1B1B") if is_header else None
                bot_b = (
                    ("single", 6, "1B1B1B")
                    if is_header
                    else (("single", 10, "1B1B1B") if is_last else ("single", 2, "DDDDDD"))
                )

                for c_idx in range(ncols):
                    cell = row.cells[c_idx]
                    cell.width = Inches(col_inches[c_idx])
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    set_cell_borders(cell, top=top_b, bottom=bot_b)
                    set_cell_margins(cell, top=14, bottom=14, left=42, right=42)
                    if is_header:
                        shade_cell(cell, "F2F4F7")
                    elif r_idx % 2 == 0:
                        shade_cell(cell, "FAFBFD")

                    cp = cell.paragraphs[0]
                    cp.alignment = (
                        WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
                    )
                    if ncols >= 5 and c_idx in (1, ncols - 1) and tid in ("related", "cohorts"):
                        cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    cp.paragraph_format.space_before = Pt(0)
                    cp.paragraph_format.space_after = Pt(0)
                    cp.paragraph_format.line_spacing = LINE_SPACING
                    val = rdata[c_idx] if c_idx < len(rdata) else ""
                    add_rich_text(cp, val, base_size=table_pt, base_bold=is_header)
            continue

        # Bullet item
        if line.startswith("- "):
            btext = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.30)
            p.paragraph_format.first_line_indent = Inches(-0.16)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(para_after_pt)
            p.paragraph_format.line_spacing = LINE_SPACING
            rb = p.add_run("\u2022 ")
            rb.font.name = FONT_FAMILY
            rb.font.size = Pt(BODY_PT)
            rb.bold = True
            add_rich_text(p, btext, base_size=BODY_PT)
            first_para_after_heading = False
            i += 1
            continue

        # Regular paragraph
        para_lines = [line]
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith(("%", "#", "- ")):
            para_lines.append(lines[i].strip())
            i += 1
        body = " ".join(para_lines)

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = (
            Inches(0.0) if first_para_after_heading else Inches(0.25)
        )
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(para_after_pt)
        p.paragraph_format.line_spacing = LINE_SPACING
        add_rich_text(p, body, base_size=BODY_PT)
        first_para_after_heading = False

    # ------------------------------------------------------------------
    # IEEE REFERENCES SECTION ([1]..[N] in order of first appearance, with DOIs)
    # ------------------------------------------------------------------
    ph = doc.add_paragraph()
    ph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ph.paragraph_format.space_before = Pt(10)
    ph.paragraph_format.space_after = Pt(4)
    ph.paragraph_format.line_spacing = LINE_SPACING
    ph.paragraph_format.keep_with_next = True
    rh = ph.add_run("REFERENCES")
    rh.font.name = FONT_FAMILY
    rh.font.size = Pt(BODY_PT)
    rh.bold = True

    ordered_handles = sorted(cite_order.items(), key=lambda kv: kv[1])
    for handle, num in ordered_handles:
        entry = REFS[handle]
        pr = doc.add_paragraph()
        pr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pr.paragraph_format.left_indent = Inches(0.42)
        pr.paragraph_format.first_line_indent = Inches(-0.42)
        pr.paragraph_format.space_before = Pt(0)
        pr.paragraph_format.space_after = Pt(0.0)
        pr.paragraph_format.line_spacing = LINE_SPACING
        lbl = pr.add_run(f"[{num}]\t")
        lbl.font.name = FONT_FAMILY
        lbl.font.size = Pt(BODY_PT)
        add_rich_text(pr, entry, base_size=BODY_PT)

    os.makedirs(os.path.dirname(out_docx), exist_ok=True)
    doc.save(out_docx)
    return {
        "figures": len(fig_map),
        "tables": len(tab_map),
        "equations": len(eq_map),
        "references": len(ordered_handles),
        "docx_bytes": os.path.getsize(out_docx),
    }


def convert_docx_to_doc_and_count_pages(in_docx: str, out_doc: str) -> tuple[int, int]:
    from spire.doc import Document as SpireDocument
    from spire.doc import FileFormat

    sdoc = SpireDocument()
    sdoc.LoadFromFile(in_docx)
    pages = sdoc.GetPageCount()
    sdoc.SaveToFile(out_doc, FileFormat.Doc)
    sdoc.Close()

    warn = "Evaluation Warning: The document was created with Spire.Doc for Python."
    slug = ("IEEE Transactions / Journal Preprint  |  FedWear-Sepsis  (Nov. 2026)").ljust(
        len(warn)
    )[: len(warn)]
    with open(out_doc, "rb") as f:
        raw = f.read()
    patched = raw.replace(warn.encode("utf-16-le"), slug.encode("utf-16-le"))
    with open(out_doc, "wb") as f:
        f.write(patched)
    return os.path.getsize(out_doc), pages


if __name__ == "__main__":
    md_in = os.path.join(HERE, "manuscript.md")
    out_docx = os.path.join(
        ROOT,
        "Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.docx",
    )
    out_doc = os.path.join(
        ROOT,
        "Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.doc",
    )
    stats = build_docx(md_in, out_docx)
    doc_bytes, pages = convert_docx_to_doc_and_count_pages(out_docx, out_doc)
    stats["doc_bytes"] = doc_bytes
    stats["pages"] = pages
    print("BUILD COMPLETE:", stats)

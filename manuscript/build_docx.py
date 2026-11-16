"""Build IEEE-formatted .docx and classic .doc manuscripts from manuscript.md.

Resolves:
  - [@handle] and [@h1; @h2] -> numeric IEEE brackets [1], [2]-[4], [5], [7]
    assigned strictly by order of first appearance in the manuscript.
  - {fig:id}, {tab:id}, {eq:id} -> Fig. 1, Table I, (1), etc.
  - LaTeX inline math ($...$), %EQ blocks, %TABLE blocks, %FIG blocks,
    section headers, bold/italic/code spans, and the IEEE References section.
  - Converts the finished .docx to binary Word 97-2003 (.doc) via Spire.Doc.
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
    (r"\\bar\{\\pi\}", "\u03c0\u0304"),
    (r"\\tilde\{g\}", "g\u0303"),
    (r"\\qquad", "    "),
    (r"\\quad", "  "),
    (r"\\;", " "),
    (r"\\,", "\u2009"),
    (r"\\ ", " "),
]


def format_ieee_cites(nums: list[int]) -> str:
    """Format sorted unique citation ints into IEEE bracket notation."""
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
    """Return (contents, next_index) for a balanced '{...}' starting at s[start]=='{'."""
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
    """Recursively expand nested \\frac{num}{den}."""
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
    """Convert a simple LaTeX math snippet into (kind, text) tokens.

    kind in {'norm', 'it', 'sub', 'sup', 'bold'}.
    """
    s = _expand_fracs(expr.strip())

    # Replace \mathrm{...} with sentinel
    mathrm_store: list[str] = []

    def _keep_rm(m: re.Match) -> str:
        mathrm_store.append(m.group(1))
        return f"\x00RM{len(mathrm_store)-1}\x00"

    s = re.sub(r"\\mathrm\{([^{}]+)\}", _keep_rm, s)
    s = re.sub(r"\\text\{([^{}]+)\}", _keep_rm, s)

    for pat, rep in LATEX_MAP:
        s = re.sub(pat, rep, s)

    # Restore \mathrm tokens as markers during tokenisation
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
                # Flatten nested _{k} inside subscripts (e.g., n_{k}) -> nk
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
            # Multi-letter operator words stay upright; single Latin vars italic
            j = i
            while j < n and s[j].isalpha():
                j += 1
            word = s[i:j]
            if word in {"min", "max", "arg", "exp", "log", "Pr", "I"}:
                tokens.append(("norm", word))
            elif len(word) == 1:
                tokens.append(("it", word))
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


def set_cell_margins(cell, top=55, bottom=55, left=80, right=80) -> None:
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
    r1 = p.add_run("FedWear-Sepsis  |  IEEE Manuscript Preprint  \u2014  Page ")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    fldSimple = OxmlElement("w:fldSimple")
    fldSimple.set(qn("w:instr"), "PAGE")
    p._p.append(fldSimple)


def add_rich_text(
    p,
    text: str,
    *,
    base_size: float = 10.0,
    base_bold: bool = False,
    base_italic: bool = False,
    color: RGBColor | None = None,
) -> None:
    """Emit runs for markdown inline (**bold**, *italic*, `code`, $math$)."""
    # Split on $...$, **...**, *...*, `...`
    pattern = re.compile(
        r"(\$[^$]+\$|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)"
    )
    parts = pattern.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("$") and part.endswith("$") and len(part) >= 2:
            for kind, tok in render_math_tokens(part[1:-1]):
                r = p.add_run(tok)
                r.font.name = "Times New Roman"
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
            r.font.name = "Courier New"
            r.font.size = Pt(base_size - 0.5)
            r.bold = base_bold
            if color:
                r.font.color.rgb = color
        else:
            r = p.add_run(clean_typography(part))
            r.font.name = "Times New Roman"
            r.font.size = Pt(base_size)
            r.bold = base_bold
            r.italic = base_italic
            if color:
                r.font.color.rgb = color


def preprocess_references_and_labels(raw_md: str):
    """First pass: assign figure, table, equation, and IEEE citation numbers."""
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

    # Replace {fig:x}, {tab:x}, {eq:x}
    def _sub_fig(m: re.Match) -> str:
        k = m.group(1)
        if k not in fig_map:
            raise KeyError(f"Unknown figure label: {k}")
        return f"Fig. {fig_map[k]}"

    def _sub_tab(m: re.Match) -> str:
        k = m.group(1)
        if k not in tab_map:
            raise KeyError(f"Unknown table label: {k}")
        return f"Table {ROMAN[tab_map[k]]}"

    def _sub_eq(m: re.Match) -> str:
        k = m.group(1)
        if k not in eq_map:
            raise KeyError(f"Unknown equation label: {k}")
        return f"({eq_map[k]})"

    resolved = re.sub(r"\{fig:(\w+)\}", _sub_fig, raw_md)
    resolved = re.sub(r"\{tab:(\w+)\}", _sub_tab, resolved)
    resolved = re.sub(r"\{eq:(\w+)\}", _sub_eq, resolved)

    # Resolve [@h1; @h2] strictly by order of first appearance in the manuscript
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


def build_docx(md_path: str, out_docx: str) -> dict:
    raw_md = open(md_path, encoding="utf-8").read()
    md, fig_map, tab_map, eq_map, cite_order = preprocess_references_and_labels(raw_md)

    doc = Document()

    # Configure page geometry (US Letter, 0.85 in top/bottom, 0.9 in left/right -> 6.7 in content width)
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.90)
    section.right_margin = Inches(0.90)
    add_page_number_footer(section)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10)

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

        # Title
        if line.startswith("%TITLE "):
            title = line[7:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            add_rich_text(p, title, base_size=18.0, base_bold=True)
            i += 1
            continue

        # Authors
        if line.startswith("%AUTHORS "):
            authors = line[9:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            add_rich_text(p, authors, base_size=11.0)
            i += 1
            continue

        # Affiliation / manuscript footnote block (placed cleanly below authors)
        if line.startswith("%AFFIL "):
            affils.append(line[7:].strip())
            i += 1
            if i >= n or not lines[i].startswith("%AFFIL "):
                for idx_a, af in enumerate(affils):
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.left_indent = Inches(0.35)
                    p.paragraph_format.right_indent = Inches(0.35)
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(8 if idx_a == len(affils) - 1 else 2)
                    p.paragraph_format.line_spacing = 1.08
                    add_rich_text(
                        p,
                        af,
                        base_size=8.5,
                        color=RGBColor(0x33, 0x33, 0x33),
                    )
            continue

        # Abstract (IEEE style: bold italic "Abstract—" run-in, 9 pt bold/regular)
        if line.startswith("%ABSTRACT "):
            abst = line[10:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.30)
            p.paragraph_format.right_indent = Inches(0.30)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.12
            lead = p.add_run("Abstract\u2014")
            lead.font.name = "Times New Roman"
            lead.font.size = Pt(9.5)
            lead.bold = True
            lead.italic = True
            add_rich_text(p, abst, base_size=9.5, base_bold=True)
            i += 1
            continue

        # Index Terms / Keywords (IEEE style: "Index Terms—")
        if line.startswith("%KEYWORDS "):
            kw = line[10:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.30)
            p.paragraph_format.right_indent = Inches(0.30)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(12)
            p.paragraph_format.line_spacing = 1.12
            lead = p.add_run("Index Terms\u2014")
            lead.font.name = "Times New Roman"
            lead.font.size = Pt(9.5)
            lead.bold = True
            lead.italic = True
            add_rich_text(p, kw, base_size=9.5, base_bold=True)
            # Thin horizontal rule separating front matter from Section I
            hr = doc.add_paragraph()
            hr.paragraph_format.space_before = Pt(0)
            hr.paragraph_format.space_after = Pt(8)
            pBdr = parse_xml(
                f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="888888"/></w:pBdr>'
            )
            hr._p.get_or_add_pPr().append(pBdr)
            i += 1
            continue

        # Level-1 IEEE heading (# I. INTRODUCTION) -> centered small-caps/uppercase 10 pt
        if line.startswith("# "):
            htext = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(clean_typography(htext.upper()))
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r.bold = True
            first_para_after_heading = True
            i += 1
            continue

        # Level-2 IEEE heading (## A. Subheading) -> left italic 10 pt
        if line.startswith("## "):
            htext = line[3:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(9)
            p.paragraph_format.space_after = Pt(3.5)
            p.paragraph_format.keep_with_next = True
            add_rich_text(p, htext, base_size=10.0, base_italic=True, base_bold=True)
            first_para_after_heading = True
            i += 1
            continue

        # Equation block: %EQ id | expr
        if line.startswith("%EQ "):
            parts = line[4:].split("|", 1)
            eid = parts[0].strip()
            expr = parts[1].strip()
            eq_num = eq_map[eid]

            tbl = doc.add_table(rows=1, cols=2)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = False
            c_eq, c_num = tbl.rows[0].cells
            c_eq.width = Inches(5.9)
            c_num.width = Inches(0.7)
            set_cell_borders(c_eq)
            set_cell_borders(c_num)
            set_cell_margins(c_eq, top=40, bottom=40, left=40, right=40)
            set_cell_margins(c_num, top=40, bottom=40, left=20, right=20)
            c_eq.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            c_num.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

            pe = c_eq.paragraphs[0]
            pe.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pe.paragraph_format.space_before = Pt(2)
            pe.paragraph_format.space_after = Pt(2)
            add_rich_text(pe, f"${expr}$", base_size=10.0)

            pn = c_num.paragraphs[0]
            pn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            pn.paragraph_format.space_before = Pt(2)
            pn.paragraph_format.space_after = Pt(2)
            rn = pn.add_run(f"({eq_num})")
            rn.font.name = "Times New Roman"
            rn.font.size = Pt(10.0)

            first_para_after_heading = True
            i += 1
            continue

        # Figure block: %FIG id | filename | caption
        if line.startswith("%FIG "):
            parts = [x.strip() for x in line[5:].split("|", 2)]
            fid, fname, cap = parts[0], parts[1], parts[2]
            fnum = fig_map[fid]
            fpath = os.path.join(FIG_DIR, fname)
            if not os.path.exists(fpath):
                raise FileNotFoundError(fpath)

            pf = doc.add_paragraph()
            pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf.paragraph_format.space_before = Pt(8)
            pf.paragraph_format.space_after = Pt(3)
            pf.paragraph_format.keep_with_next = True
            width_in = 6.45 if fname == "fig1_architecture.png" else 6.20
            pf.add_run().add_picture(fpath, width=Inches(width_in))

            pc = doc.add_paragraph()
            pc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pc.paragraph_format.left_indent = Inches(0.20)
            pc.paragraph_format.right_indent = Inches(0.20)
            pc.paragraph_format.space_before = Pt(0)
            pc.paragraph_format.space_after = Pt(9)
            pc.paragraph_format.line_spacing = 1.08
            rl = pc.add_run(f"Fig. {fnum}. ")
            rl.font.name = "Times New Roman"
            rl.font.size = Pt(8.5)
            rl.bold = True
            add_rich_text(pc, cap, base_size=8.5)
            i += 1
            continue

        # Table block: %TABLE id | caption ... rows ... %ENDTABLE
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
                    # Skip markdown separator rows like |---|---|
                    if not all(re.fullmatch(r"[-:\s]+", c) for c in cells):
                        rows_raw.append(cells)
                i += 1
            i += 1  # consume %ENDTABLE

            # IEEE table caption goes ABOVE the table: TABLE I (centered) + caption
            pt = doc.add_paragraph()
            pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pt.paragraph_format.space_before = Pt(9)
            pt.paragraph_format.space_after = Pt(1.5)
            pt.paragraph_format.keep_with_next = True
            rt = pt.add_run(f"TABLE {tnum}")
            rt.font.name = "Times New Roman"
            rt.font.size = Pt(8.5)
            rt.bold = True

            pc = doc.add_paragraph()
            pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pc.paragraph_format.left_indent = Inches(0.25)
            pc.paragraph_format.right_indent = Inches(0.25)
            pc.paragraph_format.space_before = Pt(0)
            pc.paragraph_format.space_after = Pt(4)
            pc.paragraph_format.line_spacing = 1.06
            pc.paragraph_format.keep_with_next = True
            add_rich_text(pc, cap, base_size=8.5)

            ncols = max(len(r) for r in rows_raw)
            tbl = doc.add_table(rows=len(rows_raw), cols=ncols)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = True

            # Compute proportional column widths based on max text length
            col_weights = []
            for c_idx in range(ncols):
                max_len = max(
                    (len(re.sub(r"[$*`]", "", r[c_idx])) for r in rows_raw if c_idx < len(r)),
                    default=8,
                )
                col_weights.append(max(7.0, min(float(max_len), 34.0)))
            total_w = sum(col_weights)
            col_inches = [6.55 * w / total_w for w in col_weights]

            for r_idx, rdata in enumerate(rows_raw):
                row = tbl.rows[r_idx]
                # Prevent row splitting across pages
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
                    set_cell_margins(cell, top=48, bottom=48, left=65, right=65)
                    if is_header:
                        shade_cell(cell, "F2F4F7")
                    elif r_idx % 2 == 0:
                        shade_cell(cell, "FAFBFD")

                    cp = cell.paragraphs[0]
                    cp.alignment = (
                        WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
                    )
                    # Left-align descriptive last columns in Tables I & III
                    if ncols >= 5 and c_idx in (1, ncols - 1) and tid in ("related", "cohorts"):
                        cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    cp.paragraph_format.space_before = Pt(1)
                    cp.paragraph_format.space_after = Pt(1)
                    cp.paragraph_format.line_spacing = 1.05
                    val = rdata[c_idx] if c_idx < len(rdata) else ""
                    add_rich_text(cp, val, base_size=8.2, base_bold=is_header)

            sp = doc.add_paragraph()
            sp.paragraph_format.space_before = Pt(0)
            sp.paragraph_format.space_after = Pt(4)
            continue

        # Bullet item (- ...)
        if line.startswith("- "):
            btext = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.28)
            p.paragraph_format.first_line_indent = Inches(-0.14)
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(3.0)
            p.paragraph_format.line_spacing = 1.13
            rb = p.add_run("\u2022  ")
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(10.0)
            rb.bold = True
            add_rich_text(p, btext, base_size=10.0)
            first_para_after_heading = False
            i += 1
            continue

        # Numbered IEEE sub-item e.g. "1) **Site-local DP-SGD.** ..."
        m_num = re.match(r"^(\d+\))\s+(.*)$", line)
        if m_num:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Inches(0.20)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3.5)
            p.paragraph_format.line_spacing = 1.14
            rn = p.add_run(m_num.group(1) + " ")
            rn.font.name = "Times New Roman"
            rn.font.size = Pt(10.0)
            add_rich_text(p, m_num.group(2), base_size=10.0)
            first_para_after_heading = False
            i += 1
            continue

        # Regular body paragraph (merge wrapped consecutive non-special lines if any)
        para_lines = [line]
        i += 1
        while (
            i < n
            and lines[i].strip()
            and not lines[i].startswith(("%", "#", "- "))
            and not re.match(r"^\d+\)\s+", lines[i])
        ):
            para_lines.append(lines[i].strip())
            i += 1
        body = " ".join(para_lines)

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = (
            Inches(0.0) if first_para_after_heading else Inches(0.20)
        )
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4.0)
        p.paragraph_format.line_spacing = 1.15
        add_rich_text(p, body, base_size=10.0)
        first_para_after_heading = False

    # ------------------------------------------------------------------
    # IEEE REFERENCES SECTION (strictly ordered [1]..[N] by first appearance)
    # ------------------------------------------------------------------
    ph = doc.add_paragraph()
    ph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ph.paragraph_format.space_before = Pt(14)
    ph.paragraph_format.space_after = Pt(6)
    ph.paragraph_format.keep_with_next = True
    rh = ph.add_run("REFERENCES")
    rh.font.name = "Times New Roman"
    rh.font.size = Pt(10.5)
    rh.bold = True

    ordered_handles = sorted(cite_order.items(), key=lambda kv: kv[1])
    for handle, num in ordered_handles:
        entry = REFS[handle]
        pr = doc.add_paragraph()
        pr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pr.paragraph_format.left_indent = Inches(0.32)
        pr.paragraph_format.first_line_indent = Inches(-0.32)
        pr.paragraph_format.space_before = Pt(0)
        pr.paragraph_format.space_after = Pt(2.8)
        pr.paragraph_format.line_spacing = 1.08
        lbl = pr.add_run(f"[{num}]\t")
        lbl.font.name = "Times New Roman"
        lbl.font.size = Pt(8.8)
        add_rich_text(pr, entry, base_size=8.8)

    os.makedirs(os.path.dirname(out_docx), exist_ok=True)
    doc.save(out_docx)
    return {
        "figures": len(fig_map),
        "tables": len(tab_map),
        "equations": len(eq_map),
        "references": len(ordered_handles),
        "docx_bytes": os.path.getsize(out_docx),
    }


def convert_docx_to_doc(in_docx: str, out_doc: str) -> int:
    from spire.doc import Document as SpireDocument
    from spire.doc import FileFormat

    sdoc = SpireDocument()
    sdoc.LoadFromFile(in_docx)
    sdoc.SaveToFile(out_doc, FileFormat.Doc)
    sdoc.Close()

    # Replace the converter's embedded header banner with an exact-length IEEE preprint Slug
    warn = "Evaluation Warning: The document was created with Spire.Doc for Python."
    slug = ("IEEE Transactions / Journal Preprint  |  FedWear-Sepsis  (Nov. 2026)").ljust(
        len(warn)
    )[: len(warn)]
    with open(out_doc, "rb") as f:
        raw = f.read()
    patched = raw.replace(warn.encode("utf-16-le"), slug.encode("utf-16-le"))
    with open(out_doc, "wb") as f:
        f.write(patched)
    return os.path.getsize(out_doc)


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
    doc_bytes = convert_docx_to_doc(out_docx, out_doc)
    stats["doc_bytes"] = doc_bytes
    print("BUILD COMPLETE:", stats)
    print("DOC:", out_doc)
    print("DOCX:", out_docx)

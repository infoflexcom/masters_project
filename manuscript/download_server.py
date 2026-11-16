"""Minimal HTTP preview & one-click .doc download server for the IEEE manuscript."""

from __future__ import annotations

import base64
import html
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOC_FILE = os.path.join(
    ROOT, "Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.doc"
)
DOCX_FILE = os.path.join(
    ROOT, "Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.docx"
)
MD_FILE = os.path.join(HERE, "manuscript.md")
FIG_DIR = os.path.join(ROOT, "figures")

sys.path.insert(0, HERE)
from build_docx import ROMAN, clean_typography, preprocess_references_and_labels  # noqa: E402
from refs import REFS  # noqa: E402


def _inline_html(s: str) -> str:
    s = html.escape(clean_typography(s))
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    # Render inline $...$ lightly for browser preview
    def _math(m: re.Match) -> str:
        e = m.group(1)
        reps = [
            (r"\varepsilon", "ε"), (r"\delta", "δ"), (r"\Delta", "Δ"),
            (r"\sigma", "σ"), (r"\alpha", "α"), (r"\beta", "β"),
            (r"\lambda", "λ"), (r"\mu", "μ"), (r"\bar{\pi}", "π̄"),
            (r"\pi", "π"), (r"\tau", "τ"), (r"\infty", "∞"),
            (r"\leq", "≤"), (r"\geq", "≥"), (r"\approx", "≈"),
            (r"\sim", "∼"), (r"\in", "∈"), (r"\times", "×"),
            (r"\cdot", "·"), (r"\pm", "±"), (r"\rightarrow", "→"),
            (r"\sum", "∑"), (r"\prod", "∏"), (r"\ell", "ℓ"),
            (r"\mathbb{R}", "ℝ"), (r"\ ", " "), (r"\,", " "), (r"\;", " "),
        ]
        for a, b in reps:
            e = e.replace(a, b)
        e = re.sub(r"\\mathrm\{([^{}]+)\}", r"\1", e)
        e = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", e)
        e = re.sub(r"\^\{([^{}]+)\}", r"<sup>\1</sup>", e)
        return f'<span class="math">{e}</span>'

    s = re.sub(r"\$([^$]+)\$", _math, s)
    return s


def render_preview_html() -> bytes:
    raw_md = open(MD_FILE, encoding="utf-8").read()
    md, fig_map, tab_map, eq_map, cite_order = preprocess_references_and_labels(raw_md)
    doc_kb = os.path.getsize(DOC_FILE) // 1024

    body_parts: list[str] = []
    lines = md.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("%TITLE "):
            body_parts.append(f'<h1 class="paper-title">{_inline_html(line[7:])}</h1>')
        elif line.startswith("%AUTHORS "):
            body_parts.append(f'<p class="authors">{_inline_html(line[9:])}</p>')
        elif line.startswith("%AFFIL "):
            body_parts.append(f'<p class="affil">{_inline_html(line[7:])}</p>')
        elif line.startswith("%ABSTRACT "):
            body_parts.append(
                f'<div class="abstract"><strong><em>Abstract</em>—</strong>{_inline_html(line[10:])}</div>'
            )
        elif line.startswith("%KEYWORDS "):
            body_parts.append(
                f'<div class="keywords"><strong><em>Index Terms</em>—</strong>{_inline_html(line[10:])}</div><hr class="sep"/>'
            )
        elif line.startswith("# "):
            body_parts.append(f'<h2 class="sec">{_inline_html(line[2:].upper())}</h2>')
        elif line.startswith("## "):
            body_parts.append(f'<h3 class="subsec">{_inline_html(line[3:])}</h3>')
        elif line.startswith("%EQ "):
            eid, expr = [x.strip() for x in line[4:].split("|", 1)]
            body_parts.append(
                f'<div class="eq"><span class="eq-expr">{_inline_html("$" + expr + "$")}</span><span class="eq-num">({eq_map[eid]})</span></div>'
            )
        elif line.startswith("%FIG "):
            fid, fname, cap = [x.strip() for x in line[5:].split("|", 2)]
            b64 = base64.b64encode(open(os.path.join(FIG_DIR, fname), "rb").read()).decode()
            body_parts.append(
                f'<figure class="fig"><img src="data:image/png;base64,{b64}" alt="Fig. {fig_map[fid]}"/>'
                f'<figcaption><strong>Fig. {fig_map[fid]}.</strong> {_inline_html(cap)}</figcaption></figure>'
            )
        elif line.startswith("%TABLE "):
            tid, cap = [x.strip() for x in line[7:].split("|", 1)]
            tnum = ROMAN[tab_map[tid]]
            i += 1
            rows = []
            while i < n and not lines[i].startswith("%ENDTABLE"):
                rl = lines[i].strip()
                if rl.startswith("|"):
                    cells = [c.strip() for c in rl.strip("|").split("|")]
                    if not all(re.fullmatch(r"[-:\s]+", c) for c in cells):
                        rows.append(cells)
                i += 1
            th = "".join(f"<th>{_inline_html(c)}</th>" for c in rows[0])
            trs = "".join(
                "<tr>" + "".join(f"<td>{_inline_html(c)}</td>" for c in r) + "</tr>"
                for r in rows[1:]
            )
            body_parts.append(
                f'<div class="tbl-wrap"><div class="tbl-cap"><strong>TABLE {tnum}</strong><br/>{_inline_html(cap)}</div>'
                f'<table class="ieee-tbl"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'
            )
        elif line.startswith("- "):
            body_parts.append(f'<p class="bullet">• {_inline_html(line[2:])}</p>')
        else:
            body_parts.append(f'<p class="para">{_inline_html(line)}</p>')
        i += 1

    # References
    body_parts.append('<h2 class="sec">REFERENCES</h2><ol class="refs">')
    for handle, num in sorted(cite_order.items(), key=lambda kv: kv[1]):
        body_parts.append(f'<li value="{num}">{_inline_html(REFS[handle])}</li>')
    body_parts.append("</ol>")

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Download .doc — FedWear-Sepsis IEEE Manuscript</title>
<style>
  :root {{ --ink:#182026; --muted:#5a6672; --accent:#1b4f7a; --bg:#f4f6f9; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font-family:"Times New Roman", Times, Georgia, serif; }}
  .topbar {{
    position:sticky; top:0; z-index:20; background:#102a43; color:#fff;
    padding:12px 24px; display:flex; align-items:center; justify-content:space-between;
    box-shadow:0 2px 8px rgba(0,0,0,.18); font-family:system-ui,-apple-system,sans-serif;
    flex-wrap:wrap; gap:12px;
  }}
  .topbar .meta {{ font-size:13px; line-height:1.35; }}
  .topbar .meta strong {{ font-size:14.5px; display:block; }}
  .actions {{ display:flex; gap:10px; align-items:center; }}
  .btn {{
    display:inline-flex; align-items:center; gap:8px; padding:9px 16px; border-radius:6px;
    font-weight:600; font-size:13.5px; text-decoration:none; cursor:pointer;
  }}
  .btn-primary {{ background:#2ecc71; color:#0b2517; }}
  .btn-primary:hover {{ background:#27ae60; color:#fff; }}
  .btn-secondary {{ background:rgba(255,255,255,.14); color:#fff; border:1px solid rgba(255,255,255,.28); }}
  .btn-secondary:hover {{ background:rgba(255,255,255,.24); }}
  .sheet {{
    max-width:820px; margin:26px auto 60px; background:#fff; padding:54px 62px;
    box-shadow:0 3px 18px rgba(16,42,67,.09); border-radius:3px;
  }}
  .paper-title {{ text-align:center; font-size:24px; line-height:1.25; margin:0 0 12px; }}
  .authors {{ text-align:center; font-size:15px; margin:0 0 8px; }}
  .affil {{ text-align:center; font-size:12px; color:#3b444c; margin:2px 28px; line-height:1.35; }}
  .abstract, .keywords {{ font-size:13px; font-weight:600; text-align:justify; margin:14px 26px 8px; line-height:1.42; }}
  .sep {{ border:0; border-top:1px solid #bbb; margin:16px 0 20px; }}
  .sec {{ text-align:center; font-size:14.5px; letter-spacing:.4px; margin:24px 0 8px; }}
  .subsec {{ font-size:14px; font-style:italic; margin:16px 0 6px; }}
  .para {{ font-size:14px; line-height:1.52; text-align:justify; margin:0 0 9px; text-indent:1.6em; }}
  .bullet {{ font-size:14px; line-height:1.48; text-align:justify; margin:4px 0 6px 1.6em; }}
  .eq {{ display:flex; justify-content:space-between; align-items:center; margin:12px 18px; font-size:14.5px; }}
  .eq-expr {{ flex:1; text-align:center; font-style:italic; }}
  .math {{ font-style:italic; }}
  .fig {{ margin:18px 0; text-align:center; }}
  .fig img {{ max-width:100%; height:auto; border:1px solid #e6e9ed; }}
  .fig figcaption {{ font-size:12px; text-align:justify; margin:6px 18px 0; line-height:1.38; }}
  .tbl-wrap {{ margin:18px 0; overflow-x:auto; }}
  .tbl-cap {{ text-align:center; font-size:12px; margin-bottom:6px; line-height:1.35; }}
  .ieee-tbl {{ width:100%; border-collapse:collapse; font-size:11.8px; }}
  .ieee-tbl thead th {{ border-top:2px solid #182026; border-bottom:1px solid #182026; background:#f2f4f7; padding:6px 8px; text-align:left; }}
  .ieee-tbl tbody td {{ padding:5px 8px; border-bottom:1px solid #e6e9ed; }}
  .ieee-tbl tbody tr:last-child td {{ border-bottom:2px solid #182026; }}
  .refs {{ font-size:12.3px; line-height:1.42; padding-left:28px; }}
  .refs li {{ margin-bottom:5px; text-align:justify; }}
</style>
</head>
<body>
  <div class="topbar">
    <div class="meta">
      <strong>Edge-AI Federated Learning for Sepsis Risk Stratification (IEEE Format)</strong>
      Word 97–2003 Binary Document (.doc, {doc_kb} KB) · 5 Figures · 6 Tables · 53 IEEE References
    </div>
    <div class="actions">
      <a class="btn btn-primary" href="/download/Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.doc" download="Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.doc">⬇ Download .doc ({doc_kb} KB)</a>
      <a class="btn btn-secondary" href="/download/Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.docx" download="Edge_AI_Federated_Learning_Sepsis_Risk_Stratification_IEEE.docx">Download .docx</a>
    </div>
  </div>
  <main class="sheet">
    {"".join(body_parts)}
  </main>
</body>
</html>"""
    return page.encode("utf-8")


CACHED_HTML = render_preview_html()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(CACHED_HTML)))
            self.end_headers()
            self.wfile.write(CACHED_HTML)
        elif path.endswith(".doc"):
            data = open(DOC_FILE, "rb").read()
            fname = os.path.basename(DOC_FILE)
            self.send_response(200)
            self.send_header("Content-Type", "application/msword")
            self.send_header(
                "Content-Disposition", f'attachment; filename="{fname}"'
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif path.endswith(".docx"):
            data = open(DOCX_FILE, "rb").read()
            fname = os.path.basename(DOCX_FILE)
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            self.send_header(
                "Content-Disposition", f'attachment; filename="{fname}"'
            )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def log_message(self, fmt: str, *args) -> None:
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    srv = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving IEEE manuscript preview & .doc download on http://0.0.0.0:{port}", flush=True)
    srv.serve_forever()

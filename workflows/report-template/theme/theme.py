"""Chart theme for the agent-access report template.

Colours, fonts and geometry measured from the original ReportLab PDF.
All geometry is in PostScript points (1/72 in), so charts drop into the page
at 1:1 scale.

    from theme import theme
    theme.apply()                      # loads report.mplstyle
    svg = theme.stacked_hbar(rows, verdicts)
"""
from __future__ import annotations

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

STYLE = Path(__file__).with_name("report.mplstyle")

# ---- palette (hex, measured from the PDF content stream) -------------------
INK = "#1F2429"        # body text, headings
MUTED = "#616B75"      # subtitles, captions, footer, minute labels
RULE = "#D1D6DB"       # hairlines, card borders
PAGE = "#F7F7F5"       # page background
CARD = "#FFFFFF"       # card fill
ROW_SHADE = "#F0F2F2"  # alternating row-label panel in the check grid

VERDICT_COLORS = {
    "present": ("#217A4A", "#FFFFFF"),
    "partial": ("#E3A108", "#261F0D"),
    "absent": ("#C44545", "#FFFFFF"),
    "blocked": ("#6B4C99", "#FFFFFF"),
    "not-observable": ("#D6DBE3", "#404752"),
    "unparsed": ("#F5EDD6", "#59471F"),
}
# Category band tints, cycled when a report has more categories than this.
CATEGORY_TINTS = ["#DBE8E0", "#DBE6F2", "#EDE3D6", "#E8E0F0",
                  "#F2E3E3", "#E3EEF0", "#EEEEDD", "#E6E6E6"]

FONT = ["Helvetica", "Nimbus Sans", "Arial", "Liberation Sans", "DejaVu Sans"]


def apply() -> None:
    """Load the report style for any matplotlib chart."""
    plt.style.use(str(STYLE))


_FONT_FILES = {
    False: ["/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
    True: ["/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
}
_font_cache: dict = {}


def text_width(s: str, size: float, bold: bool = False) -> float:
    """Advance width of `s` in points, measured with a Helvetica-metric font
    (Nimbus Sans / Liberation Sans) when one is installed, else estimated."""
    key = bold
    if key not in _font_cache:
        _font_cache[key] = None
        try:
            from PIL import ImageFont
            for f in _FONT_FILES[bold]:
                if Path(f).exists():
                    _font_cache[key] = ImageFont.truetype(f, 100)
                    break
        except Exception:  # Pillow missing: fall back to the estimate
            pass
    font = _font_cache[key]
    if font is not None:
        return font.getlength(s) * size / 100
    return len(s) * size * (0.58 if bold else 0.54)


_text_width = text_width


def stacked_hbar(rows, verdicts, *, width=728.0, label_w=108.0, gap=10.0,
                 right_w=90.0, pitch=24.0, bar_h=16.0, uniform=True,
                 max_total=None) -> str:
    """Verdict-mix chart: one 100%-style stacked bar per repository.

    rows:     [{"name": str, "counts": {verdict_id: int}, "total": int,
                "right": str}]
    verdicts: [{"id", "color", "text"}] in stacking order.
    Bars all span the same width when every repository ran the same checks
    (uniform=True, as in the original). Otherwise bar length is proportional
    to the number of checks, so a 10-check repository is half the length of
    a 20-check one.
    Returns SVG markup sized in points.
    """
    apply()
    n = max(len(rows), 1)
    longest = max((_text_width(r["name"], 8.5) for r in rows), default=0)
    label_w = max(label_w, longest + 2)
    bar_x0 = label_w + gap
    bar_w = width - bar_x0 - right_w
    max_total = max_total or max((r["total"] for r in rows), default=1) or 1
    height = n * pitch

    fig = plt.figure(figsize=(width / 72, height / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    fig.patch.set_alpha(0)

    for i, r in enumerate(rows):
        y = i * pitch + (pitch - bar_h) / 2
        ax.text(label_w, y + bar_h - 5, r["name"], ha="right", va="baseline",
                fontsize=8.5, color=INK)
        span = bar_w if uniform else bar_w * r["total"] / max_total
        unit = span / r["total"] if r["total"] else 0
        x = bar_x0
        for v in verdicts:
            c = r["counts"].get(v["id"], 0)
            if not c:
                continue
            w = c * unit
            ax.add_patch(Rectangle((x, y), w, bar_h, facecolor=v["color"],
                                   edgecolor="none", linewidth=0))
            if w >= 9:
                ax.text(x + w / 2, y + bar_h - 4, str(c), ha="center", va="baseline",
                        fontsize=7.5, fontweight="bold", color=v["text"])
            x += w
        if r.get("right"):
            ax.text(bar_x0 + bar_w + 8, y + bar_h - 4, r["right"], ha="left",
                    va="baseline", fontsize=8, color=MUTED)

    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True)
    plt.close(fig)
    svg = buf.getvalue()
    # Matplotlib writes pt units already; strip the XML prolog for inlining.
    return svg[svg.index("<svg"):]

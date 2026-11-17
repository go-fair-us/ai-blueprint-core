"""Visual tokens shared with the agent-access review report (report-template/STYLE.md)."""
from __future__ import annotations

from pathlib import Path

INK = "#1F2429"
MUTED = "#616B75"
RULE = "#D1D6DB"
PAGE = "#F7F7F5"
CARD = "#FFFFFF"
ROW_SHADE = "#F0F2F2"
FONT = ["Helvetica", "Nimbus Sans", "Arial", "Liberation Sans", "DejaVu Sans"]
VERDICT_COLORS = {  # fill, text
    "present": ("#217A4A", "#FFFFFF"), "partial": ("#E3A108", "#261F0D"),
    "absent": ("#C44545", "#FFFFFF"), "blocked": ("#6B4C99", "#FFFFFF"),
    "not-observable": ("#D6DBE3", "#404752"), "unparsed": ("#F5EDD6", "#59471F"),
}
VERDICT_SYMBOLS = {"present": "P", "partial": "~", "absent": "A", "blocked": "B",
                   "not-observable": "o", "unparsed": "?"}
# Category dot colours when impact.yaml lists none; chosen to sit apart from verdict colours.
CATEGORY_PALETTE = ["#3E6FA8", "#2E8A78", "#D9822B", "#8A5FB0", "#B5485D", "#5C7A2E",
                    "#4F8FBF", "#A0703A"]
QUADRANT_TINTS = {"top_left": "#E6F0E9", "top_right": "#FBF1DE",
                  "bottom_left": "#EEEFEF", "bottom_right": "#F7E7E7"}

_FONT_FILES = {
    False: ["/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
    True: ["/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
}
_cache: dict = {}


def text_width(s: str, size: float, bold: bool = False) -> float:
    """Advance width in points with a Helvetica-metric font, else an estimate."""
    if bold not in _cache:
        _cache[bold] = None
        try:
            from PIL import ImageFont
            for f in _FONT_FILES[bold]:
                if Path(f).exists():
                    _cache[bold] = ImageFont.truetype(f, 100)
                    break
        except Exception:
            pass
    f = _cache[bold]
    return f.getlength(s) * size / 100 if f else len(s) * size * (0.58 if bold else 0.54)


def line_count(s: str, size: float, width: float) -> int:
    """Lines a paragraph takes when wrapped greedily at `width` points."""
    lines, cur = 1, 0.0
    space = text_width(" ", size)
    for w in str(s).split():
        ww = text_width(w, size)
        if cur and cur + space + ww > width:
            lines += 1
            cur = ww
        else:
            cur = cur + space + ww if cur else ww
    return lines

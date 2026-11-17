#!/usr/bin/env python3
"""
quadrant_plot.py - draw a four-quadrant scatter plot from an external data file.

Both axes run from -1 to 1, with 0 at the center lines.
Data file formats:
  .yaml / .yml / .json  - chart settings plus points (see example.yaml)
  .csv                  - points only (columns: label,x,y,category[,label_pos,dx,dy]);
                          chart settings come from --config or the defaults below.

Optional point fields (backward compatible additions):
  size     - a value (e.g. a count); dot area scales between size_range[0] and
             size_range[1] over the smallest and largest size in the chart
  marker_text - short text drawn inside the dot (e.g. a number)

Optional chart settings (all off by default, so old files plot as before):
  avoid_overlap: true   - move labels that have no label_pos/dx/dy so they do not
                          collide with each other, with dots or with corner names;
                          a thin leader line is drawn when a label moves far
  size_range: [120, 900]
  size_legend: true     - small legend of dot sizes (with size_legend_title)
  watermark: "text"     - faint diagonal text across the plot area
  font_family: [...]    - matplotlib font list
  background: "#F7F7F5" - figure background
  label_wrap: 18        - wrap labels longer than this many characters

Library use:
  import quadrant_plot as qp
  cfg = qp.merge(qp.DEFAULTS, settings); qp.plot(cfg, points, "out.svg")
  fig = qp.render(cfg, points)          # matplotlib Figure, not saved

Usage:
  python quadrant_plot.py example.yaml
  python quadrant_plot.py points.csv --config settings.yaml -o chart.png
  python quadrant_plot.py example.yaml -o chart.svg      # any matplotlib format
"""
import argparse, csv, json, math, sys, textwrap
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

DEFAULTS = {
    "title": "",
    "x_label": "Effort to implement  \u2192",
    "y_label": "Impact  \u2192",
    "quadrants": {                     # label shown in each corner
        "top_left": "Quick wins", "top_right": "Big bets",
        "bottom_left": "Easy follow-ons", "bottom_right": "Plan for later",
    },
    "quadrant_colors": {
        "top_left": "#e8f4ea", "top_right": "#fff4e0",
        "bottom_left": "#f2f2f2", "bottom_right": "#fbeaea",
    },
    "categories": {},                  # name -> color; missing names get palette colors
    "width": 13.33, "height": 7.5,     # inches (16:9 slide)
    "dpi": 150,
    "dot_size": 420,
    "label_font_size": 11.5,
    "quadrant_font_size": 17,
    "title_font_size": 20,
    "axis_font_size": 14,
    "legend": True,
    "legend_font_size": 12,
    "output": None,                    # default: data file name with .png
    # ---- optional additions (defaults keep the original behaviour) ----
    "avoid_overlap": False,
    "size_range": [120, 900],          # marker area (pt^2) for the smallest/largest `size`
    "size_legend": False,
    "size_legend_title": "",
    "watermark": "",
    "font_family": None,
    "background": None,
    "label_wrap": 0,
    "label_color": None,               # None = matplotlib default (black)
    "quadrant_text_color": "#555",
    "quadrant_text_alpha": 0.75,
    "axis_line_color": "#888",
    "dot_edge_color": "white",
    "dot_edge_width": 2,
    "tight_layout": True,
    "format": None,                    # savefig format when `out` is a file object
}
PALETTE = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#d62728",
           "#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"]
# label_pos -> (dx, dy, horizontal align, vertical align); offsets in axis units (-1..1 scale)
LABEL_POS = {
    "right": (0.05, 0, "left", "center"),
    "left": (-0.05, 0, "right", "center"),
    "above": (0, 0.09, "center", "bottom"),
    "below": (0, -0.09, "center", "top"),
}


def load_structured(path):
    text = Path(path).read_text()
    if str(path).lower().endswith(".json"):
        return json.loads(text)
    try:
        import yaml
    except ImportError:
        sys.exit("YAML needs PyYAML: pip install pyyaml (or use a .json/.csv file)")
    return yaml.safe_load(text) or {}


def load_csv(path):
    pts = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row = {k.strip(): (v or "").strip() for k, v in row.items() if k}
            if not row.get("label"):
                continue
            p = {"label": row["label"].replace("\\n", "\n"),
                 "x": float(row["x"]), "y": float(row["y"]),
                 "category": row.get("category") or None}
            if row.get("label_pos"):
                p["label_pos"] = row["label_pos"]
            for k in ("dx", "dy"):
                if row.get(k):
                    p[k] = float(row[k])
            pts.append(p)
    return pts


def merge(base, extra):
    out = dict(base)
    for k, v in (extra or {}).items():
        out[k] = {**out[k], **v} if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def _wrap(label, width):
    label = str(label)
    if not width:
        return label
    return "\n".join(textwrap.fill(part, width) if len(part) > width else part
                     for part in label.split("\n"))


def _sizes(cfg, points):
    """Marker area per point: `size` values scale into size_range; otherwise dot_size."""
    vals = [float(p["size"]) for p in points if p.get("size") is not None]
    lo, hi = (min(vals), max(vals)) if vals else (0, 0)
    a, b = cfg.get("size_range") or [cfg["dot_size"], cfg["dot_size"]]
    out = []
    for p in points:
        if p.get("size") is None:
            out.append(cfg["dot_size"])
        elif hi == lo:
            out.append((a + b) / 2 if lo else a)
        else:  # area grows linearly with the value
            out.append(a + (b - a) * (float(p["size"]) - lo) / (hi - lo))
    return out, (lo, hi)


def _overlap(a, b):
    w = min(a.x1, b.x1) - max(a.x0, b.x0)
    h = min(a.y1, b.y1) - max(a.y0, b.y0)
    return w * h if w > 0 and h > 0 else 0.0


# candidate label offsets as (direction x, direction y, ha, va); distance grows per ring
_CANDIDATES = [(1, 0, "left", "center"), (-1, 0, "right", "center"),
               (0, 1, "center", "bottom"), (0, -1, "center", "top"),
               (1, 1, "left", "bottom"), (1, -1, "left", "top"),
               (-1, 1, "right", "bottom"), (-1, -1, "right", "top")]


def _place_labels(fig, ax, items, obstacles, cfg):
    """Greedy label placement. items: dicts with x, y, r (dot radius, pt), text, fixed
    (label_pos/dx/dy given) and the Text artist. Labels go where they overlap least."""
    renderer = fig.canvas.get_renderer()
    axbox = ax.get_window_extent(renderer)
    placed = []
    px = fig.dpi / 72.0
    order = sorted(range(len(items)), key=lambda i: (not items[i]["fixed"], -items[i]["r"]))
    for i in order:
        it = items[i]
        t = it["artist"]
        if it["fixed"]:
            placed.append(t.get_window_extent(renderer))
            continue
        best = None
        for ring in (1.0, 1.9, 2.9, 4.0):
            for dxn, dyn, ha, va in _CANDIDATES:
                dist = it["r"] + 3 + (ring - 1) * 9
                if dxn and dyn:
                    dist *= 0.8
                t.set_position((dxn * dist, dyn * dist))
                t.set_ha(ha); t.set_va(va)
                bb = t.get_window_extent(renderer).expanded(1.04, 1.08)
                cost = sum(_overlap(bb, o) for o in placed + obstacles
                           if o is not it["own"])
                outside = (max(0, axbox.x0 - bb.x0) + max(0, bb.x1 - axbox.x1)
                           + max(0, axbox.y0 - bb.y0) + max(0, bb.y1 - axbox.y1))
                cost += outside * bb.height * 4
                cost += (ring - 1) * 30 * px * px   # prefer close labels
                if dyn and not dxn:
                    cost += 2 * px * px             # small preference for side labels
                if best is None or cost < best[0]:
                    best = (cost, (dxn * dist, dyn * dist), ha, va, ring, bb)
            if best[0] < 1e-6 + (ring - 1) * 30 * px * px + 2 * px * px and best[4] == ring:
                break
        _, pos, ha, va, ring, bb = best
        t.set_position(pos); t.set_ha(ha); t.set_va(va)
        if ring > 1.0:
            t.arrow_patch = None
            ax.annotate("", xy=(it["x"], it["y"]), xytext=pos, textcoords="offset points",
                        arrowprops=dict(arrowstyle="-", color="#9aa1a8", lw=0.5,
                                        shrinkA=0, shrinkB=it["r"]), zorder=2)
        placed.append(t.get_window_extent(renderer))


def _rc(cfg):
    rc = {}
    if cfg.get("font_family"):
        rc["font.family"] = "sans-serif"
        rc["font.sans-serif"] = list(cfg["font_family"])
    return rc


def render(cfg, points):
    """Draw the chart and return the matplotlib Figure (caller saves/closes it).
    With font_family set, save inside plt.rc_context(_rc(cfg)) or use plot()."""
    with plt.rc_context(_rc(cfg)):
        return _render(cfg, points)


def _render(cfg, points):
    fig, ax = plt.subplots(figsize=(cfg["width"], cfg["height"]), dpi=cfg["dpi"])
    if cfg.get("background"):
        fig.patch.set_facecolor(cfg["background"])
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)

    qc = cfg["quadrant_colors"]
    for key, (x0, y0) in {"top_left": (-1, 0), "top_right": (0, 0),
                          "bottom_left": (-1, -1), "bottom_right": (0, -1)}.items():
        ax.add_patch(Rectangle((x0, y0), 1, 1, color=qc.get(key, "white"), zorder=0))
    ax.axhline(0, color=cfg["axis_line_color"], lw=1, zorder=1)
    ax.axvline(0, color=cfg["axis_line_color"], lw=1, zorder=1)

    q = cfg["quadrants"]
    qs = dict(fontsize=cfg["quadrant_font_size"], fontweight="bold",
              color=cfg["quadrant_text_color"], alpha=cfg.get("quadrant_text_alpha", .75))
    corner = [ax.text(-0.96, 0.95, q.get("top_left", ""), va="top", ha="left", **qs),
              ax.text(0.96, 0.95, q.get("top_right", ""), va="top", ha="right", **qs),
              ax.text(-0.96, -0.95, q.get("bottom_left", ""), va="bottom", ha="left", **qs),
              ax.text(0.96, -0.95, q.get("bottom_right", ""), va="bottom", ha="right", **qs)]
    if cfg.get("watermark"):
        ax.text(0, 0, cfg["watermark"], transform=ax.transData, ha="center", va="center",
                rotation=24, fontsize=cfg["quadrant_font_size"] * 1.5, fontweight="bold",
                color="#C44545", alpha=cfg.get("watermark_alpha", 0.13), zorder=0.5)

    colors = dict(cfg["categories"])
    for p in points:
        c = p.get("category")
        if c and c not in colors:
            colors[c] = PALETTE[len(colors) % len(PALETTE)]

    sizes, (smin, smax) = _sizes(cfg, points)
    smart = bool(cfg.get("avoid_overlap"))
    items = []
    for p, s in zip(points, sizes):
        x, y = float(p["x"]), float(p["y"])
        if not (-1 <= x <= 1 and -1 <= y <= 1):
            print(f"warning: '{p['label']}' is outside -1..1 ({x}, {y})", file=sys.stderr)
        color = p.get("color") or colors.get(p.get("category"), "#444")
        ax.scatter(x, y, s=s, color=color, zorder=3, edgecolor=cfg["dot_edge_color"],
                   lw=cfg.get("dot_edge_width", 2))
        if p.get("marker_text") not in (None, ""):
            ax.text(x, y, str(p["marker_text"]), ha="center", va="center", zorder=5,
                    fontsize=max(6, cfg["label_font_size"] * 0.8), fontweight="bold",
                    color="white")
        label = _wrap(p.get("label", ""), cfg.get("label_wrap"))
        fixed = bool(p.get("label_pos")) or "dx" in p or "dy" in p
        if smart and not fixed:
            t = ax.annotate(label, xy=(x, y), xytext=(0, 0), textcoords="offset points",
                            fontsize=cfg["label_font_size"], zorder=4, color=cfg["label_color"],
                            ha="left", va="center")
        else:
            pos = p.get("label_pos") or ("left" if x > 0.6 else "right")
            dx, dy, ha, va = LABEL_POS.get(pos, LABEL_POS["right"])
            dx += float(p.get("dx", 0)); dy += float(p.get("dy", 0))
            t = ax.text(x + dx, y + dy, label, ha=ha, va=va,
                        fontsize=cfg["label_font_size"], zorder=4, color=cfg["label_color"])
        items.append({"x": x, "y": y, "r": math.sqrt(s) / 2, "artist": t,
                      "fixed": fixed or not smart, "own": None})

    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel(cfg["x_label"], fontsize=cfg["axis_font_size"])
    ax.set_ylabel(cfg["y_label"], fontsize=cfg["axis_font_size"])
    if cfg["title"]:
        ax.set_title(cfg["title"], fontsize=cfg["title_font_size"], loc="left", pad=12)
    handles = []
    if cfg["legend"] and colors:
        used = {p.get("category") for p in points}
        handles = [Patch(color=c, label=k) for k, c in colors.items()
                   if k in used or k in cfg["categories"]]
    if cfg.get("size_legend") and smax and smax != smin:
        from matplotlib.lines import Line2D
        a, b = cfg["size_range"]
        picks = sorted({smin, round((smin + smax) / 2), smax})
        if cfg.get("size_legend_title"):
            handles.append(Line2D([], [], ls="", marker="", label=cfg["size_legend_title"]))
        for v in picks:
            area = a + (b - a) * (v - smin) / (smax - smin)
            handles.append(Line2D([], [], ls="", marker="o", markersize=math.sqrt(area),
                                  markerfacecolor="#B8BEC4", markeredgecolor="white",
                                  label=f"{v:g}"))
    if handles:
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, -.06),
                  ncol=min(len(handles), 10 if cfg.get("size_legend") else 8), frameon=False, fontsize=cfg["legend_font_size"],
                  **({"handletextpad": 0.5, "columnspacing": 1.4}
                     if cfg.get("size_legend") else {}))
    if cfg.get("tight_layout", True):
        plt.tight_layout()
    if smart:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        obstacles = [c.get_window_extent(renderer) for c in corner if c.get_text()]
        px = fig.dpi / 72.0
        from matplotlib.transforms import Bbox
        for it in items:
            cx, cy = ax.transData.transform((it["x"], it["y"]))
            r = (it["r"] + 1) * px
            bb = Bbox.from_extents(cx - r, cy - r, cx + r, cy + r)
            it["own"] = bb
            obstacles.append(bb)
        _place_labels(fig, ax, items, obstacles, cfg)
    return fig


def plot(cfg, points, out):
    """Draw and save to `out` (a path, or a file object with cfg['format'])."""
    with plt.rc_context(_rc(cfg)):
        fig = _render(cfg, points)
        if hasattr(out, "write"):
            fig.savefig(out, format=cfg.get("format") or "png",
                        facecolor=fig.get_facecolor())
            plt.close(fig)
            return
        fig.savefig(out, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"wrote {out}")


def main():
    ap = argparse.ArgumentParser(description="Four-quadrant scatter plot from a data file (axes -1..1).")
    ap.add_argument("data", help=".yaml/.yml/.json (settings + points) or .csv (points)")
    ap.add_argument("-c", "--config", help="optional settings file (.yaml/.json) for CSV input or overrides")
    ap.add_argument("-o", "--output", help="output image (.png, .svg, .pdf...)")
    a = ap.parse_args()

    cfg = dict(DEFAULTS)
    if a.data.lower().endswith(".csv"):
        points = load_csv(a.data)
    else:
        d = load_structured(a.data)
        points = d.pop("points", [])
        cfg = merge(cfg, d)
    if a.config:
        extra = load_structured(a.config); extra.pop("points", None)
        cfg = merge(cfg, extra)
    if not points:
        sys.exit("no points found in the data file")
    out = a.output or cfg.get("output") or str(Path(a.data).with_suffix(".png"))
    plot(cfg, points, out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
quadrant_plot.py - draw a four-quadrant scatter plot from an external data file.

Both axes run from -1 to 1, with 0 at the center lines.
Data file formats:
  .yaml / .yml / .json  - chart settings plus points (see example.yaml)
  .csv                  - points only (columns: label,x,y,category[,label_pos,dx,dy]);
                          chart settings come from --config or the defaults below.

Usage:
  python quadrant_plot.py example.yaml
  python quadrant_plot.py points.csv --config settings.yaml -o chart.png
  python quadrant_plot.py example.yaml -o chart.svg      # any matplotlib format
"""
import argparse, csv, json, sys
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
    "output": None,                    # default: data file name with .png
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


def plot(cfg, points, out):
    fig, ax = plt.subplots(figsize=(cfg["width"], cfg["height"]), dpi=cfg["dpi"])
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)

    qc = cfg["quadrant_colors"]
    for key, (x0, y0) in {"top_left": (-1, 0), "top_right": (0, 0),
                          "bottom_left": (-1, -1), "bottom_right": (0, -1)}.items():
        ax.add_patch(Rectangle((x0, y0), 1, 1, color=qc.get(key, "white"), zorder=0))
    ax.axhline(0, color="#888", lw=1, zorder=1); ax.axvline(0, color="#888", lw=1, zorder=1)

    q = cfg["quadrants"]
    qs = dict(fontsize=cfg["quadrant_font_size"], fontweight="bold", color="#555", alpha=.75)
    ax.text(-0.96, 0.95, q.get("top_left", ""), va="top", ha="left", **qs)
    ax.text(0.96, 0.95, q.get("top_right", ""), va="top", ha="right", **qs)
    ax.text(-0.96, -0.95, q.get("bottom_left", ""), va="bottom", ha="left", **qs)
    ax.text(0.96, -0.95, q.get("bottom_right", ""), va="bottom", ha="right", **qs)

    colors = dict(cfg["categories"])
    for p in points:
        c = p.get("category")
        if c and c not in colors:
            colors[c] = PALETTE[len(colors) % len(PALETTE)]

    for p in points:
        x, y = float(p["x"]), float(p["y"])
        if not (-1 <= x <= 1 and -1 <= y <= 1):
            print(f"warning: '{p['label']}' is outside -1..1 ({x}, {y})", file=sys.stderr)
        color = p.get("color") or colors.get(p.get("category"), "#444")
        ax.scatter(x, y, s=cfg["dot_size"], color=color, zorder=3, edgecolor="white", lw=2)
        pos = p.get("label_pos") or ("left" if x > 0.6 else "right")
        dx, dy, ha, va = LABEL_POS.get(pos, LABEL_POS["right"])
        dx += float(p.get("dx", 0)); dy += float(p.get("dy", 0))
        ax.text(x + dx, y + dy, str(p["label"]), ha=ha, va=va,
                fontsize=cfg["label_font_size"], zorder=4)

    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel(cfg["x_label"], fontsize=cfg["axis_font_size"])
    ax.set_ylabel(cfg["y_label"], fontsize=cfg["axis_font_size"])
    if cfg["title"]:
        ax.set_title(cfg["title"], fontsize=cfg["title_font_size"], loc="left", pad=12)
    if cfg["legend"] and colors:
        ax.legend(handles=[Patch(color=c, label=k) for k, c in colors.items()],
                  loc="upper center", bbox_to_anchor=(.5, -.06), ncol=min(len(colors), 5),
                  frameon=False, fontsize=12)
    plt.tight_layout()
    plt.savefig(out)
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

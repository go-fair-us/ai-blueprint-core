"""Cross-repository view: one point per gap (source + key), grouped by check."""
from __future__ import annotations

import statistics

from .rubric import quadrant


def combine(gapfiles: list[dict], placements: dict[str, dict], cfg: dict,
            overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    n_repos = sum(1 for g in gapfiles
                  if any(s.get("available") for s in g["sources"].values()))
    groups: dict[str, dict] = {}
    order = []
    for gf in gapfiles:
        slug = gf["repo"]["slug"]
        gaps = {g["id"]: g for g in gf["gaps"]}
        for p in (placements.get(slug) or {}).get("points") or []:
            g = gaps.get(p.get("gap_id"))
            if g is None:
                continue
            if g["id"] not in groups:
                order.append(g["id"])
                groups[g["id"]] = {"id": g["id"], "source": g["source"], "key": g["key"],
                                   "label": g["label"], "category": g["category"],
                                   "xs": [], "ys": [], "repos": [], "fixes": []}
            grp = groups[g["id"]]
            grp["xs"].append(float(p["x"])); grp["ys"].append(float(p["y"]))
            grp["repos"].append(gf["repo"]["display"]); grp["fixes"].append(p.get("label"))
    rows = []
    for gid in order:
        g = groups[gid]
        mx, my = statistics.median(g["xs"]), statistics.median(g["ys"])
        n = len(g["repos"])
        rows.append({**{k: g[k] for k in ("id", "source", "key", "label", "category", "repos")},
                     "count": n, "x": round(mx, 3), "y": round(my, 3),
                     "spread_x": round(max(g["xs"]) - min(g["xs"]), 3),
                     "spread_y": round(max(g["ys"]) - min(g["ys"]), 3),
                     "quadrant": quadrant(mx, my, cfg["quadrants"])})
    rows.sort(key=lambda r: (-r["count"], -r["y"], r["x"], r["label"]))
    points = []
    for r in rows:
        p = {"label": f"{r['label']} ({r['count']}/{n_repos})", "x": r["x"], "y": r["y"],
             "category": r["category"], "size": r["count"], "gap_id": r["id"]}
        o = overrides.get(r["id"]) or {}
        if o.get("hide"):
            continue
        p.update({k: v for k, v in o.items() if k in ("label", "x", "y", "label_pos", "dx", "dy", "color")})
        points.append(p)
    return {"n_repos": n_repos, "rows": rows, "points": points,
            "total": sum(r["count"] for r in rows)}

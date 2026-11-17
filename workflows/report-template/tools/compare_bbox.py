#!/usr/bin/env python3
"""Compare word positions between two PDFs (e.g. the original and a rebuild).

    python3 tools/compare_bbox.py original.pdf out/example.pdf

Prints, per page, words whose position differs by more than 1.5 pt.
Needs poppler-utils (pdftotext -bbox).
"""
import re, subprocess, sys, html
from collections import defaultdict

def words(pdf):
    x = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    pages, cur = [], None
    for line in x.splitlines():
        if "<page " in line:
            cur = defaultdict(list); pages.append(cur)
        m = re.search(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*)</word>', line)
        if m and cur is not None:
            cur[html.unescape(m.group(5))].append(tuple(float(m.group(i)) for i in range(1, 5)))
    return pages

a, b = words(sys.argv[1]), words(sys.argv[2])
for p, (pa, pb) in enumerate(zip(a, b), 1):
    print(f"--- page {p}")
    for w, la in pa.items():
        lb = pb.get(w)
        if not lb:
            continue
        for (x0, y0, x1, y1), (u0, v0, u1, v1) in zip(la, lb):
            if abs(x0 - u0) > 1.5 or abs(y1 - v1) > 1.5:
                print(f"{w[:24]:24s} orig x={x0:6.1f} yb={y1:6.1f}  new x={u0:6.1f} yb={v1:6.1f}  dx={u0-x0:+5.1f} dy={v1-y1:+5.1f}")
            break

#!/usr/bin/env python3
"""Render two PDFs and save page-by-page side-by-side PNGs plus a pixel-diff score.

    python3 tools/side_by_side.py reference/original.pdf out/example.pdf out/compare
"""
import subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

a_pdf, b_pdf, outdir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
outdir.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as t:
    for tag, pdf in (("a", a_pdf), ("b", b_pdf)):
        subprocess.run(["pdftoppm", "-r", "100", "-png", pdf, f"{t}/{tag}"], check=True)
    pa, pb = sorted(Path(t).glob("a-*.png")), sorted(Path(t).glob("b-*.png"))
    for i, (fa, fb) in enumerate(zip(pa, pb), 1):
        A, B = Image.open(fa).convert("RGB"), Image.open(fb).convert("RGB")
        d = ImageChops.difference(A, B).convert("L")
        score = 100 * sum(1 for v in d.get_flattened_data() if v > 60) / (A.width * A.height)
        W = Image.new("RGB", (A.width + B.width + 20, max(A.height, B.height) + 30), "white")
        W.paste(A, (0, 30)); W.paste(B, (A.width + 20, 30))
        dr = ImageDraw.Draw(W)
        dr.text((10, 8), f"original  (page {i})", fill="black")
        dr.text((A.width + 30, 8), f"template build  (page {i}, {score:.1f}% pixels differ)", fill="black")
        W.save(outdir / f"page-{i}.png")
        print(f"page {i}: {score:.2f}% of pixels differ")

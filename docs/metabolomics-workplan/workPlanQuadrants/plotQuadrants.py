import matplotlib.pyplot as plt
import numpy as np

# Data: (x=effort, y=impact, label, category)
points = [
    # Reachable (blue)
    (1.2, 4.2, "Robots.txt by visitor class", "Reachable"),
    (2.8, 2.8, "Sitemap with lastmod", "Reachable"),
    # Readable (green)
    (1.5, 3.5, "License + Signposting\nin first HTML", "Readable"),
    (3.2, 3.8, "Dataset JSON-LD\n+ conformsTo", "Readable"),
    # Callable (orange)
    (3.0, 4.5, "REST reads return\nHTTP 200 + types", "Callable"),
    (4.5, 4.3, "OpenAPI for\nexisting API", "Callable"),
    # Meaningful (purple)
    (1.0, 1.5, "Example questions\non a stable URL", "Meaningful"),
    (2.5, 2.2, "RefMet ids as\nPubChem/ChEBI URLs", "Meaningful"),
    (4.2, 2.8, "ORCID + ROR on\nnamed people/orgs", "Meaningful"),
]

colors = {
    "Reachable": "#2563EB",
    "Readable": "#059669",
    "Callable": "#D97706",
    "Meaningful": "#7C3AED",
}

fig, ax = plt.subplots(figsize=(12, 7))

# Background quadrants
ax.axvspan(0, 3, 0, 3, facecolor="#F3F4F6", alpha=0.6, zorder=0)   # Easy follow-ons
ax.axvspan(3, 6, 0, 3, facecolor="#FCE7F3", alpha=0.6, zorder=0)   # Plan for later
ax.axvspan(0, 3, 3, 6, facecolor="#D1FAE5", alpha=0.5, zorder=0)   # Quick wins
ax.axvspan(3, 6, 3, 6, facecolor="#FEF3C7", alpha=0.6, zorder=0)   # Big bets

# Quadrant labels
ax.text(1.5, 5.5, "Quick wins", ha="center", va="center", fontsize=16, color="#4B5563", fontweight="bold")
ax.text(4.5, 5.5, "Big bets", ha="center", va="center", fontsize=16, color="#4B5563", fontweight="bold")
ax.text(1.5, 0.5, "Easy follow-ons", ha="center", va="center", fontsize=16, color="#4B5563", fontweight="bold")
ax.text(4.5, 0.5, "Plan for later", ha="center", va="center", fontsize=16, color="#4B5563", fontweight="bold")

# Plot points
for x, y, label, cat in points:
    ax.scatter(x, y, s=180, color=colors[cat], zorder=3, edgecolors="white", linewidth=1.5)
    ax.annotate(label, (x, y), xytext=(8, 6), textcoords="offset points",
                fontsize=9, color="#1F2937", ha="left")

# Axes
ax.set_xlim(0, 6)
ax.set_ylim(0, 6)
ax.set_xlabel("Effort to implement →", fontsize=13, labelpad=10)
ax.set_ylabel("Impact on agent access →", fontsize=13, labelpad=10)
ax.set_xticks([])
ax.set_yticks([])
ax.spines[["top", "right"]].set_visible(False)
ax.axhline(3, color="#9CA3AF", linewidth=1, zorder=1)
ax.axvline(3, color="#9CA3AF", linewidth=1, zorder=1)

# Legend
handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=12, label=name)
           for name, c in colors.items()]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.12),
          ncol=4, frameon=False, fontsize=11)

ax.set_title("Metabolomics Workbench: where to start", fontsize=16, pad=15, loc="left", fontweight="medium")

plt.tight_layout()
plt.show()
plt.savefig("metabolomics_workbench_matrix.png", dpi=200, bbox_inches="tight")
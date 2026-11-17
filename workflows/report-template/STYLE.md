# Style spec: "Repository agent-access review"

Measured from the original PDF (`reference/original.pdf`, ReportLab, 3 pages) with
`pdfinfo`, `pdffonts`, `pdfimages`, `pdftotext -layout/-bbox`, page renders, and the
decompressed content streams. Coordinates are PostScript points (1/72 in). "From top"
means distance from the top edge of the page.

## Page

| Property | Value |
|---|---|
| Size | US Letter landscape, 792 x 612 pt |
| Background | full-bleed `#F7F7F5` (warm off-white) |
| Side margins | 32 pt left and right (content width 728 pt) |
| Top | title baseline 52 pt from top (page 1); section titles 44 pt (grid page), 52 pt (questions page) |
| Footer rule | 0.4 pt hairline `#D1D6DB`, y = 32 pt from bottom, x 32 to 760 |
| Footer text | 8 pt Helvetica `#616B75`, baseline 20 pt from bottom. Left: `org  ·  stamp  ·  model` (two spaces around each middle dot). Right: `n / N` |
| Images | none. Every graphic is vector (rects, rounded rects, text) |

## Type

The fonts are the standard-14 **Helvetica** and **Helvetica-Bold**. They are not embedded,
so the template asks for `Helvetica, Nimbus Sans, Arial`. Nimbus Sans, which is metric-compatible,
is what renders on Linux.

| Role | Font | Size | Colour |
|---|---|---|---|
| Report title | Bold | 20 | `#1F2429` |
| Subtitle | Regular | 10 | `#616B75` |
| Page section title | Bold | 16 | `#1F2429` |
| Page caption | Regular | 9 | `#616B75` |
| Sub-section heading ("Verdict mix") | Bold | 12 | `#1F2429` |
| Inline caption next to it | Regular | 8.5 | `#616B75` |
| Card value / label | Bold 16 / Regular 9 | | `#1F2429` |
| Bar-chart row labels | Regular | 8.5 | `#1F2429`, right-aligned |
| Numbers inside bars | Bold | 7.5 | per-verdict text colour |
| Minutes column | Regular | 8 | `#616B75` |
| Grid row labels | Regular | 8 | `#1F2429`, right-aligned |
| Grid cell letters | Bold | 8 | per-verdict text colour |
| Rotated column headers | Regular | 7 | `#1F2429` |
| Category band labels | Regular | 7 | `#1F2429` |
| Repo name (questions page) | Bold | 10 | `#1F2429`; URL Regular 8 `#616B75` at x = 118 |
| Tile id / grade | Bold 8 / Regular 7 | | per-grade text colour |
| Footnotes | Regular | 8 | `#616B75`; notes bullets `#1F2429` |

## Colour

| Token | Fill | Text on it | Used for |
|---|---|---|---|
| present `P` | `#217A4A` green | `#FFFFFF` | verdict; also "match" grade |
| partial `~` | `#E3A108` amber | `#261F0D` | verdict; also "ungraded" grade |
| absent `A` | `#C44545` red | `#FFFFFF` | verdict |
| blocked `B` | `#6B4C99` purple | `#FFFFFF` | verdict |
| not-observable `o` | `#D6DBE3` grey-blue | `#404752` | verdict; also "no-answer" grade |
| unparsed `?` | `#F5EDD6` cream | `#59471F` | verdict |
| ink | `#1F2429` | | body text |
| muted | `#616B75` | | captions, footer |
| rule | `#D1D6DB` | | hairlines, card borders |
| row shade | `#F0F2F2` | | alternate row-label panels in the grid |
| card | `#FFFFFF` | | summary cards |
| category tints | `#DBE8E0` `#DBE6F2` `#EDE3D6` `#E8E0F0` | `#1F2429` | band behind each category's column headers |

Each verdict letter repeats its colour, so the page still reads in black and white.

## Components

**Summary cards** (page 1): 230 x 52 pt, radius 6, white, 0.4 pt `#D1D6DB` border, 14 pt
gap, top at 82 pt from top. Value baseline 28 pt below card top, label 42 pt.

**Legend chips**: 14 x 12 pt rounded (r 2) chip holding the bold 7 pt symbol, then
`label count` in 8 pt. The chips sit about 14 pt apart.

**Verdict-mix chart** (stacked horizontal bars): one bar per repository, 16 pt tall, row
pitch 24 pt, bars from x = 150 to 670 (520 pt). Segments are square-cornered and touch, in
verdict order present, partial, absent, blocked, not-observable, unparsed. Each segment shows
its count in bold 7.5 pt. The label is right-aligned at x = 142; the minutes are at x = 678.
There are no axes, gridlines or ticks.

**Check grid** (page 2): category bands 14 pt tall (r 2) above rotated (90°) 7 pt column
names; column pitch 34 pt from x = 119.5; cells 31 x 20 pt (r 2) holding the bold letter;
row pitch 26 pt; row-label panel 82 x 26 pt, shaded `#F0F2F2` on every other row
starting with the first.

**Grade tiles** (page 3): 92 x 26 pt (r 3), 98 pt pitch, id bold 8 pt + grade 7 pt,
inset 6 pt. Repo name line, then the tiles 16 pt below it. A grade legend of 46 x 14 pt
chips sits under the caption.

**Notes block**: 0.4 pt rule across the content width, bold 10 pt heading, bullets
written as `- text` in 8 pt at a 14 pt line pitch.

## Voice

Short declarative captions explain how to read each figure ("Each bar is the 19 checks
for that repository"). Counts appear as words up to twenty ("Twelve", "Nine rows
matched"). Footnotes say what a symbol means and call out anomalies in the run.

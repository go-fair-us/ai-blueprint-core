# quadrant_plot.py

Draws a four-quadrant scatter plot from an external data file. Both axes run from -1 to 1, and 0 is the center line.

Requirements: Python 3, matplotlib, and pyyaml (only needed for YAML files):

    pip install matplotlib pyyaml

## Run

    python quadrant_plot.py example.yaml                              # writes example.png
    python quadrant_plot.py example.yaml -o slide.svg                 # any matplotlib format: png, svg, pdf
    python quadrant_plot.py example.csv --config example.yaml -o out.png

## Data file

A YAML or JSON file holds the chart settings and a `points` list. A CSV file holds points only, and its settings come from `--config` or the defaults.

Each point has these fields:
- `label`: the text next to the dot. Use `\n` for a line break.
- `x` and `y`: the position, from -1 to 1.
- `category`: picks the color and the legend entry.
- `label_pos` (optional): where the label goes relative to the dot: right, left, above, or below.
- `dx` and `dy` (optional): an extra nudge for the label, in the same -1 to 1 units.
- `color` (optional): sets the color for that one dot.

Chart settings: title, x_label, y_label, quadrants (the corner names), quadrant_colors, categories (name and color, in legend order), width, height, dpi, dot_size, the font sizes, legend, and output.

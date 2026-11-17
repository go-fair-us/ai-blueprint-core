"""impactQuadrants report: absent facet checks -> effort/impact placements -> PDF.

Modules
  runfiles     read a repo_herd run folder (manifest.json, summary.md, facet reports)
  gaps         the generic gap-item schema and the extract step
  extractors/  one module per gap source, registered by name (facet-check today)
  rubric       load the versioned effort/impact rubric
  backends     model backends: pi, openai (compatible endpoint), stub (placeholder)
  assess       prompt, schema validation, retries, sampling, cache
  review       placements in quadrant_plot.py format + overrides that survive re-runs
  combine      cross-repository grouping by check
  report       HTML/PDF rendering in the agent-access report style
"""
__version__ = "0.1.0"

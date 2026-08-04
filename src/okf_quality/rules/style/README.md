# Style rules (P2)

Prose quality for OKF bodies, atomic claims, and related docs.

## Integration

| Tool | Path |
|------|------|
| STE anti-slop skill | `~/.grok/skills/ste-writing/` (+ `scripts/ste-lint.py`) |
| Rule notes | [claim-style.md](claim-style.md) |

## Suggested CI use

1. Export or collect atomic texts from the bundle (`okf_core.walk`).  
2. Run `ste-lint.py` on a temp file of concatenated claims.  
3. Fail only on extreme scores if desired; default = report.

Style failures should rarely block RDF publish; they inform agent rewrite loops.

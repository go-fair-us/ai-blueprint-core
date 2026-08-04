# Lint (P0)

| Path | Role |
|------|------|
| `rules/*.yaml` | Declarative rule registry (ids, severity, docs) |
| `../scripts/okf_lint.py` | Implementation using `okf_core.walk` |

Add new structural rules by:

1. Documenting in `rules/okf-structure.yaml`  
2. Implementing in `okf_lint.lint_bundle`  
3. Testing in `tests/test_okf_lint.py`  

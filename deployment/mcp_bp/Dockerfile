# Slim MCP image: knowledge server + skill catalog + SHACL wrap.
# Does not install the repo's full ML stack (docling / dspy / marker).
FROM python:3.13-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir \
    "fastmcp>=2.0" \
    "rank-bm25>=0.2" \
    "rapidfuzz>=3.0" \
    "pyyaml>=6.0" \
    "pyshacl>=0.40.0" \
    "rdflib>=7.6.0"

COPY mcp_bp ./mcp_bp
COPY src/okf_core/src/okf_core ./src/okf_core/src/okf_core
COPY docs ./docs
COPY okf ./okf
COPY prompts ./prompts
COPY niaid-blueprint/skills ./niaid-blueprint/skills

ENV PYTHONPATH=/app
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV MCP_PATH=/mcp
ENV BLUEPRINT_SKILLS_DIR=/app/niaid-blueprint/skills

EXPOSE 8000

CMD ["python", "-m", "mcp_bp.server"]

# LibreChat + Blueprint MCP (localhost)

Browser chat UI that calls **NRP** (`https://ellm.nrp-nautilus.io/v1`) and the
Blueprint MCP server, and mounts `niaid-blueprint/skills` as LibreChat
deployment skills.

## What runs

| Service | Address | Role |
|---------|---------|------|
| LibreChat | http://127.0.0.1:3080 | Chat UI, agents, native `SKILL.md` loader |
| `mcp_bp` | http://127.0.0.1:8000/mcp | Docs / OKF / prompts / skill catalog / SHACL |

Ports bind to loopback only. There is no SSO and no MCP auth — do not publish
this compose off localhost.

## Start

From the repository root:

```bash
cd deployment/librechat
cp .env.example .env
# set NRP_API_KEY (and replace the JWT / Meili example secrets)
docker compose up --build
```

Register a local account on first visit, then:

1. New chats default to the **Blueprint (NRP)** model spec (`deepseek-v4-flash` plus a
   standing prompt that requires MCP lookup before answering Blueprint
   questions). You can still pick other NRP models. Restart the `api`
   container after you edit `librechat.yaml`.
2. The **Blueprint (NRP)** spec now attaches the **ai-blueprint** MCP server
   (`mcpServers: [ai-blueprint]`). Without that, LibreChat ran an ephemeral
   agent with 0 tools and the model only streamed Thoughts.
3. Optional: create a saved **agent** and attach a subset of MCP tools plus
   `niaid-bp-*` skills for interviews. Copy the spec’s `promptPrefix` into
   agent Instructions if you want the same lookup rule.
4. First checks:
   - “Search the Blueprint for Table 1 identifier requirements.”
   - “Load `niaid-bp-fair-assess` and start Phase 1.”
   - Paste `niaid-blueprint/skills/niaid-bp-validation/tests/fixtures/valid_dataset.jsonld`
     and ask the agent to `validate_dataset`.

## Skills: two paths

- **Native:** `DEPLOYMENT_SKILLS_DIR=/app/skill` is the plugin `skills/` tree.
  LibreChat can advertise `$niaid-bp-fair-assess` and inject `SKILL.md`.
- **MCP:** `list_skills` / `read_skill` / `read_skill_file` for progressive
  reads; `validate_dataset` runs pySHACL (a web UI will not execute
  `scripts/validate.py` by itself).

Interview skills stay procedures. Only the SHACL runner is a callable tool.

## Point LibreChat at a host MCP instead

If `mcp_bp` is already running on the host (`uv run --extra mcp python -m mcp_bp.server`
with `MCP_HOST=0.0.0.0`), set in `librechat.yaml`:

```yaml
url: http://host.docker.internal:8000/mcp
```

and you can `docker compose up` without the `mcp_bp` service.

## Fallback

If LibreChat’s MCP handshake or skill mount fails, keep `mcp_bp` and attach
**Open WebUI** (Admin → Integrations → MCP Streamable HTTP) to the same URL.
Skills then go through the MCP catalog only.

## Image notes

`deployment/mcp_bp/Dockerfile` installs FastMCP, search, PyYAML, and pySHACL.
It does **not** install the repo’s docling / DSPy / marker stack.

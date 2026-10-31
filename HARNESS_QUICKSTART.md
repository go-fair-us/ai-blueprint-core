# Harness quickstart

Install [Pi](https://pi.dev) and [uv](https://docs.astral.sh/uv/), clone this repository, and start the Blueprint skills with `./bin/pi`.

You need a valid API key, or a subscription login, for a model provider Pi supports. Pi uses that credential for the chat. A key that is missing, expired, or for a different provider leaves the session with no model to call.

## 1. Install Pi

On macOS or Linux:

```bash
curl -fsSL https://pi.dev/install.sh | sh
pi --version
```

Open a new terminal if `pi` is not found. The installer adds it to your `PATH`.

Pi also installs from npm when Node.js is 22.19 or newer:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

On Windows, PowerShell can install Pi with `irm https://pi.dev/install.ps1 | iex`. `./bin/pi` is a bash script, so run it from Git Bash or WSL. Details are in the [Pi Windows guide](https://pi.dev/docs/latest/windows).

## 2. Install uv

On macOS or Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Open a new terminal if `uv` is not found. `./bin/pi` starts without uv. The sitemap, robots, and llms.txt skills call `uv run` when you use them, and the optional knowledge server is installed with uv.

## 3. Give Pi a provider key

Set one provider variable in the shell you use to start Pi, or sign in after Pi opens.

| Provider | Environment variable |
|----------|----------------------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| xAI | `XAI_API_KEY` |

```bash
export OPENROUTER_API_KEY="your-key"
```

Inside Pi, `/login` stores a key or completes a subscription login. `/model` selects the model. The key has to be valid for the provider you pick.

`NRP_API_KEY` is for the Python optimizers in this repo. Pi does not read it.

## 4. Clone the repository

```bash
git clone https://github.com/go-fair-us/ai-blueprint-core.git
cd ai-blueprint-core
```

## 5. Start Pi

```bash
./bin/pi
```

The launcher checks that `pi` is on `PATH`, changes to the repository root, and runs `pi --no-skills -e extensions/load-skills.ts`. That extension loads the skills in `niaid-blueprint/skills/` and the 23 evaluation commands in `extensions/prompts/`. A command name is the filename, so `/sitemap https://example.org/` runs the sitemap evaluation. Extra arguments pass through to Pi.

The first start asks you to trust this project, because the clone contains `.pi/settings.json` and `.pi/mcp.json`. Skills and prompt commands load either way. Trust the project when you want Pi to read that MCP file.

Two messages can appear after you trust it. The session still starts.

- The `immport` entry in `.pi/mcp.json` is skipped. Pi 1.4 reports `auth.provider must be a provider name` for that entry.
- Pi tries `http://localhost:8000/mcp`. That address answers after you start the knowledge server below.

## 6. Run a skill or an evaluation

Skills are advertised by name. Force one with its command:

```text
/skill:niaid-bp-fair-assess
```

Evaluation prompts take a repository origin, and some take a second URL:

```text
/robots-policy https://example.org/
/llms-txt https://example.org/
```

## 7. Optional: Blueprint knowledge server

Start this in a second terminal when you want Pi to search Blueprint docs, OKF concepts, and the skill catalog. The first `uv sync` downloads a large environment.

```bash
uv sync --extra mcp
uv run --extra mcp python -m mcp_bp.server
```

The server listens at `http://127.0.0.1:8000/mcp`. Pi connects to it in the background. A connection refused message on an earlier start clears once the server is up and Pi retries.

Leave this server off when you only want the skills and the evaluation commands.

"""Model backends for the assess step.

  pi      Pi CLI, as the repo_herd run used it (--provider nrp --model deepseek-v4-flash)
  openai  any OpenAI-compatible /chat/completions endpoint (env vars, see impact.yaml)
  stub    PLACEHOLDER placements from stub_defaults.yaml. Not a model. Every output
          it produces is marked placeholder: true and watermarked in the report.

A backend has .name, .model, .placeholder and complete(system, user, gaps) -> str.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import yaml


class BackendError(RuntimeError):
    pass


class PiBackend:
    name = "pi"
    placeholder = False

    def __init__(self, cfg: dict, model: str | None = None, provider: str | None = None):
        c = cfg["pi"]
        self.bin = c.get("bin") or "pi"
        self.provider = provider or c.get("provider")
        self.model = model or c.get("model")
        self.args = list(c.get("args") or [])
        self.timeout = int(c.get("timeout") or 900)
        if not (Path(self.bin).is_file() or shutil.which(self.bin)):
            raise BackendError(f"Pi CLI {self.bin!r} not found. Set pi.bin in impact.yaml "
                               "(e.g. ai-blueprint-core/bin/pi), or use --backend openai, "
                               "or --backend stub for placeholder placements.")

    @property
    def label(self) -> str:
        return f"pi / {self.provider} / {self.model}" if self.provider else f"pi / {self.model}"

    def complete(self, system: str, user: str, gaps: list[dict]) -> str:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(system)
            sysfile = f.name
        cmd = [self.bin, *self.args, "--append-system-prompt", sysfile]
        if self.provider:
            cmd += ["--provider", self.provider]
        if self.model:
            cmd += ["--model", self.model]
        cmd += ["--", user]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired as e:
            raise BackendError(f"pi timed out after {self.timeout}s") from e
        finally:
            os.unlink(sysfile)
        if p.returncode != 0:
            raise BackendError(f"pi exited {p.returncode}: {(p.stderr or '').strip()[:400]}")
        return p.stdout


class OpenAIBackend:
    name = "openai"
    placeholder = False

    def __init__(self, cfg: dict, model: str | None = None, provider: str | None = None):
        c = cfg["openai"]
        env = os.environ
        self.base = (env.get(c["base_url_env"]) or env.get("OPENAI_BASE_URL") or "").rstrip("/")
        self.key = env.get(c["api_key_env"]) or env.get("OPENAI_API_KEY") or ""
        self.model = model or env.get(c["model_env"]) or c.get("model")
        self.temperature = c.get("temperature", 0.2)
        self.timeout = int(c.get("timeout") or 300)
        missing = [n for n, v in (("base URL", self.base), ("API key", self.key),
                                  ("model", self.model)) if not v]
        if missing:
            raise BackendError(f"openai backend needs {', '.join(missing)}: set "
                               f"{c['base_url_env']}, {c['api_key_env']} and {c['model_env']} "
                               "(or OPENAI_BASE_URL / OPENAI_API_KEY / --model)")

    @property
    def label(self) -> str:
        return f"openai-compatible / {self.model}"

    def complete(self, system: str, user: str, gaps: list[dict]) -> str:
        body = json.dumps({"model": self.model, "temperature": self.temperature,
                           "messages": [{"role": "system", "content": system},
                                        {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(f"{self.base}/chat/completions", data=body, headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read())
        except Exception as e:  # network, HTTP or JSON error
            raise BackendError(f"openai endpoint error: {e}") from e
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise BackendError(f"unexpected response shape: {str(data)[:300]}") from e


class StubBackend:
    """Deterministic PLACEHOLDER placements. Not model output."""
    name = "stub"
    placeholder = True
    model = "stub-defaults"

    def __init__(self, cfg: dict, model: str | None = None, provider: str | None = None):
        d = yaml.safe_load(Path(cfg["stub_defaults"]).read_text()) or {}
        self.checks = d.get("checks") or {}
        self.cats = d.get("categories") or {}
        self.version = str(d.get("rubric_version") or "")

    @property
    def label(self) -> str:
        return "stub (PLACEHOLDER, not model output)"

    def complete(self, system: str, user: str, gaps: list[dict]) -> str:
        out = []
        for g in gaps:
            d = self.checks.get(g["key"]) or self.cats.get(g.get("category")) or self.cats.get("default") or {"x": 0, "y": 0}
            out.append({"gap_id": g["id"],
                        "fix_label": d.get("fix_label") or f"Fix {g.get('label', g['key'])}"[:40],
                        "x": float(d["x"]), "y": float(d["y"]),
                        "rationale": "PLACEHOLDER: fixed default position for this check from "
                                     "stub_defaults.yaml; not a model judgement.",
                        "confidence": "low"})
        return json.dumps({"placements": out})


BACKENDS = {"pi": PiBackend, "openai": OpenAIBackend, "stub": StubBackend}


def make(name: str, cfg: dict, model: str | None = None, provider: str | None = None):
    if name not in BACKENDS:
        raise SystemExit(f"unknown backend {name!r}; choose from {', '.join(BACKENDS)}")
    try:
        return BACKENDS[name](cfg, model=model, provider=provider)
    except BackendError as e:
        raise SystemExit(f"backend {name}: {e}")

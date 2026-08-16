"""FastMCP server exposing NIAID Blueprint docs, OKF knowledge, and prompts.

This package serves Markdown under ``./docs``, OKF bundles under ``./okf``,
prompt personas under ``./prompts``, and Agent Skills under
``niaid-blueprint/skills`` over the Model Context Protocol (MCP)
using an HTTP (Streamable HTTP / SSE-compatible) transport.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"

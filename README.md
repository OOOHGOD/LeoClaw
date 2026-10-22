<div align="center">

# LeoClaw

A small ReAct coding agent for a workspace you control.

**English** · [简体中文](README.zh-CN.md)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square) ![Typer](https://img.shields.io/badge/Typer-009688?style=flat-square) [![MIT License](https://img.shields.io/badge/License-MIT-2563EB?style=flat-square)](LICENSE)

</div>

<p align="center">
<a href="#overview">Overview</a> · <a href="#install">Install</a> · <a href="#run">Run</a> · <a href="#structure-and-development">Structure and development</a> · <a href="#author--license">Author &amp; License</a>
</p>

---

> **Project focus** · Agent CLI


## Overview

A small ReAct-style coding agent CLI using LangChain model integrations and tool calling to inspect and modify files inside a selected workspace.


## Features

- DeepSeek and OpenAI providers selected through environment variables.
- A bounded model/tool loop with live tool-call and result output.
- Workspace-aware file reading, writing, editing, and text search.
- Shell commands launched from the workspace with a timeout.
- A pure-Python hash fallback for Windows environments that block the unsigned `xxhash` extension.

The current implementation uses an explicit Python agent loop; LangGraph is not a runtime dependency.

## Install

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

## Configure a provider

Set one provider and its API key in `.env`:

```dotenv
MODEL_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-key
```

Alternatively, use `MODEL_PROVIDER=openai` with `OPENAI_API_KEY`. Optional `DEEPSEEK_MODEL` and `OPENAI_MODEL` settings are documented in `.env.example`; choose IDs available to your account. Keep `.env` out of version control.

## Run

```powershell
leoclaw "Create a hello.py script" --workspace .\demo
```

Without `--workspace`, the CLI creates `.leoclaw-workspace` in the current directory. A run prints tool activity followed by the final response.

## Structure and development

| Path | Purpose |
| --- | --- |
| `src/leoclaw/core/` | Agent loop, runtime state, and workspace paths |
| `src/leoclaw/providers/` | DeepSeek/OpenAI model construction |
| `src/leoclaw/tools/` | File, search, and shell tools |
| `src/leoclaw/cli/` | Typer interface |
| `demo/`, `tests/` | Example workspace and automated tests |

```bash
pytest
```

File and grep tools reject resolved paths outside the workspace, including existing symlink escapes. Shell subprocesses are not an operating-system sandbox; use trusted tasks and workspaces.

## Author & License

Author / maintainer: [OOOHGOD](https://github.com/OOOHGOD) · Original contributions: [MIT License](LICENSE)

Commercial use and modification are permitted with preservation of copyright and license notices in copies or substantial portions. Third-party code, datasets, models, and media retain their own terms; see [license scope](LICENSE_SCOPE.md).

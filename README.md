# LeoClaw

LeoClaw is a small ReAct-style coding agent CLI built with Typer and LangChain.
It supports DeepSeek and OpenAI models. Its file tools resolve every path
against one workspace before reading or writing.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

To use DeepSeek, add your API key to `.env`:

```dotenv
MODEL_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-deepseek-key
DEEPSEEK_MODEL=deepseek-v4-pro
```

Do not wrap the key in quotes and do not commit `.env` to Git.

To switch back to OpenAI, change the same file:

```dotenv
MODEL_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-5.6-sol
```

## Run

```powershell
leoclaw "Create a hello.py script" --workspace .\demo
```

If `--workspace` is omitted, LeoClaw creates `.leoclaw-workspace` in the
current directory.

`DEEPSEEK_MODEL` and `OPENAI_MODEL` are optional. The default provider is
DeepSeek. LeoClaw uses LangChain's provider-specific `ChatDeepSeek` integration
so that tool calls and DeepSeek response metadata remain available to the
agent loop.

During a run, the Rich-powered CLI prints each tool call and result as it
happens, followed by the model's final answer.

On Windows systems that block LangSmith's unsigned `xxhash` extension,
LeoClaw automatically uses a deterministic pure-Python hash fallback during
startup. It does not disable or modify Windows application-control policies.

## Test

```powershell
pytest
```

## Safety boundary

File and grep tools reject paths that resolve outside the workspace, including
paths that escape through `..` or existing symlinks. `BashTool` starts commands
with the workspace as their working directory and enforces a timeout. A child
process is not an operating-system sandbox, so do not expose the CLI to
untrusted users or prompts when shell access is enabled.

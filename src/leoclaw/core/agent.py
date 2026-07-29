"""Streaming ReAct loop for LeoClaw."""

from collections.abc import Iterator
import json
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from leoclaw.core.state import RuntimeState
from leoclaw.providers import create_model
from leoclaw.tools.registry import build_tools


ACTOR_PROMPT = """You are the actor node in LeoClaw's ReAct workflow.

You implement the user's task using tools. Work inside the workspace only.

Rules:
- Use FileWriteTool for new files.
- Use FileReadTool before editing existing files.
- Use FileEditTool for focused edits.
- Use BashTool to run commands and test results.
- BashTool already runs inside the workspace. Use relative paths, never "cd /workspace".
- End with a concise summary of files changed and commands run.
"""


def _content_as_text(content: Any) -> str:
    """Normalize LangChain text or content blocks for event consumers."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        if parts:
            return "\n".join(parts)
    return str(content)


def stream_agent_events(
    task: str,
    *,
    workspace: str | Path,
    max_loops: int = 10,
) -> Iterator[dict[str, Any]]:
    """Run the actor loop and yield model, tool, and final-answer events."""
    if max_loops <= 0:
        raise ValueError("max_loops must be greater than 0")

    state = RuntimeState(Path(workspace))
    messages = [
        SystemMessage(content=ACTOR_PROMPT),
        HumanMessage(content=task),
    ]
    tools = build_tools(state)
    tools_by_name = {tool.name: tool for tool in tools}
    agent = create_model().bind_tools(tools)
    last_ai_content = ""

    def execute_tool(call: dict[str, Any]) -> Any:
        name = call["name"]
        tool = tools_by_name.get(name)
        if tool is None:
            return {"error": f"Unknown tool: {name}"}
        try:
            return tool.invoke(call.get("args", {}))
        except Exception as exc:
            return {"error": f"{type(exc).__name__}: {exc}"}

    for _ in range(max_loops):
        response = agent.invoke(messages)
        messages.append(response)
        last_ai_content = _content_as_text(response.content)
        yield {"type": "ai_message", "content": last_ai_content}

        if not response.tool_calls:
            break

        for call in response.tool_calls:
            name = call["name"]
            args = call.get("args", {})
            yield {"type": "tool_call", "name": name, "args": args}

            result = execute_tool(call)
            tool_message = ToolMessage(
                content=json.dumps(result, ensure_ascii=False, default=str),
                tool_call_id=call["id"],
                name=name,
            )
            messages.append(tool_message)
            yield {"type": "tool_result", "name": name, "result": result}

    yield {"type": "final_answer", "content": last_ai_content}

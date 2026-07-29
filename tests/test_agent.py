from __future__ import annotations

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

import leoclaw.core.agent as agent_module


class FakeTool:
    name = "file_write"

    def __init__(self):
        self.calls = []

    def invoke(self, args):
        self.calls.append(args)
        return "wrote demo.txt"


class FakeModel:
    def __init__(self):
        self.invocations = []
        self.responses = iter(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "file_write",
                            "args": {"file_path": "demo.txt", "content": "hello"},
                            "id": "call-1",
                            "type": "tool_call",
                        }
                    ],
                ),
                AIMessage(content="Created demo.txt."),
            ]
        )

    def bind_tools(self, tools):
        self.bound_tools = tools
        return self

    def invoke(self, messages):
        self.invocations.append(list(messages))
        return next(self.responses)


def test_stream_agent_events_runs_tool_loop(monkeypatch, tmp_path):
    tool = FakeTool()
    model = FakeModel()
    monkeypatch.setattr(agent_module, "build_tools", lambda state: [tool])
    monkeypatch.setattr(agent_module, "create_model", lambda: model)

    events = list(
        agent_module.stream_agent_events(
            "Create a demo file",
            workspace=tmp_path / "workspace",
        )
    )

    assert [event["type"] for event in events] == [
        "ai_message",
        "tool_call",
        "tool_result",
        "ai_message",
        "final_answer",
    ]
    assert events[1] == {
        "type": "tool_call",
        "name": "file_write",
        "args": {"file_path": "demo.txt", "content": "hello"},
    }
    assert events[2]["result"] == "wrote demo.txt"
    assert events[-1]["content"] == "Created demo.txt."
    assert tool.calls == [{"file_path": "demo.txt", "content": "hello"}]

    first_messages = model.invocations[0]
    assert isinstance(first_messages[0], SystemMessage)
    assert first_messages[0].content == agent_module.ACTOR_PROMPT
    assert isinstance(first_messages[1], HumanMessage)

    second_messages = model.invocations[1]
    assert isinstance(second_messages[-1], ToolMessage)
    assert json.loads(second_messages[-1].content) == "wrote demo.txt"
    assert second_messages[-1].tool_call_id == "call-1"


def test_stream_agent_events_reports_tool_errors(monkeypatch, tmp_path):
    model = FakeModel()
    model.responses = iter(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "missing",
                        "args": {},
                        "id": "call-2",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Could not run the tool."),
        ]
    )
    monkeypatch.setattr(agent_module, "build_tools", lambda state: [])
    monkeypatch.setattr(agent_module, "create_model", lambda: model)

    events = list(
        agent_module.stream_agent_events("Try a tool", workspace=tmp_path)
    )

    result_event = next(event for event in events if event["type"] == "tool_result")
    assert result_event["result"] == {"error": "Unknown tool: missing"}


def test_stream_agent_events_validates_max_loops(tmp_path):
    iterator = agent_module.stream_agent_events(
        "task",
        workspace=tmp_path,
        max_loops=0,
    )
    try:
        next(iterator)
    except ValueError as exc:
        assert str(exc) == "max_loops must be greater than 0"
    else:
        raise AssertionError("Expected max_loops validation to fail")

from leoclaw.core.state import RuntimeState
from leoclaw.tools.registry import build_tools


def test_build_tools_returns_expected_structured_tools(tmp_path):
    tools = build_tools(RuntimeState(tmp_path / "workspace"))
    assert [tool.name for tool in tools] == [
        "file_read",
        "file_write",
        "file_edit",
        "grep",
        "bash",
    ]
    assert all(tool.args_schema is not None for tool in tools)

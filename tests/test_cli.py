from typer.testing import CliRunner

import leoclaw.cli.app as cli_module


def test_cli_renders_streamed_events(monkeypatch, tmp_path):
    def fake_events(task, *, workspace):
        assert task == "Build demo"
        assert workspace == tmp_path
        yield {
            "type": "tool_call",
            "name": "file_write",
            "args": {"file_path": "demo.txt"},
        }
        yield {
            "type": "tool_result",
            "name": "file_write",
            "result": "wrote demo.txt",
        }
        yield {"type": "final_answer", "content": "Created `demo.txt`."}

    monkeypatch.setattr(cli_module, "stream_agent_events", fake_events)
    result = CliRunner().invoke(
        cli_module.app,
        ["Build demo", "--workspace", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "Tool call:" in result.output
    assert "file_write" in result.output
    assert "Tool result:" in result.output
    assert "wrote demo.txt" in result.output
    assert "Final answer" in result.output
    assert "Created demo.txt." in result.output

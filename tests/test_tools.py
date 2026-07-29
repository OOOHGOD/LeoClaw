from __future__ import annotations

import sys

import pytest

from leoclaw.core.paths import WorkspacePathError, workspace_path
from leoclaw.core.state import RuntimeState
from leoclaw.tools.bash_tool import BashTool
from leoclaw.tools.file_tools import FileEditTool, FileReadTool, FileWriteTool
from leoclaw.tools.grep_tool import GrepTool


@pytest.fixture
def state(tmp_path):
    return RuntimeState(tmp_path / "workspace")


def test_workspace_is_created_and_escape_is_rejected(state, tmp_path):
    assert state.workspace.is_dir()
    with pytest.raises(WorkspacePathError):
        workspace_path(state, tmp_path / "outside.txt")
    with pytest.raises(WorkspacePathError):
        workspace_path(state, "../outside.txt")


def test_file_read_write_and_unique_edit(state):
    writer = FileWriteTool(state)
    reader = FileReadTool(state)
    editor = FileEditTool(state)

    writer.run("nested/example.txt", "zero\none\ntwo\n")
    assert reader.run("nested/example.txt", offset=1, limit=1) == "one\n"

    editor.run("nested/example.txt", "one", "ONE")
    assert reader.run("nested/example.txt") == "zero\nONE\ntwo\n"


def test_file_edit_rejects_multiple_matches(state):
    FileWriteTool(state).run("duplicate.txt", "same same")
    with pytest.raises(ValueError, match="2 locations"):
        FileEditTool(state).run("duplicate.txt", "same", "new")


def test_grep_regex_glob_and_limit(state):
    writer = FileWriteTool(state)
    writer.run("a.py", "Alpha\nbeta\n")
    writer.run("b.py", "alpha two\n")
    writer.run("ignored.txt", "alpha\n")

    result = GrepTool(state).run(
        r"^alpha", glob="*.py", head_limit=1, ignore_case=True
    )
    assert result == "a.py:1:Alpha"


def test_bash_runs_in_workspace(state):
    command = f'"{sys.executable}" -c "import pathlib; print(pathlib.Path.cwd().name)"'
    result = BashTool(state).run(command, timeout_seconds=5)
    assert "exit_code=0" in result
    assert state.workspace.name in result


def test_bash_timeout(state):
    command = f'"{sys.executable}" -c "import time; time.sleep(2)"'
    with pytest.raises(TimeoutError):
        BashTool(state).run(command, timeout_seconds=0.05)

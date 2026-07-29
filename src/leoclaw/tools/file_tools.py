"""Workspace-scoped file tools."""

from dataclasses import dataclass

from leoclaw.core.paths import workspace_path
from leoclaw.core.state import RuntimeState


@dataclass(slots=True)
class FileReadTool:
    """Read UTF-8 text from a file in the workspace."""

    state: RuntimeState

    def run(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        """Read lines from a workspace file using a zero-based line offset."""
        if offset < 0:
            raise ValueError("offset must be at least 0")
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        path = workspace_path(self.state, file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        return "".join(lines[offset : offset + limit])


@dataclass(slots=True)
class FileWriteTool:
    """Create or overwrite a UTF-8 text file in the workspace."""

    state: RuntimeState

    def run(self, file_path: str, content: str) -> str:
        """Create or overwrite a file and return a short confirmation."""
        path = workspace_path(self.state, file_path)
        if path.exists() and path.is_dir():
            raise IsADirectoryError(f"Cannot write to a directory: {file_path}")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {len(content.encode('utf-8'))} bytes to {path.relative_to(self.state.workspace)}"


@dataclass(slots=True)
class FileEditTool:
    """Replace one unique text fragment in a workspace file."""

    state: RuntimeState

    def run(self, file_path: str, old_text: str, new_text: str) -> str:
        """Replace old_text only when it occurs exactly once."""
        if not old_text:
            raise ValueError("old_text must not be empty")

        path = workspace_path(self.state, file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        content = path.read_text(encoding="utf-8")
        matches = content.count(old_text)
        if matches == 0:
            raise ValueError("old_text was not found")
        if matches > 1:
            raise ValueError(f"old_text matched {matches} locations; expected exactly one")

        path.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Edited {path.relative_to(self.state.workspace)}"

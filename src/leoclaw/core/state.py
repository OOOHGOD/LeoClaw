"""Runtime state shared by all LeoClaw tools."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RuntimeState:
    """State available to tools during one agent run."""

    workspace: Path

    def __post_init__(self) -> None:
        workspace = self.workspace.expanduser().resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        if not workspace.is_dir():
            raise NotADirectoryError(f"Workspace is not a directory: {workspace}")
        object.__setattr__(self, "workspace", workspace)

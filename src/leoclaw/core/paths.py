"""Workspace path validation helpers."""

from pathlib import Path

from leoclaw.core.state import RuntimeState


class WorkspacePathError(ValueError):
    """Raised when a requested path escapes the configured workspace."""


def workspace_path(state: RuntimeState, path: str | Path = ".") -> Path:
    """Resolve *path* and ensure the result remains inside the workspace."""
    requested = Path(path).expanduser()
    candidate = requested if requested.is_absolute() else state.workspace / requested
    resolved = candidate.resolve(strict=False)

    try:
        resolved.relative_to(state.workspace)
    except ValueError as exc:
        raise WorkspacePathError(
            f"Path escapes workspace {state.workspace}: {path}"
        ) from exc
    return resolved

"""Regular-expression search tool."""

from dataclasses import dataclass
from pathlib import Path
import re

from leoclaw.core.paths import workspace_path
from leoclaw.core.state import RuntimeState


@dataclass(slots=True)
class GrepTool:
    """Search text files within the workspace."""

    state: RuntimeState

    def run(
        self,
        pattern: str,
        path: str = ".",
        glob: str = "*",
        head_limit: int = 100,
        ignore_case: bool = False,
    ) -> str:
        """Return up to head_limit matches as path:line:text."""
        if head_limit <= 0:
            raise ValueError("head_limit must be greater than 0")

        flags = re.IGNORECASE if ignore_case else 0
        expression = re.compile(pattern, flags)
        root = workspace_path(self.state, path)
        if not root.exists():
            raise FileNotFoundError(f"Search path does not exist: {path}")

        candidates = [root] if root.is_file() else root.rglob(glob)
        matches: list[str] = []

        for candidate in candidates:
            if not candidate.is_file():
                continue
            safe_candidate = workspace_path(self.state, candidate)
            try:
                lines = safe_candidate.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            relative = safe_candidate.relative_to(self.state.workspace)
            for line_number, line in enumerate(lines, start=1):
                if expression.search(line):
                    matches.append(f"{relative}:{line_number}:{line}")
                    if len(matches) >= head_limit:
                        return "\n".join(matches)

        return "\n".join(matches)

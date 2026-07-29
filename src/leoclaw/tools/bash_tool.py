"""Timed shell-command tool."""

from dataclasses import dataclass
import os
import signal
import subprocess

from leoclaw.core.state import RuntimeState


@dataclass(slots=True)
class BashTool:
    """Execute a shell command with the workspace as its working directory."""

    state: RuntimeState

    @staticmethod
    def _stop_process_tree(process: subprocess.Popen[str]) -> None:
        """Stop the shell and its descendants after a timeout."""
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            os.killpg(process.pid, signal.SIGKILL)

    def run(self, command: str, timeout_seconds: float = 30) -> str:
        """Run a command, capture combined output, and enforce a timeout."""
        if not command.strip():
            raise ValueError("command must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")
        if timeout_seconds > 300:
            raise ValueError("timeout_seconds must not exceed 300")

        process = subprocess.Popen(
            command,
            cwd=self.state.workspace,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            start_new_session=os.name != "nt",
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            ),
        )
        try:
            output, _ = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            self._stop_process_tree(process)
            remaining_output, _ = process.communicate()
            partial_output = exc.output or ""
            if isinstance(partial_output, bytes):
                partial_output = partial_output.decode("utf-8", errors="replace")
            output = partial_output + remaining_output
            raise TimeoutError(
                f"Command timed out after {timeout_seconds} seconds"
                + (f"\nPartial output:\n{output}" if output else "")
            ) from exc

        output = output.rstrip()
        return f"exit_code={process.returncode}" + (f"\n{output}" if output else "")

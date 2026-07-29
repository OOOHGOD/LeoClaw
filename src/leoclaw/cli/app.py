"""Typer application for LeoClaw's streaming agent."""

from pathlib import Path
from typing import Annotated

from rich.console import Console
from rich.markdown import Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.pretty import Pretty
import typer

from leoclaw.core.agent import stream_agent_events


app = typer.Typer(
    name="leoclaw",
    help="Run a workspace-scoped coding agent.",
    no_args_is_help=True,
)


@app.command()
def leoclaw(
    task: Annotated[str, typer.Argument(help="Task for the coding agent.")],
    workspace: Annotated[
        Path,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace directory; it is created when missing.",
        ),
    ] = Path(".leoclaw-workspace"),
) -> None:
    """Run LeoClaw on TASK."""
    console = Console()
    try:
        for event in stream_agent_events(task, workspace=workspace):
            event_type = event["type"]
            if event_type == "tool_call":
                console.print(
                    f"\n[bold cyan]Tool call:[/bold cyan] "
                    f"[cyan]{escape(event['name'])}[/cyan]"
                )
                console.print(Pretty(event["args"], expand_all=True))
            elif event_type == "tool_result":
                console.print(
                    f"[bold green]Tool result:[/bold green] "
                    f"[green]{escape(event['name'])}[/green]"
                )
                console.print(Panel.fit(str(event["result"]), border_style="green"))
            elif event_type == "final_answer":
                content = event["content"] or "(No final response.)"
                console.print(
                    Panel(
                        Markdown(content),
                        title="Final answer",
                        border_style="blue",
                    )
                )
    except Exception as exc:
        Console(stderr=True).print(f"[bold red]Error:[/bold red] {escape(str(exc))}")
        raise typer.Exit(code=1) from exc

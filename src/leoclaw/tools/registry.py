"""LangChain tool registration."""

from langchain_core.tools import StructuredTool

from leoclaw.core.state import RuntimeState
from leoclaw.tools.bash_tool import BashTool
from leoclaw.tools.file_tools import FileEditTool, FileReadTool, FileWriteTool
from leoclaw.tools.grep_tool import GrepTool


def build_tools(state: RuntimeState) -> list[StructuredTool]:
    """Build the structured tools supplied to ``model.bind_tools()``."""
    file_read = FileReadTool(state)
    file_write = FileWriteTool(state)
    file_edit = FileEditTool(state)
    grep = GrepTool(state)
    bash = BashTool(state)

    return [
        StructuredTool.from_function(
            func=file_read.run,
            name="file_read",
            description="Read a UTF-8 file inside the workspace by line offset and limit.",
        ),
        StructuredTool.from_function(
            func=file_write.run,
            name="file_write",
            description="Create or overwrite a UTF-8 file inside the workspace.",
        ),
        StructuredTool.from_function(
            func=file_edit.run,
            name="file_edit",
            description="Replace exactly one matching text fragment in a workspace file.",
        ),
        StructuredTool.from_function(
            func=grep.run,
            name="grep",
            description="Search workspace text files with a regular expression.",
        ),
        StructuredTool.from_function(
            func=bash.run,
            name="bash",
            description="Run a timed shell command with the workspace as cwd.",
        ),
    ]

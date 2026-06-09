from typing import Dict, List
from tools import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """Adds a tool to the toolbox."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """Finds a tool by its name."""
        return self._tools.get(name)

    def remove_tool(self, name: str):
        """Removes a tool by its name."""
        self._tools.pop(name)

    def get_tool_count(self):
        return len(self._tools)

    def get_all_specs(self) -> str:
        """Generates the text the LLM needs to see to understand the tools."""
        lines = []
        for t in self._tools.values():
            params = ", ".join([f"{k}: {v}" for k, v in t.parameters.items()])
            lines.append(f"- {t.name}: {t.description} Parameters: {params}")
        return "\n".join(lines)
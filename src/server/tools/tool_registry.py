from typing import Dict, List, Any
import mcp.types

class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, tool_instance):
        self.tools[name] = tool_instance
    
    def get_tool_definitions(self) -> List[mcp.types.Tool]:
        definitions = []
        for _, tool in self.tools.items():
            definitions.append(tool.get_definition())
        return definitions
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        return await self.tools[name].execute(arguments)
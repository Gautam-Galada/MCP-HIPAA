from abc import ABC, abstractmethod
from typing import Dict, Any, List
import mcp.types

class BaseTool(ABC):
    @abstractmethod
    def get_definition(self) -> mcp.types.Tool:
        """Return the tool definition for MCP registration"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
        """Execute the tool with given arguments"""
        pass
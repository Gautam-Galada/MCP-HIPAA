import asyncio
import logging
from typing import Any, Dict, List
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types
from .tools.tool_registry import ToolRegistry
from .tools.patient_info_tool import PatientInfoTool
from .tools.xray_analysis_tool import XrayAnalysisTool
from .tools.chat_tool import ChatTool
from .models.model_manager import ModelManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hipaa-medical-mcp")

class HIPAAMedicalServer:
    def __init__(self):
        self.server = Server("hipaa-medical-mcp")
        self.model_manager = ModelManager()
        self.tool_registry = ToolRegistry()
        self._setup_tools()
        self._register_handlers()
    
    def _setup_tools(self):
        self.tool_registry.register("get_patient_info", PatientInfoTool())
        self.tool_registry.register("analyze_xray", XrayAnalysisTool(self.model_manager))
        self.tool_registry.register("chat_with_agent", ChatTool())
    
    def _register_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[mcp.types.Tool]:
            return self.tool_registry.get_tool_definitions()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
            try:
                return await self.tool_registry.execute_tool(name, arguments)
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [mcp.types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def run(self):
        # Load the ML model
        self.model_manager.load_model()
        
        options = InitializationOptions(
            server_name="hipaa-medical-mcp",
            server_version="1.0.0",
            capabilities=self.server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, options)
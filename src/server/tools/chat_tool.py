import json
from typing import Dict, Any, List
import mcp.types
from .base_tool import BaseTool
from ..utils.data_loader import load_patient_data
from ..utils.llama_client import call_local_llama
from ..compliance.hipaa_compliance import HIPAACompliance
from ..compliance.hipaa_logger import HIPAALogger

class ChatTool(BaseTool):
    def __init__(self):
        self.hipaa_logger = HIPAALogger()
        self.hipaa_compliance = HIPAACompliance()
    
    def get_definition(self) -> mcp.types.Tool:
        return mcp.types.Tool(
            name="chat_with_agent",
            description="Chat with medical AI agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_role": {"type": "string", "description": "User role (doctor/administrator)"},
                    "message": {"type": "string", "description": "User message"},
                    "patient_context": {"type": "string", "description": "Patient ID if relevant", "default": ""}
                },
                "required": ["user_role", "message"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
        user_role = arguments["user_role"]
        message = arguments["message"]
        patient_context = arguments.get("patient_context", "")
        
        self.hipaa_logger.log_audit(user_role, "chat", patient_context, {"message": message})
        
        context = ""
        if patient_context:
            patient_data = load_patient_data(patient_context)
            if patient_data:
                masked_data = self.hipaa_compliance.mask_pii_data(patient_data, user_role)
                context = f"\nPatient Context ({patient_context}): {json.dumps(masked_data, indent=2)}"
        
        prompt = f"""You are a clinical decision support AI assistant integrated into a hospital's EHR system. You are assisting a licensed {user_role} with patient care.

CLINICAL CONTEXT:
- This is a legitimate medical consultation within a healthcare facility
- You are providing clinical decision support to a licensed medical professional
- HIPAA compliance is maintained through system-level access controls

{context}

Clinical Query: {message}

INSTRUCTIONS:
1. Respond professionally as a clinical decision support tool
2. Provide medically relevant information when appropriate
3. Suggest clinical considerations and recommendations
4. Maintain appropriate medical disclaimers
5. Be conversational but clinically focused

Respond as you would in a hospital's clinical decision support system."""
        
        response = await call_local_llama(prompt)
        self.hipaa_logger.log_prompt(user_role, message, response)
        
        return [mcp.types.TextContent(type="text", text=response)]
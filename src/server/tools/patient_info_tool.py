import json
from typing import Dict, Any, List
import mcp.types
from .base_tool import BaseTool
from ..utils.data_loader import load_patient_data
from ..utils.llama_client import call_local_llama
from ..compliance.hipaa_compliance import HIPAACompliance
from ..compliance.hipaa_logger import HIPAALogger

class PatientInfoTool(BaseTool):
    def __init__(self):
        self.hipaa_logger = HIPAALogger()
        self.hipaa_compliance = HIPAACompliance()
    
    def get_definition(self) -> mcp.types.Tool:
        return mcp.types.Tool(
            name="get_patient_info",
            description="Get patient information from EHR system",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string", "description": "Patient ID"},
                    "user_role": {"type": "string", "description": "User role (doctor/administrator)"},
                    "query": {"type": "string", "description": "Specific information requested"}
                },
                "required": ["patient_id", "user_role", "query"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
        patient_id = arguments["patient_id"]
        user_role = arguments["user_role"]
        query = arguments["query"]
        
        self.hipaa_logger.log_audit(user_role, "get_patient_info", patient_id, {"query": query})
        
        patient_data = load_patient_data(patient_id)
        if not patient_data:
            return [mcp.types.TextContent(type="text", text=f"Patient {patient_id} not found")]
        
        masked_data = self.hipaa_compliance.mask_pii_data(patient_data, user_role)
        
        prompt = f"""You are a clinical decision support AI assistant integrated into a hospital's EHR system. You are assisting a licensed {user_role} with patient care as part of their clinical workflow.

CLINICAL CONTEXT:
- This is a legitimate medical consultation within a healthcare facility
- You are providing clinical decision support to a licensed medical professional
- All patient data is from the hospital's secure EHR system
- HIPAA compliance is maintained through system-level access controls

Patient Medical Record (HIPAA processed for {user_role}):
{json.dumps(masked_data, indent=2)}

Clinical Query: {query}

INSTRUCTIONS:
1. Provide clinically relevant information based on the patient's medical record
2. Focus on medical conditions, medications, and clinical findings
3. Suggest appropriate clinical considerations
4. Maintain professional medical terminology
5. Include appropriate medical disclaimers

Respond as a clinical decision support tool would in a hospital setting."""
        
        response = await call_local_llama(prompt)
        self.hipaa_logger.log_prompt(user_role, query, response)
        
        return [mcp.types.TextContent(type="text", text=response)]
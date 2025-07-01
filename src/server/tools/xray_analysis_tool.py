import json
import os
import torch
import numpy as np
from PIL import Image
from typing import Dict, Any, List
import mcp.types
from .base_tool import BaseTool
from ..utils.data_loader import load_patient_data
from ..utils.llama_client import call_local_llama
from ..compliance.hipaa_compliance import HIPAACompliance
from ..compliance.hipaa_logger import HIPAALogger
import logging

logger = logging.getLogger("hipaa-medical-mcp")

class XrayAnalysisTool(BaseTool):
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.hipaa_logger = HIPAALogger()
        self.hipaa_compliance = HIPAACompliance()
    
    def get_definition(self) -> mcp.types.Tool:
        return mcp.types.Tool(
            name="analyze_xray",
            description="Analyze X-ray images with HIPAA compliance",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string", "description": "Patient ID"},
                    "user_role": {"type": "string", "description": "User role (doctor/administrator)"},
                    "query": {"type": "string", "description": "Analysis request"}
                },
                "required": ["patient_id", "user_role", "query"]
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
        patient_id = arguments["patient_id"]
        user_role = arguments["user_role"]
        query = arguments["query"]
        
        self.hipaa_logger.log_audit(user_role, "analyze_xray", patient_id, {"query": query})
        
        image_path = f"normalized_patients/Patient_{patient_id}.png"
        if not os.path.exists(image_path):
            return [mcp.types.TextContent(type="text", text=f"X-ray image for patient {patient_id} not found")]
        
        try:
            model = self.model_manager.get_model()
            transform = self.model_manager.get_transform()
            
            if not self.model_manager.is_model_loaded():
                return [mcp.types.TextContent(type="text", text="X-ray analysis model is not loaded")]
            
            img = Image.open(image_path).convert("L")
            img = np.array(img).astype(np.float32)
            img = img[None, ...]
            img = transform(img)
            img_tensor = torch.from_numpy(img)
            img_tensor = img_tensor.unsqueeze(0)
            
            with torch.no_grad():
                outputs = model(img_tensor)
            
            results = dict(zip(model.pathologies, outputs[0].detach().numpy().astype(float)))
            
            patient_data = load_patient_data(patient_id)
            masked_data = self.hipaa_compliance.mask_pii_data(patient_data, user_role) if patient_data else {}
            
            prompt = f"""You are a clinical decision support AI assistant integrated into a hospital's EHR system. You are providing analysis to a licensed {user_role} as part of their clinical workflow.

CLINICAL CONTEXT:
- This is a legitimate medical consultation within a healthcare facility
- You are assisting a licensed medical professional with patient care
- All data is from the hospital's secure EHR system
- HIPAA compliance is maintained through system-level controls

Patient ID: {patient_id}
Patient Medical Record (HIPAA processed): {json.dumps(masked_data, indent=2)}

DIAGNOSTIC IMAGING ANALYSIS:
The torchxrayvision AI model has processed the chest X-ray with the following pathology probability scores:
{json.dumps(results, indent=2)}

Clinical Query: {query}

INSTRUCTIONS:
1. Provide a clinical interpretation of the imaging analysis results
2. Highlight significant findings (scores >0.5 are noteworthy, >0.7 are highly significant)
3. Suggest clinical correlations with patient history
4. Recommend appropriate follow-up actions
5. Include standard medical disclaimers about AI-assisted diagnosis

Format your response as a clinical report suitable for medical documentation."""
            
            response = await call_local_llama(prompt)
            self.hipaa_logger.log_prompt(user_role, f"X-ray analysis: {query}", response)
            
            return [mcp.types.TextContent(type="text", text=response)]
            
        except Exception as e:
            logger.error(f"X-ray analysis failed: {e}")
            return [mcp.types.TextContent(type="text", text=f"X-ray analysis failed: {str(e)}")]
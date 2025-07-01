import json
import os
import logging

logger = logging.getLogger("hipaa-medical-mcp")

def load_patient_data(patient_id):
    """Load patient data from EHR files"""
    try:
        patient_file = f"ehr/Patient_{patient_id}.json"
        if not os.path.exists(patient_file):
            return None
        
        with open(patient_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load patient data: {e}")
        return None
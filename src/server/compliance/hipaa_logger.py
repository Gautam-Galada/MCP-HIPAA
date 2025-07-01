import json
import os
import logging
from datetime import datetime

logger = logging.getLogger("hipaa-medical-mcp")

class HIPAALogger:
    def __init__(self):
        self.audit_log = "logs/audit_log.json"
        self.prompt_log = "logs/prompt_log.json"
        self.violation_log = "logs/violation_log.json"
        os.makedirs("logs", exist_ok=True)
    
    def log_audit(self, user_role, action, patient_id, details):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_role": user_role,
            "action": action,
            "patient_id": patient_id,
            "details": details
        }
        self._write_log(self.audit_log, log_entry)
    
    def log_prompt(self, user_role, prompt, response):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_role": user_role,
            "prompt": prompt,
            "response": response
        }
        self._write_log(self.prompt_log, log_entry)
    
    def log_violation(self, user_role, violation_type, details):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_role": user_role,
            "violation_type": violation_type,
            "details": details
        }
        self._write_log(self.violation_log, log_entry)
    
    def _write_log(self, log_file, entry):
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            logs.append(entry)
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
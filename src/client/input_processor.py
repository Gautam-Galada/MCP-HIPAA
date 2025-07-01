import re

class InputProcessor:
    def extract_patient_id(self, text):
        patterns = [
            r'patient\s+(\d+)',
            r'patient\s+id\s+(\d+)',
            r'pt\s+(\d+)',
            r'patient_(\d+)',
            r'Patient_(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:return match.group(1)
        return None
    def is_patient_info_request(self, text):
        keywords = ["notes", "information", "summary", "details", "record", "history", "data"]
        return any(keyword in text.lower() for keyword in keywords)
    def is_xray_request(self, text):
        keywords = ["xray", "x-ray", "scan", "imaging", "radiolog", "chest"]
        return any(keyword in text.lower() for keyword in keywords)
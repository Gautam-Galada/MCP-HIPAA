class HIPAACompliance:
    PII_FIELDS = ["name", "ssn", "address", "phone", "email", "policy_number", "date_of_birth"]
    
    @staticmethod
    def mask_pii_data(data, user_role):
        """Mask PII data based on user role"""
        if user_role == "administrator":
            return data
        
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if key.lower() in HIPAACompliance.PII_FIELDS:
                    masked_data[key] = HIPAACompliance._mask_value(value)
                else:
                    masked_data[key] = value
            return masked_data
        return data
    
    @staticmethod
    def _mask_value(value):
        """Mask individual values"""
        if isinstance(value, str):
            if len(value) <= 4:
                return "*" * len(value)
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        return "***MASKED***"
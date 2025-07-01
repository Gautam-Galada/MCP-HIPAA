import logging
import torchxrayvision as xrv
import torch
import torchvision

logger = logging.getLogger("hipaa-medical-mcp")

class ModelManager:
    def __init__(self):
        self.model = None
        self.transform = None
    
    def load_model(self):
        try:
            logger.info("Loading DenseNet121 model for X-ray analysis...")
            self.model = xrv.models.DenseNet(weights="densenet121-res224-all")
            self.model.eval()
            
            self.transform = torchvision.transforms.Compose([
                xrv.datasets.XRayCenterCrop(),
                xrv.datasets.XRayResizer(224)
            ])
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def get_model(self):
        return self.model
    
    def get_transform(self):
        return self.transform
    
    def is_model_loaded(self):
        return self.model is not None and self.transform is not None
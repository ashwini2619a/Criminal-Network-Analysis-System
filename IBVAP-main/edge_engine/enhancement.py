import cv2
import numpy as np
from edge_engine.config import get_config

class NightVisionEnhancer:
    def __init__(self):
        self.config = get_config()
        self.clahe = cv2.createCLAHE(
            clipLimit=self.config.clahe_clip_limit, 
            tileGridSize=self.config.clahe_tile_size
        )
        
    def enhance(self, frame: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        
        l_avg = np.mean(l_channel)
        
        if l_avg < self.config.luminance_threshold:
            cl = self.clahe.apply(l_channel)
            merged = cv2.merge((cl, a, b))
            return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
            
        return frame

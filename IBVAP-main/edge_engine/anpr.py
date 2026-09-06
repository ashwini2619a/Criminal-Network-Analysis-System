import re
from dataclasses import dataclass
from typing import List
import numpy as np
import cv2
from paddleocr import PaddleOCR

from edge_engine.config import get_config
from edge_engine.detector import Detection

@dataclass
class PlateResult:
    plate_text: str
    confidence: float
    bbox: tuple[float, float, float, float]
    is_valid: bool

class ANPREngine:
    def __init__(self):
        self.config = get_config()
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        self.regex = re.compile(self.config.anpr_regex)
        
    def process(self, frame: np.ndarray, vehicle_bboxes: List[Detection]) -> List[PlateResult]:
        results = []
        for det in vehicle_bboxes:
            if det.class_name not in ['car', 'motorcycle', 'truck', 'bus']:
                continue
                
            x1, y1, x2, y2 = map(int, det.bbox)
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(frame.shape[1], x2), min(frame.shape[0], y2)
            if x2 <= x1 or y2 <= y1:
                continue
            vehicle_crop = frame[y1:y2, x1:x2]
            
            if vehicle_crop.size == 0:
                continue
                
            ocr_results = self.ocr.ocr(vehicle_crop, cls=True)
            
            if not ocr_results or not ocr_results[0]:
                continue
                
            for res in ocr_results[0]:
                box, (text, confidence) = res
                
                clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                
                if not clean_text:
                    continue
                    
                is_valid = bool(self.regex.match(clean_text))
                
                bx1 = min([p[0] for p in box]) + x1
                by1 = min([p[1] for p in box]) + y1
                bx2 = max([p[0] for p in box]) + x1
                by2 = max([p[1] for p in box]) + y1
                
                if confidence > 0.5:
                    results.append(PlateResult(
                        plate_text=clean_text,
                        confidence=confidence,
                        bbox=(float(bx1), float(by1), float(bx2), float(by2)),
                        is_valid=is_valid
                    ))
                    
        return results

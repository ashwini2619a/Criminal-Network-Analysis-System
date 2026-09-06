import threading
from typing import List, Optional
from dataclasses import dataclass
import numpy as np
from ultralytics import YOLO

from edge_engine.config import get_config

@dataclass
class Detection:
    bbox: tuple[float, float, float, float]
    confidence: float
    class_id: int
    class_name: str
    track_id: Optional[int]

class ObjectDetector:
    def __init__(self, model_path: str = 'yolov8n.pt'):
        self.config = get_config()
        self.model = YOLO(model_path)
        self.lock = threading.Lock()
        
        self.class_names = self.model.names
        
    def detect(self, frame: np.ndarray) -> List[Detection]:
        with self.lock:
            results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False, conf=0.4)
            
        detections = []
        if not results or len(results) == 0:
            return detections
            
        result = results[0]
        if result.boxes is None:
            return detections
            
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            track_id = int(box.id[0]) if box.id is not None else None
            
            name = self.class_names.get(cls_id, f"class_{cls_id}")
            
            detections.append(Detection(
                bbox=(x1, y1, x2, y2),
                confidence=conf,
                class_id=cls_id,
                class_name=name,
                track_id=track_id
            ))
            
        return detections

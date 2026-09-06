import os
import cv2
import numpy as np
from typing import List, Dict, Optional, Any
from backend.config import BBOX_COLOR_LIVE, BBOX_COLOR_UPLOADED

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("WARNING: ultralytics (YOLO) not available. Falling back to OpenCV HOG descriptor.")

class PersonDetector:
    def __init__(self):
        self.model = None
        self.hog = None
        yolo_loaded = False
        if YOLO_AVAILABLE:
            try:
                # Load YOLOv8 nano model
                self.model = YOLO('yolov8n.pt')
                yolo_loaded = True
            except Exception as e:
                print(f"Error loading YOLO model: {e}")
        
        if not yolo_loaded or self.model is None:
            try:
                if hasattr(cv2, 'HOGDescriptor'):
                    self.hog = cv2.HOGDescriptor()
                    self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            except Exception as e:
                print(f"Notice: OpenCV HOG detector fallback not loaded: {e}")
                self.hog = None

    def detect_persons(self, image_data: bytes = None, image_path: str = None, fast_mode: bool = False, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Detect persons in image and return bounding boxes and confidence scores."""
        if image_data is None and image_path is None:
            raise ValueError("Must provide either image_data or image_path")
            
        img = None
        if image_path:
            img = cv2.imread(image_path)
        else:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        if img is None:
            return []
            
        if self.model is not None:
            return self._detect_yolo(img, fast_mode, confidence_threshold)
        else:
            return self._detect_hog(img, confidence_threshold)

    def _detect_yolo(self, img: np.ndarray, fast_mode: bool, conf_threshold: float) -> List[Dict[str, Any]]:
        imgsz = 320 if fast_mode else 640
        results = self.model(img, imgsz=imgsz, conf=conf_threshold, classes=[0], verbose=False)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": conf
                })
        return detections

    def _detect_hog(self, img: np.ndarray, conf_threshold: float) -> List[Dict[str, Any]]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        boxes, weights = self.hog.detectMultiScale(gray, winStride=(8,8), padding=(4,4), scale=1.05)
        
        detections = []
        for i, (x, y, w, h) in enumerate(boxes):
            conf = float(weights[i])
            if conf >= conf_threshold:
                detections.append({
                    "bbox": [int(x), int(y), int(x+w), int(y+h)],
                    "confidence": conf
                })
        return detections

    def draw_annotated_image(self, image_data: bytes, detections: List[Dict[str, Any]], source_type: str) -> bytes:
        """Draw bounding boxes on image and return annotated JPEG bytes."""
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        color = BBOX_COLOR_LIVE if source_type == 'live' else BBOX_COLOR_UPLOADED
        
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            conf_text = f"{det['confidence']:.2f}"
            cv2.putText(img, conf_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        _, encoded_img = cv2.imencode('.jpg', img)
        return encoded_img.tobytes()

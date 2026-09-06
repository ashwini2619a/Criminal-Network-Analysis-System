import time
from collections import deque
from dataclasses import dataclass
from typing import List, Dict
import numpy as np

from edge_engine.config import get_config
from edge_engine.detector import Detection
from edge_engine.geometry import get_bottom_center

@dataclass
class BehaviorAlert:
    track_id: int
    alert_type: str
    confidence: float
    duration: float
    bbox: tuple[float, float, float, float]

class TrackState:
    def __init__(self):
        self.positions = deque(maxlen=300)
        self.timestamps = deque(maxlen=300)
        self.aspect_ratios = deque(maxlen=60)
        self.last_seen: float = time.time()

class BehaviorAnalyzer:
    def __init__(self):
        self.config = get_config()
        self.states: Dict[int, TrackState] = {}
        self._cooldowns: Dict[tuple, float] = {}
        
    def analyze(self, detections: List[Detection], timestamp: float) -> List[BehaviorAlert]:
        alerts = []
        
        stale_tracks = [tid for tid, state in self.states.items() if timestamp - state.last_seen > 10.0]
        for tid in stale_tracks:
            del self.states[tid]
            
        for det in detections:
            if det.track_id is None:
                continue
                
            tid = det.track_id
            if tid not in self.states:
                self.states[tid] = TrackState()
                
            state = self.states[tid]
            state.last_seen = timestamp
            
            x1, y1, x2, y2 = det.bbox
            width = x2 - x1
            height = y2 - y1
            
            if height == 0:
                continue
                
            centroid = get_bottom_center(det.bbox)
            state.positions.append(centroid)
            state.timestamps.append(timestamp)
            
            if det.class_name == 'person':
                ar = width / height
                state.aspect_ratios.append(ar)
                
                if len(state.aspect_ratios) >= self.config.crawl_frame_count:
                    recent_ars = list(state.aspect_ratios)[-self.config.crawl_frame_count:]
                    if all(a > self.config.crawl_ar_threshold for a in recent_ars):
                        if timestamp - self._cooldowns.get((tid, 'CRAWLING'), 0) > 30:
                            self._cooldowns[(tid, 'CRAWLING')] = timestamp
                            alerts.append(BehaviorAlert(
                                track_id=tid,
                                alert_type='CRAWLING',
                                confidence=det.confidence,
                                duration=0.0,
                                bbox=det.bbox
                            ))
                        
            if len(state.positions) > 0:
                first_time = state.timestamps[0]
                duration = timestamp - first_time
                
                if duration > self.config.loiter_timeout_sec:
                    pts = np.array(state.positions)
                    center = np.mean(pts, axis=0)
                    distances = np.linalg.norm(pts - center, axis=1)
                    
                    if np.all(distances < self.config.loiter_radius_px):
                        if timestamp - self._cooldowns.get((tid, 'LOITERING'), 0) > 30:
                            self._cooldowns[(tid, 'LOITERING')] = timestamp
                            alerts.append(BehaviorAlert(
                                track_id=tid,
                                alert_type='LOITERING',
                                confidence=det.confidence,
                                duration=duration,
                                bbox=det.bbox
                            ))
                        
        return alerts

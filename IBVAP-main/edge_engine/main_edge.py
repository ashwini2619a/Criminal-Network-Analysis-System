import argparse
import time
import logging
import signal
import sys
import cv2
import datetime
import threading
import queue
import base64
import json
import asyncio
import websockets
from collections import defaultdict
import numpy as np

from edge_engine.config import get_config
from edge_engine.stream import RTSPStreamReader
from edge_engine.enhancement import NightVisionEnhancer
from edge_engine.detector import ObjectDetector
from edge_engine.geometry import DirectionalTripwire, PolygonZone, get_bottom_center
from edge_engine.behavior import BehaviorAnalyzer, BehaviorAlert
from edge_engine.frs import FaceRecognitionSystem
from edge_engine.anpr import ANPREngine
from edge_engine.security import ChainOfCustody

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

running = True

def signal_handler(sig, frame):
    global running
    logger.info("Graceful shutdown initiated...")
    running = False

class FrameStreamer:
    def __init__(self, url):
        self.url = url
        self.queue = queue.Queue(maxsize=10)
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def send_frame(self, frame_b64: str):
        try:
            self.queue.put(frame_b64, block=False)
        except queue.Full:
            pass

    def stop(self):
        self.running = False
        self.thread.join(timeout=2.0)

    def _run_loop(self):
        asyncio.run(self._ws_loop())

    async def _ws_loop(self):
        while self.running:
            try:
                async with websockets.connect(self.url) as ws:
                    while self.running:
                        try:
                            frame_b64 = self.queue.get(timeout=1.0)
                            await ws.send(frame_b64)
                        except queue.Empty:
                            pass
            except Exception as e:
                logger.error(f"WebSocket streamer error: {e}")
                await asyncio.sleep(2.0)

class AlertStreamer:
    def __init__(self, url):
        self.url = url
        self.queue = queue.Queue(maxsize=50)
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def send_alert(self, alert_data: dict):
        try:
            self.queue.put(json.dumps(alert_data), block=False)
        except queue.Full:
            pass

    def stop(self):
        self.running = False
        self.thread.join(timeout=2.0)

    def _run_loop(self):
        asyncio.run(self._ws_loop())

    async def _ws_loop(self):
        while self.running:
            try:
                async with websockets.connect(self.url) as ws:
                    while self.running:
                        try:
                            alert_json = self.queue.get(timeout=1.0)
                            await ws.send(alert_json)
                        except queue.Empty:
                            pass
            except Exception as e:
                logger.error(f"WebSocket alert streamer error: {e}")
                await asyncio.sleep(2.0)

def main():
    parser = argparse.ArgumentParser(description="IBVAP Edge Engine")
    parser.add_argument("--rtsp_url", type=str, help="Override RTSP URL")
    args = parser.parse_args()

    config = get_config()
    if args.rtsp_url:
        config.rtsp_url = args.rtsp_url

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Initializing components...")
    
    stream = RTSPStreamReader()
    enhancer = NightVisionEnhancer()
    detector = ObjectDetector()
    behavior_analyzer = BehaviorAnalyzer()
    frs = FaceRecognitionSystem()
    anpr = ANPREngine()
    coc = ChainOfCustody()

    tripwires = [DirectionalTripwire((100, 300), (500, 300))]
    zones = [PolygonZone([(10, 10), (200, 10), (200, 200), (10, 200)], zone_type='exclusion')]
    
    ws_stream_url = f"ws://localhost:8000/ws/stream/{config.camera_id}"
    ws_alerts_url = config.backend_ws_url
    
    frame_streamer = FrameStreamer(ws_stream_url)
    alert_streamer = AlertStreamer(ws_alerts_url)
    
    stream.start()
    coc.start_sync_worker()
    
    logger.info("Edge Engine started.")
    
    track_history = {}
    
    while running:
        frame = stream.read()
        if frame is None:
            time.sleep(0.01)
            continue
            
        timestamp_curr = time.time()
        iso_time = datetime.datetime.fromtimestamp(timestamp_curr).isoformat()
        
        # 1. Enhancement
        enhanced_frame = enhancer.enhance(frame)
        
        # 2. Detection
        detections = detector.detect(enhanced_frame)
        
        # 3. Geometry & Rules
        alerts = []
        for det in detections:
            if det.track_id is None:
                continue
                
            bottom_center = get_bottom_center(det.bbox)
            
            for zone in zones:
                if zone.check_breach(bottom_center):
                    alerts.append(BehaviorAlert(det.track_id, 'ZONE_BREACH', det.confidence, 0.0, det.bbox))
                    
            if det.track_id in track_history:
                prev_pos = track_history[det.track_id]
                for tw in tripwires:
                    cross_res = tw.check_crossing(prev_pos, bottom_center)
                    if cross_res:
                        alerts.append(BehaviorAlert(det.track_id, 'TRIPWIRE_BREACH', det.confidence, 0.0, det.bbox))
            
            track_history[det.track_id] = bottom_center
        
        # 4. Behavior Analysis
        behavior_alerts = behavior_analyzer.analyze(detections, timestamp_curr)
        alerts.extend(behavior_alerts)
        
        for alert in alerts:
            hsh = coc.hash_evidence(frame, config.camera_id, iso_time, config.bop_id, alert.alert_type)
            coc.store_event(config.bop_id, config.camera_id, iso_time, alert.alert_type, hsh, frame)
            logger.warning(f"Alert: {alert.alert_type} for track {alert.track_id}")
            
            _, buffer = cv2.imencode('.jpg', frame)
            thumbnail_b64 = base64.b64encode(buffer).decode('utf-8')
            
            alert_payload = {
                'bop_id': config.bop_id,
                'camera_id': config.camera_id,
                'timestamp': iso_time,
                'alert_type': alert.alert_type,
                'sha256_hash': hsh,
                'severity': 'HIGH',
                'description': f"{alert.alert_type} detected",
                'thumbnail_b64': thumbnail_b64
            }
            alert_streamer.send_alert(alert_payload)

        # 5. Face Recognition
        person_detections = [d for d in detections if d.class_name == 'person']
        if person_detections:
            face_matches = frs.identify(enhanced_frame)
            for fm in face_matches:
                cv2.rectangle(frame, (int(fm.bbox[0]), int(fm.bbox[1])), (int(fm.bbox[2]), int(fm.bbox[3])), (0, 255, 0), 2)
                cv2.putText(frame, fm.person_id, (int(fm.bbox[0]), int(fm.bbox[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

        # 6. ANPR
        vehicle_detections = [d for d in detections if d.class_name in ['car', 'motorcycle', 'truck', 'bus']]
        if vehicle_detections:
            plates = anpr.process(enhanced_frame, vehicle_detections)
            for plate in plates:
                if plate.is_valid:
                    cv2.putText(frame, plate.plate_text, (int(plate.bbox[0]), int(plate.bbox[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)

        # Render overlays
        for tw in tripwires:
            cv2.line(frame, (int(tw.p1[0]), int(tw.p1[1])), (int(tw.p2[0]), int(tw.p2[1])), (0, 0, 255), 2)
            
        for zone in zones:
            color = (0, 165, 255) if zone.zone_type == 'exclusion' else (0, 255, 255)
            pts = np.array(zone.vertices, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, color, 2)

        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{det.class_name} {det.track_id}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        # Stream frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame_b64 = base64.b64encode(buffer).decode('utf-8')
        frame_streamer.send_frame(frame_b64)

    logger.info("Cleaning up...")
    stream.stop()
    coc.stop_sync_worker()
    frame_streamer.stop()
    alert_streamer.stop()
    cv2.destroyAllWindows()
    logger.info("Exited.")

if __name__ == '__main__':
    main()

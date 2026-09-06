import os
import cv2
import time
import threading
import queue
import logging
from typing import Optional
import numpy as np

from edge_engine.config import get_config

logger = logging.getLogger(__name__)

class RTSPStreamReader:
    def __init__(self, rtsp_url: Optional[str] = None):
        self.config = get_config()
        self.rtsp_url = rtsp_url or self.config.rtsp_url
        self.queue: queue.Queue = queue.Queue(maxsize=self.config.frame_queue_size)
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.current_fps = self.config.fps_static
        self.last_frame_gray: Optional[np.ndarray] = None
        self._is_alive = False
        
    def start(self) -> None:
        if self.thread is not None and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        
    def stop(self) -> None:
        self._stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=2.0)
        self._is_alive = False

    def read(self) -> Optional[np.ndarray]:
        try:
            return self.queue.get(timeout=0.1)
        except queue.Empty:
            return None

    def is_alive(self) -> bool:
        return self._is_alive

    def _capture_loop(self) -> None:
        reconnect_delay = 1
        
        while not self._stop_event.is_set():
            logger.info(f"Connecting to RTSP stream: {self.rtsp_url}")
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            
            if not cap.isOpened():
                logger.error(f"Failed to open stream. Retrying in {reconnect_delay}s...")
                time.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, self.config.reconnect_max_delay)
                continue
                
            self._is_alive = True
            reconnect_delay = 1
            
            while not self._stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Stream disconnected or EOF.")
                    self._is_alive = False
                    break
                    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if self.last_frame_gray is not None:
                    diff = cv2.absdiff(self.last_frame_gray, gray)
                    motion_score = np.sum(diff > 25)
                    if motion_score > 5000:
                        self.current_fps = self.config.fps_active
                    else:
                        self.current_fps = self.config.fps_static
                self.last_frame_gray = gray
                
                if self.queue.full():
                    try:
                        self.queue.get_nowait()
                    except queue.Empty:
                        pass
                
                self.queue.put(frame)
                time.sleep(1.0 / self.current_fps)
                
            cap.release()

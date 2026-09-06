import os
from pydantic import BaseModel, Field

class EdgeConfig(BaseModel):
    rtsp_url: str = Field(default=os.getenv('IBVAP_RTSP_URL', 'rtsp://localhost:8554/stream'))
    camera_id: str = Field(default=os.getenv('IBVAP_CAMERA_ID', 'cam_001'))
    bop_id: str = Field(default=os.getenv('IBVAP_BOP_ID', 'bop_01'))
    fps_static: int = Field(default=int(os.getenv('IBVAP_FPS_STATIC', '8')))
    fps_active: int = Field(default=int(os.getenv('IBVAP_FPS_ACTIVE', '25')))
    frame_queue_size: int = Field(default=int(os.getenv('IBVAP_FRAME_QUEUE_SIZE', '30')))
    clahe_clip_limit: float = Field(default=float(os.getenv('IBVAP_CLAHE_CLIP_LIMIT', '3.0')))
    clahe_tile_size: tuple[int, int] = Field(default=(8, 8))
    luminance_threshold: int = Field(default=int(os.getenv('IBVAP_LUMINANCE_THRESHOLD', '65')))
    crawl_ar_threshold: float = Field(default=float(os.getenv('IBVAP_CRAWL_AR_THRESHOLD', '1.35')))
    crawl_frame_count: int = Field(default=int(os.getenv('IBVAP_CRAWL_FRAME_COUNT', '6')))
    loiter_radius_px: int = Field(default=int(os.getenv('IBVAP_LOITER_RADIUS_PX', '100')))
    loiter_timeout_sec: int = Field(default=int(os.getenv('IBVAP_LOITER_TIMEOUT_SEC', '45')))
    face_similarity_threshold: float = Field(default=float(os.getenv('IBVAP_FACE_SIMILARITY_THRESHOLD', '0.68')))
    anpr_regex: str = Field(default=os.getenv('IBVAP_ANPR_REGEX', r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$'))
    backend_ws_url: str = Field(default=os.getenv('IBVAP_BACKEND_WS_URL', 'ws://localhost:8000/ws/alerts'))
    backend_api_url: str = Field(default=os.getenv('IBVAP_BACKEND_API_URL', 'http://localhost:8000/api/v1/alerts'))
    faiss_index_path: str = Field(default=os.getenv('IBVAP_FAISS_INDEX_PATH', 'faces.index'))
    sqlite_db_path: str = Field(default=os.getenv('IBVAP_SQLITE_DB_PATH', 'offline_audit.db'))
    sync_interval_sec: int = Field(default=int(os.getenv('IBVAP_SYNC_INTERVAL_SEC', '10')))
    reconnect_max_delay: int = Field(default=int(os.getenv('IBVAP_RECONNECT_MAX_DELAY', '30')))

_config_instance = None

def get_config() -> EdgeConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = EdgeConfig()
    return _config_instance

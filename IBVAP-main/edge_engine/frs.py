import os
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import faiss
import pickle

from edge_engine.config import get_config

@dataclass
class FaceMatch:
    bbox: tuple[float, float, float, float]
    person_id: str
    similarity: float
    embedding: np.ndarray

class FaceRecognitionSystem:
    def __init__(self):
        self.config = get_config()
        self.lock = threading.Lock()
        
        self.app = FaceAnalysis(name='buffalo_l', root='~/.insightface', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        self.embedding_dim = 512
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.id_map: Dict[int, str] = {}
        
        self.load_index()
        
    def enroll(self, face_image: np.ndarray, person_id: str) -> bool:
        with self.lock:
            faces = self.app.get(face_image)
            if not faces or len(faces) != 1:
                return False
                
            embedding = faces[0].normed_embedding
            faiss.normalize_L2(embedding.reshape(1, -1))
            
            idx = self.index.ntotal
            self.index.add(embedding.reshape(1, -1))
            self.id_map[idx] = person_id
            
            self.save_index()
            return True
            
    def identify(self, frame: np.ndarray) -> List[FaceMatch]:
        matches = []
        faces = self.app.get(frame)
        
        if not faces or self.index.ntotal == 0:
            return matches
            
        with self.lock:
            for face in faces:
                embedding = face.normed_embedding.reshape(1, -1)
                faiss.normalize_L2(embedding)
                
                distances, indices = self.index.search(embedding, 1)
                best_dist = float(distances[0][0])
                best_idx = int(indices[0][0])
                
                bbox = (float(face.bbox[0]), float(face.bbox[1]), float(face.bbox[2]), float(face.bbox[3]))
                
                if best_dist >= self.config.face_similarity_threshold:
                    person_id = self.id_map.get(best_idx, "Unknown")
                    matches.append(FaceMatch(bbox=bbox, person_id=person_id, similarity=best_dist, embedding=face.normed_embedding))
                else:
                    matches.append(FaceMatch(bbox=bbox, person_id="Unknown", similarity=best_dist, embedding=face.normed_embedding))
                    
        return matches

    def save_index(self):
        faiss.write_index(self.index, self.config.faiss_index_path)
        with open(self.config.faiss_index_path + '.map', 'wb') as f:
            pickle.dump(self.id_map, f)
            
    def load_index(self):
        if os.path.exists(self.config.faiss_index_path):
            self.index = faiss.read_index(self.config.faiss_index_path)
            map_path = self.config.faiss_index_path + '.map'
            if os.path.exists(map_path):
                with open(map_path, 'rb') as f:
                    self.id_map = pickle.load(f)

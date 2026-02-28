import numpy as np
from insightface.app import FaceAnalysis
import torch
import cv2
from typing import Optional


class RecognitionService:
    def __init__(self):
        self.app = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize InsightFace model"""
        try:
            self.app = FaceAnalysis(
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
            )
            ctx_id = 0 if torch.cuda.is_available() else -1
            self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))
        except Exception as e:
            print(f"Error initializing InsightFace: {e}")
            raise

    def extract_embedding(self, img: np.ndarray) -> Optional[np.ndarray]:
        """Extract face embedding from image"""
        try:
            if img is None:
                return None

            faces = self.app.get(img)
            if len(faces) == 0:
                return None

            # Get the largest face
            face = max(
                faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1])
            )
            embedding = face.embedding

            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)

            return embedding
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            return None

    def compare_embeddings(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)


# Singleton instance
recognition_service = RecognitionService()

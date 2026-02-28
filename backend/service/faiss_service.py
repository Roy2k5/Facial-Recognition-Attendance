import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Optional


class FaissService:
    def __init__(self, dimension: int = 512, index_path: str = "faiss_index.bin"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.employee_ids: List[str] = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if os.path.exists(self.index_path):
            self.load_index()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.employee_ids = []

    def add_embedding(self, employee_id: str, embedding: np.ndarray):
        """Add new embedding to index"""
        if embedding.shape[0] != self.dimension:
            raise ValueError(f"Embedding dimension must be {self.dimension}")

        embedding = embedding.reshape(1, -1).astype("float32")

        # Normalize embedding
        faiss.normalize_L2(embedding)

        self.index.add(embedding)
        self.employee_ids.append(employee_id)
        self.save_index()

    def search(self, embedding: np.ndarray, k: int = 1) -> Optional[Tuple[str, float]]:
        """Search for nearest neighbor"""
        if self.index.ntotal == 0:
            return None

        embedding = embedding.reshape(1, -1).astype("float32")

        # Normalize embedding
        faiss.normalize_L2(embedding)

        distances, indices = self.index.search(embedding, k)

        if len(indices[0]) > 0:
            idx = indices[0][0]
            distance = distances[0][0]

            # Convert L2 distance to cosine similarity
            # After normalization: cosine_similarity = 1 - (L2_distance^2 / 2)
            similarity = 1 - (distance**2) / 2

            return self.employee_ids[idx], float(similarity)

        return None

    def remove_embedding(self, employee_id: str):
        """Remove embedding by rebuilding index"""
        if employee_id in self.employee_ids:
            idx = self.employee_ids.index(employee_id)
            self.employee_ids.pop(idx)
            # Note: FAISS doesn't support direct deletion, need to rebuild index

    def save_index(self):
        """Save index and employee_ids to disk"""
        faiss.write_index(self.index, self.index_path)
        with open(self.index_path + ".meta", "wb") as f:
            pickle.dump(self.employee_ids, f)

    def load_index(self):
        """Load index and employee_ids from disk"""
        self.index = faiss.read_index(self.index_path)
        with open(self.index_path + ".meta", "rb") as f:
            self.employee_ids = pickle.load(f)

    def clear_index(self):
        """Clear all data"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.employee_ids = []
        self.save_index()


# Singleton instance
faiss_service = FaissService()

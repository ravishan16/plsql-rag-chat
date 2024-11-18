import numpy as np
import hashlib
from typing import List
from langchain.embeddings.base import Embeddings

class SimpleHashEmbeddings(Embeddings):
    """Simple deterministic hash-based embeddings for testing"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def _hash_text(self, text: str) -> List[float]:
        hash_object = hashlib.sha256(text.encode())
        hash_hex = hash_object.hexdigest()
        
        float_array = []
        for i in range(0, len(hash_hex), 8):
            chunk = hash_hex[i:i+8]
            float_val = int(chunk, 16) / 2**32 - 1
            float_array.append(float_val)
        
        array = np.array(float_array, dtype=np.float32)
        
        if len(array) < self.dimension:
            array = np.pad(array, (0, self.dimension - len(array)))
        else:
            array = array[:self.dimension]
            
        norm = np.linalg.norm(array)
        if norm > 0:
            array = array / norm
            
        return array.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts"""
        return [self._hash_text(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single text"""
        return self._hash_text(text)

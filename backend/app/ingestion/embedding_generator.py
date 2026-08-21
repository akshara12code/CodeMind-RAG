"""Lightweight semantic search without heavy embeddings"""
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List
import numpy as np

class EmbeddingGenerator:
    """Lightweight TF-IDF based semantic search"""
    
    def __init__(self):
        """Initialize TF-IDF vectorizer"""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.fitted = False
        self.embedding_dim = 1000
        print(f"TF-IDF vectorizer ready. Dimension: {self.embedding_dim}")
    
    def embed_text(self, text: str) -> List[float]:
        """Get TF-IDF representation"""
        if not self.fitted:
            return [0] * self.embedding_dim
        
        try:
            vector = self.vectorizer.transform([text]).toarray()[0]
            return vector.tolist()
        except:
            return [0] * self.embedding_dim
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Fit vectorizer on texts and return embeddings"""
        self.vectorizer.fit(texts)
        self.fitted = True
        
        vectors = self.vectorizer.transform(texts).toarray()
        return [v.tolist() for v in vectors]
    
    def embed_chunk(self, chunk: dict) -> dict:
        """Embed code chunk"""
        text = f"""
File: {chunk['file_path']}
Symbol: {chunk['symbol_name']} ({chunk['symbol_type']})
Language: {chunk['language']}

{chunk['code']}
"""
        # Don't embed yet - will batch embed during indexing
        chunk['text_for_embedding'] = text
        return chunk
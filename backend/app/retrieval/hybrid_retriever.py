"""
Hybrid retrieval: combines vector search, BM25, and reranking
"""

import asyncio
import logging
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
import numpy as np

from app.core.models import (
    CodeChunk, RetrievedChunk, QueryAnalysis, RetrievalTrace
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class Retriever(ABC):
    """Abstract base retriever"""
    
    @abstractmethod
    async def retrieve(
        self,
        repository_id: str,
        query: str,
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Retrieve relevant chunks
        Returns: List[(chunk_id, score)]
        """
        pass


class VectorRetriever(Retriever):
    """Vector similarity search using Qdrant"""
    
    def __init__(self, embedding_client):
        self.embedding_client = embedding_client
        self.vector_store = None  # Qdrant client
    
    async def retrieve(
        self,
        repository_id: str,
        query: str,
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Semantic search using dense embeddings
        """
        try:
            # Embed the query
            query_embedding = await self.embedding_client.embed(query)
            
            # Search in Qdrant with metadata filtering
            results = await self.vector_store.search(
                collection_name=f"repo_{repository_id}",
                query_vector=query_embedding,
                query_filter={
                    "key": "repository_id",
                    "match": {"value": repository_id}
                },
                limit=top_k
            )
            
            # Extract results
            chunk_scores = []
            for result in results:
                chunk_id = result.payload.get("chunk_id")
                score = float(result.score)
                chunk_scores.append((chunk_id, score))
            
            return chunk_scores
        
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")
            return []


class BM25Retriever(Retriever):
    """Keyword search using BM25"""
    
    def __init__(self, bm25_index):
        self.bm25_index = bm25_index
    
    async def retrieve(
        self,
        repository_id: str,
        query: str,
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Keyword search using BM25
        """
        try:
            # Tokenize query
            query_tokens = query.lower().split()
            
            # Search in BM25 index
            results = await self.bm25_index.search(
                repository_id=repository_id,
                query_tokens=query_tokens,
                top_k=top_k
            )
            
            return results
        
        except Exception as e:
            logger.error(f"BM25 retrieval failed: {e}")
            return []


class ReciprocalRankFusion:
    """
    Reciprocal Rank Fusion (RRF) for combining multiple ranked lists
    
    RRF(d) = Σ 1 / (k + rank(d))
    where k is typically 60
    """
    
    @staticmethod
    def fuse(
        vector_results: List[Tuple[str, float]],
        bm25_results: List[Tuple[str, float]],
        k: int = 60
    ) -> List[Tuple[str, float]]:
        """
        Fuse results from multiple retrievers
        """
        rrf_scores: Dict[str, float] = {}
        
        # Score vector results
        for rank, (chunk_id, _) in enumerate(vector_results, 1):
            score = 1.0 / (k + rank)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + score
        
        # Score BM25 results
        for rank, (chunk_id, _) in enumerate(bm25_results, 1):
            score = 1.0 / (k + rank)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + score
        
        # Sort by combined score
        fused = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return fused


class CrossEncoderReranker:
    """Cross-encoder based reranking for precision"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.RERANKER_MODEL
        self.model = None  # Load from settings
    
    async def rerank(
        self,
        query: str,
        candidates: List[CodeChunk],
        top_k: int = 5
    ) -> List[Tuple[CodeChunk, float]]:
        """
        Rerank candidates using cross-encoder
        
        Returns:
            List[(chunk, score)]
        """
        if not candidates:
            return []
        
        try:
            # Prepare query-chunk pairs
            pairs = []
            for chunk in candidates:
                # Use first 500 chars of code for efficiency
                chunk_text = chunk.code[:500]
                pairs.append([query, chunk_text])
            
            # Score with cross-encoder
            scores = await self._score_pairs(pairs)
            
            # Combine chunks with scores
            ranked = list(zip(candidates, scores))
            
            # Sort by score and take top-k
            ranked_sorted = sorted(
                ranked,
                key=lambda x: x[1],
                reverse=True
            )
            
            return ranked_sorted[:top_k]
        
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fallback to original order
            return [(chunk, 0.5) for chunk in candidates[:top_k]]
    
    async def _score_pairs(self, pairs: List[List[str]]) -> List[float]:
        """Score query-chunk pairs (placeholder)"""
        # In production, this would call the cross-encoder model
        return [0.5] * len(pairs)


class HybridRetriever:
    """
    Hybrid retriever combining:
    - Vector semantic search
    - BM25 keyword search
    - RRF fusion
    - Cross-encoder reranking
    """
    
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        bm25_retriever: BM25Retriever,
        reranker: CrossEncoderReranker
    ):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.reranker = reranker
        self.chunk_store = None  # Database access
    
    async def retrieve(
        self,
        repository_id: str,
        query: str,
        query_analysis: Optional[QueryAnalysis] = None,
        top_k: int = None,
        use_reranking: bool = True,
        debug: bool = False
    ) -> Tuple[List[RetrievedChunk], Optional[RetrievalTrace]]:
        """
        Full hybrid retrieval pipeline
        
        Returns:
            (retrieved_chunks, trace)
        """
        top_k = top_k or settings.RERANKER_TOP_K
        
        trace = None
        if debug:
            trace = RetrievalTrace(
                query_id=str(id(query)),
                query_analysis=query_analysis,
                vector_results=[],
                vector_latency_ms=0,
                bm25_results=[],
                bm25_latency_ms=0,
                fused_results=[],
                reranked_results=[],
                reranking_latency_ms=0,
                final_chunks=[],
                context_tokens=0,
                context_latency_ms=0
            )
        
        # 1. Parallel retrieval (vector + BM25)
        start_time = self._time()
        vector_results, bm25_results = await asyncio.gather(
            self.vector_retriever.retrieve(
                repository_id,
                query,
                settings.VECTOR_TOP_K
            ),
            self.bm25_retriever.retrieve(
                repository_id,
                query,
                settings.BM25_TOP_K
            )
        )
        
        if trace:
            trace.vector_results = vector_results
            trace.vector_latency_ms = self._time() - start_time
            trace.bm25_results = bm25_results
            trace.bm25_latency_ms = self._time() - start_time
        
        logger.info(f"Vector results: {len(vector_results)}, BM25 results: {len(bm25_results)}")
        
        # 2. Fusion (Reciprocal Rank Fusion)
        fused_results = ReciprocalRankFusion.fuse(
            vector_results,
            bm25_results,
            k=settings.RRF_K
        )
        
        if trace:
            trace.fused_results = fused_results
        
        logger.info(f"Fused results: {len(fused_results)}")
        
        # 3. Load chunks from store
        chunk_ids = [chunk_id for chunk_id, _ in fused_results]
        chunks = await self.chunk_store.get_chunks(
            chunk_ids=chunk_ids[:settings.VECTOR_TOP_K]
        )
        
        # 4. Reranking
        reranked_chunks = chunks
        if use_reranking and len(chunks) > 0:
            start_time = self._time()
            
            reranked_tuples = await self.reranker.rerank(
                query=query,
                candidates=chunks,
                top_k=top_k
            )
            
            reranked_chunks = [chunk for chunk, _ in reranked_tuples]
            
            if trace:
                trace.reranked_results = [
                    RetrievedChunk(
                        chunk=chunk,
                        rerank_score=score
                    )
                    for chunk, score in reranked_tuples
                ]
                trace.reranking_latency_ms = self._time() - start_time
        
        # 5. Build RetrievedChunk objects with scores
        retrieved = []
        for chunk in reranked_chunks[:top_k]:
            # Find original scores
            vector_score = next(
                (score for cid, score in vector_results if cid == chunk.chunk_id),
                None
            )
            bm25_score = next(
                (score for cid, score in bm25_results if cid == chunk.chunk_id),
                None
            )
            fusion_score = next(
                (score for cid, score in fused_results if cid == chunk.chunk_id),
                None
            )
            
            retrieved_chunk = RetrievedChunk(
                chunk=chunk,
                vector_score=vector_score,
                bm25_score=bm25_score,
                fusion_score=fusion_score,
                final_score=fusion_score or 0.5
            )
            retrieved.append(retrieved_chunk)
        
        if trace:
            trace.final_chunks = retrieved
        
        logger.info(f"Retrieved {len(retrieved)} final chunks")
        
        return retrieved, trace
    
    @staticmethod
    def _time() -> float:
        """Get current time in milliseconds"""
        import time
        return time.time() * 1000


class MetadataFilter:
    """Filter results by metadata"""
    
    @staticmethod
    def filter_by_language(
        chunks: List[CodeChunk],
        languages: List[str]
    ) -> List[CodeChunk]:
        """Filter chunks by language"""
        return [c for c in chunks if c.language in languages]
    
    @staticmethod
    def filter_by_path(
        chunks: List[CodeChunk],
        path_patterns: List[str]
    ) -> List[CodeChunk]:
        """Filter chunks by file path patterns"""
        result = []
        for chunk in chunks:
            for pattern in path_patterns:
                if pattern in chunk.file_path:
                    result.append(chunk)
                    break
        return result
    
    @staticmethod
    def filter_by_symbol_type(
        chunks: List[CodeChunk],
        symbol_types: List[str]
    ) -> List[CodeChunk]:
        """Filter chunks by symbol type"""
        return [c for c in chunks if c.symbol_type and c.symbol_type.value in symbol_types]

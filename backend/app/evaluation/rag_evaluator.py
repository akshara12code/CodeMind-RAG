"""
RAG Evaluation Framework
Measure retrieval quality and generation fidelity
"""

import logging
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from app.core.models import (
    BenchmarkQuery, RetrievedChunk, EvaluationMetrics,
    RetrievalStrategyComparison, QueryType
)

logger = logging.getLogger(__name__)


@dataclass
class RetrievalMetrics:
    """Retrieval performance metrics"""
    query_id: str
    query: str
    expected_chunk_ids: Set[str]
    expected_files: Set[str]
    expected_symbols: Set[str]
    
    retrieved_chunk_ids: Set[str]
    retrieved_files: Set[str]
    retrieved_symbols: Set[str]
    
    def recall_at_k(self, k: int = 5) -> float:
        """Recall@k: % of relevant chunks in top-k"""
        if not self.expected_chunk_ids:
            return 1.0
        
        retrieved_at_k = self.retrieved_chunk_ids
        if isinstance(retrieved_at_k, list):
            retrieved_at_k = set(retrieved_at_k[:k])
        
        hits = len(self.expected_chunk_ids & retrieved_at_k)
        return hits / len(self.expected_chunk_ids)
    
    def precision_at_k(self, k: int = 5) -> float:
        """Precision@k: % of top-k that are relevant"""
        if not self.retrieved_chunk_ids:
            return 0.0
        
        retrieved_at_k = self.retrieved_chunk_ids
        if isinstance(retrieved_at_k, list):
            retrieved_at_k = set(retrieved_at_k[:k])
        
        if len(retrieved_at_k) == 0:
            return 0.0
        
        hits = len(self.expected_chunk_ids & retrieved_at_k)
        return hits / len(retrieved_at_k)
    
    def mrr(self) -> float:
        """Mean Reciprocal Rank: 1/rank of first relevant"""
        for rank, chunk_id in enumerate(self.retrieved_chunk_ids, 1):
            if chunk_id in self.expected_chunk_ids:
                return 1.0 / rank
        return 0.0
    
    def hit_rate(self) -> bool:
        """Binary: did we retrieve at least one relevant chunk?"""
        return len(self.expected_chunk_ids & self.retrieved_chunk_ids) > 0
    
    def file_recall(self) -> float:
        """% of expected files retrieved"""
        if not self.expected_files:
            return 1.0
        hits = len(self.expected_files & self.retrieved_files)
        return hits / len(self.expected_files)
    
    def symbol_recall(self) -> float:
        """% of expected symbols retrieved"""
        if not self.expected_symbols:
            return 1.0
        hits = len(self.expected_symbols & self.retrieved_symbols)
        return hits / len(self.expected_symbols)


@dataclass
class GenerationMetrics:
    """Generation quality metrics"""
    query_id: str
    query: str
    response: str
    
    # Grounding metrics
    grounded_claims: int
    ungrounded_claims: int
    total_claims: int
    
    # Citation metrics
    citations_present: int
    correct_citations: int
    
    @property
    def faithfulness(self) -> float:
        """% of claims grounded in evidence"""
        if self.total_claims == 0:
            return 1.0
        return self.grounded_claims / self.total_claims
    
    @property
    def citation_accuracy(self) -> float:
        """% of citations that point to correct code"""
        if self.citations_present == 0:
            return 1.0
        return self.correct_citations / self.citations_present
    
    @property
    def hallucination_rate(self) -> float:
        """% of ungrounded claims"""
        if self.total_claims == 0:
            return 0.0
        return self.ungrounded_claims / self.total_claims


class MetricsAggregator:
    """Aggregate metrics across multiple queries"""
    
    def __init__(self):
        self.retrieval_metrics: List[RetrievalMetrics] = []
        self.generation_metrics: List[GenerationMetrics] = []
    
    def add_retrieval_result(self, metrics: RetrievalMetrics):
        """Add retrieval result"""
        self.retrieval_metrics.append(metrics)
    
    def add_generation_result(self, metrics: GenerationMetrics):
        """Add generation result"""
        self.generation_metrics.append(metrics)
    
    def aggregate(self) -> EvaluationMetrics:
        """Compute aggregate metrics"""
        if not self.retrieval_metrics:
            logger.warning("No retrieval metrics to aggregate")
            return EvaluationMetrics(
                recall_at_5=0.0,
                recall_at_10=0.0,
                precision_at_5=0.0,
                precision_at_10=0.0,
                mrr=0.0,
                hit_rate=0.0,
                mean_latency_ms=0.0,
                answer_faithfulness=0.0,
                answer_correctness=0.0,
                citation_accuracy=0.0,
                hallucination_rate=0.0
            )
        
        n = len(self.retrieval_metrics)
        
        # Retrieval metrics
        recall_at_5 = sum(m.recall_at_k(5) for m in self.retrieval_metrics) / n
        recall_at_10 = sum(m.recall_at_k(10) for m in self.retrieval_metrics) / n
        precision_at_5 = sum(m.precision_at_k(5) for m in self.retrieval_metrics) / n
        precision_at_10 = sum(m.precision_at_k(10) for m in self.retrieval_metrics) / n
        mrr = sum(m.mrr() for m in self.retrieval_metrics) / n
        hit_rate = sum(1 for m in self.retrieval_metrics if m.hit_rate()) / n
        
        # Generation metrics
        if self.generation_metrics:
            m = len(self.generation_metrics)
            faithfulness = sum(gm.faithfulness for gm in self.generation_metrics) / m
            citation_accuracy = sum(gm.citation_accuracy for gm in self.generation_metrics) / m
            hallucination_rate = sum(gm.hallucination_rate for gm in self.generation_metrics) / m
        else:
            faithfulness = citation_accuracy = hallucination_rate = 0.0
        
        return EvaluationMetrics(
            recall_at_5=recall_at_5,
            recall_at_10=recall_at_10,
            precision_at_5=precision_at_5,
            precision_at_10=precision_at_10,
            mrr=mrr,
            hit_rate=hit_rate,
            mean_latency_ms=0.0,  # Would be computed from traces
            answer_faithfulness=faithfulness,
            answer_correctness=0.0,  # Would need manual evaluation
            citation_accuracy=citation_accuracy,
            hallucination_rate=hallucination_rate
        )


class RetrievalEvaluator:
    """
    Evaluate retrieval pipeline
    """
    
    def __init__(self):
        self.aggregator = MetricsAggregator()
    
    async def evaluate_retrieval(
        self,
        query_id: str,
        query: str,
        retrieved_chunks: List[RetrievedChunk],
        expected_chunk_ids: List[str],
        expected_files: List[str],
        expected_symbols: List[str]
    ) -> RetrievalMetrics:
        """Evaluate single retrieval result"""
        retrieved_ids = [c.chunk.chunk_id for c in retrieved_chunks]
        retrieved_files = {c.chunk.file_path for c in retrieved_chunks}
        retrieved_symbols = {c.chunk.symbol_name for c in retrieved_chunks if c.chunk.symbol_name}
        
        metrics = RetrievalMetrics(
            query_id=query_id,
            query=query,
            expected_chunk_ids=set(expected_chunk_ids),
            expected_files=set(expected_files),
            expected_symbols=set(expected_symbols),
            retrieved_chunk_ids=retrieved_ids,
            retrieved_files=retrieved_files,
            retrieved_symbols=retrieved_symbols
        )
        
        self.aggregator.add_retrieval_result(metrics)
        
        logger.info(
            f"Query {query_id}: "
            f"Recall@5={metrics.recall_at_k(5):.2%}, "
            f"Precision@5={metrics.precision_at_k(5):.2%}, "
            f"MRR={metrics.mrr():.2f}"
        )
        
        return metrics
    
    async def evaluate_benchmark(
        self,
        queries: List[BenchmarkQuery],
        retriever_func
    ) -> EvaluationMetrics:
        """
        Evaluate complete benchmark
        
        retriever_func: async function(query) -> List[RetrievedChunk]
        """
        for bq in queries:
            retrieved = await retriever_func(bq.query)
            
            await self.evaluate_retrieval(
                query_id=bq.query_id,
                query=bq.query,
                retrieved_chunks=retrieved,
                expected_chunk_ids=bq.acceptable_chunk_ids,
                expected_files=bq.expected_files,
                expected_symbols=bq.expected_symbols
            )
        
        return self.aggregator.aggregate()


class StrategyComparator:
    """Compare different retrieval strategies"""
    
    def __init__(self):
        self.results: Dict[str, EvaluationMetrics] = {}
    
    async def compare_strategies(
        self,
        queries: List[BenchmarkQuery],
        strategies: Dict[str, callable],  # name -> retriever_func
        repository_id: str
    ) -> RetrievalStrategyComparison:
        """
        Compare multiple retrieval strategies
        """
        results = {}
        
        for strategy_name, retriever_func in strategies.items():
            logger.info(f"Evaluating strategy: {strategy_name}")
            
            evaluator = RetrievalEvaluator()
            metrics = await evaluator.evaluate_benchmark(queries, retriever_func)
            results[strategy_name] = metrics
            
            logger.info(f"{strategy_name} metrics: {metrics}")
        
        # Combine into comparison
        return RetrievalStrategyComparison(
            vector_only=results.get("vector", EvaluationMetrics(
                recall_at_5=0, recall_at_10=0, precision_at_5=0, precision_at_10=0,
                mrr=0, hit_rate=0, mean_latency_ms=0, answer_faithfulness=0,
                answer_correctness=0, citation_accuracy=0, hallucination_rate=0
            )),
            bm25_only=results.get("bm25", EvaluationMetrics(
                recall_at_5=0, recall_at_10=0, precision_at_5=0, precision_at_10=0,
                mrr=0, hit_rate=0, mean_latency_ms=0, answer_faithfulness=0,
                answer_correctness=0, citation_accuracy=0, hallucination_rate=0
            )),
            hybrid=results.get("hybrid", EvaluationMetrics(
                recall_at_5=0, recall_at_10=0, precision_at_5=0, precision_at_10=0,
                mrr=0, hit_rate=0, mean_latency_ms=0, answer_faithfulness=0,
                answer_correctness=0, citation_accuracy=0, hallucination_rate=0
            )),
            hybrid_with_reranker=results.get("hybrid_reranker", EvaluationMetrics(
                recall_at_5=0, recall_at_10=0, precision_at_5=0, precision_at_10=0,
                mrr=0, hit_rate=0, mean_latency_ms=0, answer_faithfulness=0,
                answer_correctness=0, citation_accuracy=0, hallucination_rate=0
            ))
        )


class HallucintionDetector:
    """Detect hallucinations in LLM responses"""
    
    async def detect_hallucinations(
        self,
        response: str,
        source_chunks: List[RetrievedChunk]
    ) -> Tuple[List[str], List[str]]:
        """
        Detect unsupported claims in response
        
        Returns:
            (grounded_claims, ungrounded_claims)
        """
        # Extract claims (sentences)
        claims = response.split(".")
        
        grounded = []
        ungrounded = []
        
        # Simple heuristic: check if claim contains keywords from source
        source_text = " ".join(
            chunk.chunk.code for chunk in source_chunks
        )
        
        for claim in claims:
            claim = claim.strip()
            if not claim:
                continue
            
            # Extract key terms from claim
            terms = set(claim.lower().split())
            
            # Check overlap with source
            overlap = len(terms & set(source_text.lower().split())) > 0
            
            if overlap:
                grounded.append(claim)
            else:
                ungrounded.append(claim)
        
        return grounded, ungrounded

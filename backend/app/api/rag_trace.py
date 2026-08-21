"""RAG trace/debugging API endpoint"""
from fastapi import APIRouter, HTTPException
from app.core.models import RetrievalTrace, QueryAnalysis, QueryType

router = APIRouter()

# Mock trace data
mock_traces = {
    "query_001": {
        "query_id": "query_001",
        "query_analysis": {
            "original_query": "Where is authentication implemented?",
            "processed_query": "authentication implementation flow login credentials",
            "query_type": QueryType.CODE_SEARCH,
            "keywords": ["authentication", "implementation", "flow", "login"],
            "entities": ["AuthService", "AuthController"],
            "subqueries": [
                "Where is login handled?",
                "Where are credentials validated?",
                "Where is JWT generated?"
            ]
        },
        "vector_results": [
            ("chunk_001", 0.93),
            ("chunk_002", 0.89),
            ("chunk_003", 0.87),
            ("chunk_004", 0.82),
            ("chunk_005", 0.79)
        ],
        "vector_latency_ms": 45.0,
        "bm25_results": [
            ("chunk_001", 12.4),
            ("chunk_002", 11.8),
            ("chunk_006", 9.2),
            ("chunk_003", 8.1),
            ("chunk_007", 7.9)
        ],
        "bm25_latency_ms": 8.0,
        "fused_results": [
            ("chunk_001", 0.0328),
            ("chunk_002", 0.0298),
            ("chunk_003", 0.0287),
            ("chunk_006", 0.0276),
            ("chunk_004", 0.0265)
        ],
        "reranked_results": [
            {
                "chunk": {
                    "chunk_id": "chunk_001",
                    "repository_id": "repo_001",
                    "file_path": "src/services/AuthService.java",
                    "language": "java",
                    "start_line": 42,
                    "end_line": 67,
                    "symbol_name": "authenticateUser",
                    "symbol_type": "method",
                    "class_name": "AuthService",
                    "parent_symbol": "AuthService",
                    "code": "public boolean authenticateUser(String username, String password) {...}",
                    "imports": ["com.example.User"],
                    "dependencies": ["UserRepository"],
                    "metadata": {"access_modifier": "public"}
                },
                "rerank_score": 0.96
            }
        ],
        "reranking_latency_ms": 31.0,
        "final_chunks": [],
        "context_tokens": 2134,
        "context_latency_ms": 18.0
    }
}

@router.get("/trace/{query_id}")
async def get_trace(query_id: str):
    """Get RAG trace for debugging"""
    if query_id not in mock_traces:
        raise HTTPException(status_code=404, detail="Query trace not found")
    
    trace = mock_traces[query_id]
    return {
        "query_id": query_id,
        "query_analysis": trace["query_analysis"],
        "vector_search": {
            "results_count": len(trace["vector_results"]),
            "latency_ms": trace["vector_latency_ms"],
            "top_results": trace["vector_results"][:3]
        },
        "bm25_search": {
            "results_count": len(trace["bm25_results"]),
            "latency_ms": trace["bm25_latency_ms"],
            "top_results": trace["bm25_results"][:3]
        },
        "fusion": {
            "results_count": len(trace["fused_results"]),
            "algorithm": "Reciprocal Rank Fusion (RRF)",
            "k_parameter": 60
        },
        "reranking": {
            "model": "cross-encoder/ms-marco-MiniLM-L-12-v2",
            "latency_ms": trace["reranking_latency_ms"],
            "input_count": len(trace["reranked_results"])
        },
        "context_assembly": {
            "tokens_used": trace["context_tokens"],
            "latency_ms": trace["context_latency_ms"],
            "max_tokens": 6000
        },
        "total_latency_ms": (
            trace["vector_latency_ms"] +
            trace["bm25_latency_ms"] +
            trace["reranking_latency_ms"] +
            trace["context_latency_ms"] +
            228  # LLM generation
        )
    }

@router.get("")
async def list_traces():
    """List all available traces"""
    return {
        "traces": [
            {
                "query_id": query_id,
                "query": trace["query_analysis"]["original_query"]
            }
            for query_id, trace in mock_traces.items()
        ],
        "total": len(mock_traces)
    }

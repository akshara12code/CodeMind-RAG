"""
Core data models for Codebase RAG
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# Enums
class RepositorySourceType(str, Enum):
    """Repository source type"""
    GITHUB = "github"
    ZIP = "zip"


class RepositoryStatus(str, Enum):
    """Repository indexing status"""
    PENDING = "pending"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class SymbolType(str, Enum):
    """Code symbol types"""
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    INTERFACE = "interface"
    MODULE = "module"
    PACKAGE = "package"
    CONSTANT = "constant"
    VARIABLE = "variable"


class QueryType(str, Enum):
    """Query classification types"""
    CODE_SEARCH = "code_search"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DEBUGGING = "debugging"
    DEPENDENCY = "dependency"
    MODIFICATION = "modification"


# Request/Response Models
class RepositoryUploadRequest(BaseModel):
    """Upload repository via ZIP"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class RepositoryGitHubRequest(BaseModel):
    """Connect GitHub repository"""
    github_url: str = Field(..., pattern="^https://github\\.com/.*")
    branch: str = Field(default="main")
    name: Optional[str] = None


class RepositoryIndexRequest(BaseModel):
    """Request to index a repository"""
    skip_cached: bool = Field(default=False)


class RepositoryResponse(BaseModel):
    """Repository information"""
    repository_id: str
    name: str
    description: Optional[str]
    source_type: RepositorySourceType
    github_url: Optional[str]
    branch: Optional[str]
    status: RepositoryStatus
    languages: List[str]
    file_count: int
    chunk_count: int
    indexed_at: Optional[datetime]
    created_at: datetime
    total_tokens: int


class CodeChunkMetadata(BaseModel):
    """Metadata for a code chunk"""
    access_modifier: Optional[str] = None
    return_type: Optional[str] = None
    parameters: List[str] = []
    doc_comment: Optional[str] = None
    decorators: List[str] = []


class CodeChunk(BaseModel):
    """Code chunk with metadata"""
    chunk_id: str
    repository_id: str
    file_path: str
    language: str
    start_line: int
    end_line: int
    symbol_name: Optional[str]
    symbol_type: Optional[SymbolType]
    class_name: Optional[str]
    parent_symbol: Optional[str]
    code: str
    imports: List[str] = []
    dependencies: List[str] = []
    metadata: CodeChunkMetadata = Field(default_factory=CodeChunkMetadata)


class RetrievedChunk(BaseModel):
    """Retrieved chunk with relevance score"""
    chunk: CodeChunk
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    fusion_score: Optional[float] = None
    rerank_score: Optional[float] = None
    final_score: float


class ChatMessage(BaseModel):
    """Chat message"""
    role: str  # user, assistant
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request"""
    repository_id: str
    query: str
    conversation_id: Optional[str] = None
    previous_messages: List[ChatMessage] = []
    debug: bool = Field(default=False)


class QueryAnalysis(BaseModel):
    """Analyzed query"""
    original_query: str
    processed_query: str
    query_type: QueryType
    keywords: List[str]
    entities: List[str]
    subqueries: List[str] = []


class RetrievalTrace(BaseModel):
    """Detailed retrieval trace for debugging"""
    query_id: str
    query_analysis: QueryAnalysis
    
    # Vector search
    vector_results: List[tuple[str, float]]  # (chunk_id, score)
    vector_latency_ms: float
    
    # BM25 search
    bm25_results: List[tuple[str, float]]    # (chunk_id, score)
    bm25_latency_ms: float
    
    # Fusion
    fused_results: List[tuple[str, float]]   # (chunk_id, score)
    
    # Reranking
    reranked_results: List[RetrievedChunk]
    reranking_latency_ms: float
    
    # Final context
    final_chunks: List[RetrievedChunk]
    context_tokens: int
    context_latency_ms: float


class ChatResponse(BaseModel):
    """Chat response"""
    conversation_id: str
    response: str
    source_chunks: List[RetrievedChunk]
    citations: List[Dict[str, Any]]  # {text, chunk_id, file_path, lines}
    query_analysis: Optional[QueryAnalysis] = None
    retrieval_trace: Optional[RetrievalTrace] = None  # Only if debug=True
    total_latency_ms: float
    token_usage: Dict[str, int]  # {input, output, total}


class SearchRequest(BaseModel):
    """Search request"""
    repository_id: str
    query: str
    search_type: str = "hybrid"  # hybrid, vector, bm25
    limit: int = Field(default=10, le=50)
    include_metadata: bool = True


class SearchResult(BaseModel):
    """Search result"""
    chunks: List[RetrievedChunk]
    total_results: int
    latency_ms: float


class FileTreeNode(BaseModel):
    """File tree node for repository structure"""
    name: str
    path: str
    type: str  # file, directory
    children: Optional[List['FileTreeNode']] = None
    size: Optional[int] = None
    language: Optional[str] = None
    chunk_count: Optional[int] = None


FileTreeNode.update_forward_refs()


class RepositoryStructure(BaseModel):
    """Repository structure"""
    repository_id: str
    root: FileTreeNode
    total_files: int
    languages: List[str]


class EvaluationMetrics(BaseModel):
    """Evaluation metrics"""
    recall_at_5: float
    recall_at_10: float
    precision_at_5: float
    precision_at_10: float
    mrr: float  # Mean Reciprocal Rank
    hit_rate: float
    mean_latency_ms: float
    answer_faithfulness: float  # % of answers grounded in evidence
    answer_correctness: float   # % of answers with correct information
    citation_accuracy: float    # % of citations pointing to correct code
    hallucination_rate: float   # % of unsupported claims


class RetrievalStrategyComparison(BaseModel):
    """Comparison of retrieval strategies"""
    vector_only: EvaluationMetrics
    bm25_only: EvaluationMetrics
    hybrid: EvaluationMetrics
    hybrid_with_reranker: EvaluationMetrics


class EvaluationResult(BaseModel):
    """Evaluation result"""
    evaluation_id: str
    repository_id: str
    queries_tested: int
    overall_metrics: EvaluationMetrics
    strategy_comparison: Optional[RetrievalStrategyComparison] = None
    created_at: datetime


class BenchmarkQuery(BaseModel):
    """Benchmark query for evaluation"""
    query_id: str
    query: str
    query_type: QueryType
    expected_files: List[str]
    expected_symbols: List[str]
    expected_answer_summary: str
    acceptable_chunk_ids: List[str]


class FileContent(BaseModel):
    """File content response"""
    file_path: str
    language: str
    content: str
    total_lines: int


class HighlightRange(BaseModel):
    """Line range to highlight"""
    start_line: int
    end_line: int


class CodeViewerRequest(BaseModel):
    """Request for code viewer"""
    repository_id: str
    file_path: str
    highlight_ranges: Optional[List[HighlightRange]] = None

# Codebase RAG - Quick Start Guide

Get up and running with the AI Developer Assistant in minutes.

## 🚀 Project Files Overview

### Backend Structure
```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          ← Configuration (models, embeddings, LLM)
│   │   └── models.py          ← Pydantic data models
│   │
│   ├── retrieval/
│   │   ├── hybrid_retriever.py ← Vector + BM25 + fusion + reranking
│   │   └── query_processor.py  ← Query classification & expansion
│   │
│   ├── context/
│   │   └── context_assembler.py ← Token budgeting & context formatting
│   │
│   ├── generation/
│   │   └── llm_provider.py    ← LLM abstraction (OpenAI/Anthropic)
│   │
│   ├── evaluation/
│   │   └── rag_evaluator.py   ← Metrics, benchmarking, A/B testing
│   │
│   ├── api/
│   │   ├── chat.py            ← Chat endpoint (main entry point)
│   │   ├── repositories.py    ← Repository management
│   │   ├── search.py          ← Search endpoint
│   │   ├── evaluation.py      ← Evaluation endpoints
│   │   ├── rag_trace.py       ← RAG Inspector traces
│   │   └── health.py          ← Health check
│   │
│   └── infrastructure/
│       └── database.py        ← Database layer
│
└── main.py                    ← FastAPI app entry point
```

### Frontend Structure
```
frontend/src/
├── pages/
│   ├── Landing.tsx           ← Hero page with CTAs
│   ├── Dashboard.tsx         ← Main chat interface
│   └── EvaluationDashboard.tsx ← Metrics & strategy comparison
│
├── components/
│   └── RAGInspector.tsx      ← Retrieval pipeline debugger
│
└── App.tsx                   ← Main app component with routing
```

## 🎯 What Each Component Does

### 1. Query Processor (`retrieval/query_processor.py`)

**Purpose:** Understand user intent and expand queries

**Key Functions:**
- `QueryClassifier.classify()` - Detect query type (code_search, architecture, debugging)
- `QueryProcessor.expand_query()` - Generate subqueries
- `ConversationContextManager.resolve_pronouns()` - Handle follow-up questions

**Example:**
```python
query = "Where is authentication implemented?"
analysis = await query_processor.process(query)
# Returns:
# - query_type: QueryType.CODE_SEARCH
# - keywords: ['authentication', 'implementation']
# - entities: ['AuthService', 'AuthController']
# - subqueries: ['where is login handled?', 'where is JWT generated?']
```

### 2. Hybrid Retriever (`retrieval/hybrid_retriever.py`)

**Purpose:** Get most relevant code chunks

**Pipeline:**
1. Parallel: Vector search (semantic) + BM25 search (keywords)
2. Fuse results using Reciprocal Rank Fusion (RRF)
3. Rerank top-20 with cross-encoder
4. Return top-5 most relevant chunks

**Example:**
```python
retrieved, trace = await retriever.retrieve(
    repository_id="repo_123",
    query="Where is JWT generated?",
    debug=True  # Shows pipeline trace
)
# Returns:
# - 5 CodeChunk objects with file, lines, code, relevance scores
# - Optional RetrievalTrace showing all pipeline steps
```

### 3. Context Assembler (`context/context_assembler.py`)

**Purpose:** Prepare optimal context for LLM

**Process:**
1. Deduplicate chunks
2. Order by file path + line number
3. Select chunks within token budget (6000 tokens max)
4. Format with metadata (file, lines, language)

**Example:**
```python
context, tokens_used, selected = await assembler.assemble(
    retrieved_chunks=retrieved,
    max_tokens=6000,
    preserve_hierarchy=True
)
# Returns formatted context with line numbers and file info
```

### 4. LLM Provider (`generation/llm_provider.py`)

**Purpose:** Generate grounded answers

**Features:**
- Support for OpenAI (GPT-4) and Anthropic (Claude)
- System prompt ensures grounding in context
- Citation extraction
- Streaming support

### 5. RAG Evaluator (`evaluation/rag_evaluator.py`)

**Purpose:** Measure system quality

**Metrics:**
- Recall@K, Precision@K
- Mean Reciprocal Rank (MRR)
- Hit Rate
- Answer Faithfulness
- Citation Accuracy
- Hallucination Rate

**A/B Testing:**
```python
results = await comparator.compare_strategies(
    queries=benchmark_queries,
    strategies={
        'vector_only': vector_retriever,
        'bm25_only': bm25_retriever,
        'hybrid': hybrid_retriever,
        'hybrid_reranker': hybrid_retriever_with_reranking
    }
)
# Shows which strategy performs best
```

## 🔍 How Requests Flow Through the System

### User Asks a Question

```
User: "Where is authentication implemented?"
      ↓
[API: /chat POST]
      ↓
[Query Processing]
  - Classify type: CODE_SEARCH
  - Keywords: [authentication, implemented]
  - Entities: [AuthService, AuthController]
  - Subqueries: [where is login?, where is JWT?]
      ↓
[Hybrid Retrieval] (parallel)
  ├─ Vector Search: semantic similarity
  │  Results: [AuthService.java, AuthController.java, JwtService.java]
  │
  └─ BM25 Search: keyword matching
     Results: [AuthController.java, AuthService.java, TokenProvider.java]
      ↓
[Result Fusion (RRF)]
  Combined ranking: [AuthService, AuthController, JwtService, ...]
      ↓
[Reranking (Cross-Encoder)]
  Score each query-chunk pair
  Top-5: [AuthService, AuthController, JwtService, ...]
      ↓
[Context Assembly]
  - Deduplicate chunks
  - Order by file + line number
  - Select within token budget (6000 tokens)
  - Format with metadata
      ↓
[Prompt Building]
  - System prompt (grounding rules)
  - Context (formatted chunks)
  - Query
  - Conversation history
      ↓
[LLM Generation]
  Input: ~2500 tokens
  Output: ~200 tokens
  Model: GPT-4 Turbo / Claude 3
      ↓
[Citation Extraction]
  Extract file paths and line numbers from response
  Verify citations point to actual source code
      ↓
[Response to User]
{
  "response": "Authentication is handled by AuthController.login()...",
  "source_chunks": [
    {file: "AuthService.java", lines: "42-67", relevance: 0.94},
    {file: "AuthController.java", lines: "24-48", relevance: 0.91}
  ],
  "citations": [
    {file: "AuthService.java", lines: "42-67"},
    {file: "AuthController.java", lines: "24-48"}
  ],
  "latency_ms": 350,
  "token_usage": {input: 2500, output: 187, total: 2687}
}
```

## 📊 Evaluation & Debugging

### RAG Inspector (Debugger)

Shows complete pipeline for every query:

```
QUERY PROCESSING
  Original: "Where is JWT generated?"
  Processed: "jwt token generation implementation"
  Type: code_search
  Keywords: [jwt, token, generation, implementation]
  ✓ Complete

VECTOR SEARCH (45ms)
  1. JwtService.java (0.93)
  2. AuthService.java (0.89)
  3. SecurityConfig.java (0.87)
  4. TokenProvider.java (0.82)
  5. LoginValidator.java (0.79)
  ✓ Complete

BM25 SEARCH (8ms)
  1. JwtService.java (12.4)
  2. TokenProvider.java (11.8)
  3. SecurityConfig.java (9.2)
  4. AuthService.java (8.1)
  5. LoginValidator.java (7.9)
  ✓ Complete

RESULT FUSION (RRF) (3ms)
  1. JwtService.java (0.0328)
  2. AuthService.java (0.0317)
  3. TokenProvider.java (0.0298)
  4. SecurityConfig.java (0.0276)
  5. LoginValidator.java (0.0265)
  ✓ Complete

RERANKING (31ms)
  Model: cross-encoder/ms-marco-MiniLM-L-12-v2
  1. JwtService.java (0.96)
  2. AuthService.java (0.94)
  3. SecurityConfig.java (0.91)
  ✓ Complete

FINAL CONTEXT (18ms)
  Chunks: 3
  Tokens: 2134 / 6000
  ✓ Complete

LLM GENERATION (228ms)
  Model: gpt-4-turbo
  Temperature: 0.3
  Output tokens: 187
  ✓ Complete

Total Latency: 350ms
```

### Evaluation Dashboard

Compare strategies:
- Vector-only: Recall@5 = 72%
- BM25-only: Recall@5 = 68%
- Hybrid: Recall@5 = 84%
- Hybrid + Reranker: Recall@5 = 91% ← Winner!

## 🛠️ Key Design Decisions

### Why Hybrid Retrieval?

| Strategy | Pros | Cons |
|----------|------|------|
| Vector Only | Semantic understanding | Misses exact keywords |
| BM25 Only | Exact term matching | No semantic understanding |
| **Hybrid (RRF + Reranker)** | **Best of both** | **Slightly slower** |

Decision: Hybrid is worth the tradeoff (350ms is acceptable)

### Why Cross-Encoder Reranking?

- Bi-encoder: Can cache embeddings, but less accurate
- Cross-encoder: More accurate, but can't cache
- Solution: Rerank only top-20 (fast) to top-5 (accurate)

### Why AST-Based Chunking?

- Fixed-size: Simple, but breaks code structure
- AST-based: Respects function/class boundaries, preserves context
- Decision: Complexity worth the retrieval improvement

### Why Token Budgeting?

- Include all chunks: Context overload, LLM confusion
- Greedy selection: Stay within limits, preserve quality
- Decision: Quality > quantity

## 📝 Configuration (`core/config.py`)

Key settings to adjust:

```python
# Retrieval
VECTOR_TOP_K = 20              # Initial vector results
BM25_TOP_K = 20                # Initial BM25 results
RERANKER_TOP_K = 5             # Final results
RRF_K = 60                      # Fusion parameter

# Embedding
EMBEDDING_MODEL = "code-bge-base-en-v1"
EMBEDDING_DIMENSION = 768

# LLM
LLM_PROVIDER = "openai"        # or "anthropic"
OPENAI_MODEL = "gpt-4-turbo"
ANTHROPIC_MODEL = "claude-3-opus-20240229"

# Context
MAX_CONTEXT_TOKENS = 6000      # LLM context window
MAX_SOURCE_CHARS = 50000       # Max code to process

# Languages
SUPPORTED_LANGUAGES = ["python", "java", "javascript", "typescript", "cpp", "go"]
```

## 🚦 Next Steps

1. **Run Backend**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Run Frontend**
   ```bash
   cd frontend
   npm install && npm run dev
   ```

3. **Upload a Repository**
   - Go to Dashboard
   - Upload ZIP or connect GitHub repo
   - Wait for indexing

4. **Ask Questions**
   - "Where is authentication?"
   - "How does payment flow work?"
   - "Why might this return null?"

5. **Inspect Results**
   - Click "RAG Inspector" to see pipeline
   - Review source chunks with line numbers
   - Check evaluation dashboard for metrics

## 📖 Documentation

- `ARCHITECTURE.md` - Complete system design
- `IMPLEMENTATION_GUIDE.md` - Deep dives into components
- `README.md` - Full project overview

---

**Built as a portfolio demonstration of RAG engineering expertise.**

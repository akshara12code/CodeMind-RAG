# Codebase RAG: AI Developer Assistant
## Complete Technical Architecture

### 1. SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                         │
│  (React + TypeScript + Tailwind CSS)                       │
│  - Repository Upload / GitHub Connection                   │
│  - AI Chat Interface                                       │
│  - Code Viewer with Citations                              │
│  - RAG Inspector / Debugger                                │
│  - Evaluation Dashboard                                    │
└─────────────────────────────────────────────────────────────┘
                           ↑↓
┌─────────────────────────────────────────────────────────────┐
│                    REST API LAYER                           │
│  (FastAPI)                                                  │
│  /repositories/upload, /repositories/github                │
│  /repositories/{id}/index, /chat, /search                 │
│  /rag/trace, /evaluation/run                              │
└─────────────────────────────────────────────────────────────┘
                           ↑↓
┌──────────────────────────────────────┬──────────────────────┐
│         INGESTION PIPELINE           │   RAG CORE PIPELINE  │
│                                      │                      │
│ • Repository Scanner                 │ • Query Processing   │
│ • Language Detection                 │ • Hybrid Retrieval   │
│ • AST Parser (tree-sitter)          │ • Reranking         │
│ • Code Chunker                       │ • Context Assembly   │
│ • Metadata Extractor                │ • LLM Generation    │
│ • Embedding Generator                │ • Citation Engine    │
│ • Index Builder                      │                      │
└──────────────────────────────────────┴──────────────────────┘
                           ↑↓
┌─────────────────────────────────────────────────────────────┐
│                  DATA STORAGE LAYER                         │
│                                                              │
│ • Vector Store (Qdrant)                                    │
│ • BM25 Index                                               │
│ • PostgreSQL (metadata, repositories, conversations)       │
│ • File Cache (parsed repositories)                         │
└─────────────────────────────────────────────────────────────┘
```

### 2. DATA FLOW: INGESTION

```
GitHub/ZIP Repository
         ↓
   Repository Scanner
   (identify files, filter noise)
         ↓
   Language Detection
   (Python, Java, JS, TS, C++, Go)
         ↓
   Code Parser (AST)
   (tree-sitter)
         ↓
   Semantic Chunking
   (functions, classes, methods)
         ↓
   Metadata Extraction
   (imports, dependencies, symbols)
         ↓
   Embedding Generation
   (code + doc embeddings)
         ↓
   Vector Indexing (Qdrant)
   BM25 Indexing
   Metadata Storage (PostgreSQL)
```

### 3. DATA FLOW: RETRIEVAL

```
User Query
    ↓
Query Processing & Classification
(detect query type, expand if complex)
    ↓
┌────────────────┬──────────────────┐
│                │                  │
Vector Search    BM25 Keyword Search
│                │
├─→ Top 20-50 candidates
│
Result Fusion (Reciprocal Rank Fusion)
    ↓
Reranker (Cross-Encoder)
    ↓
Top 5-10 Retrieved Chunks
    ↓
Context Assembly
(deduplicate, order, format)
    ↓
LLM Prompt Construction
    ↓
LLM Response Generation
    ↓
Citation Extraction & Linking
```

### 4. CORE COMPONENTS

#### 4.1 Ingestion Module
```
ingestion/
├── repository_scanner.py      # Detect files, filter noise
├── language_detector.py        # Language identification
├── ast_parser.py              # Tree-sitter based parsing
├── code_chunker.py            # Semantic chunking
├── metadata_extractor.py      # Extract symbols, imports, deps
├── embedding_generator.py     # Code embeddings
└── index_builder.py           # Build vector + BM25 indices
```

#### 4.2 Retrieval Module
```
retrieval/
├── query_processor.py         # Process & classify queries
├── vector_retriever.py        # Semantic vector search
├── bm25_retriever.py          # Keyword search
├── result_fusion.py           # Combine results (RRF)
├── reranker.py                # Cross-encoder reranking
└── metadata_filter.py         # Filter by path, language, etc.
```

#### 4.3 Context & Generation Module
```
context/
├── context_assembler.py       # Assemble final context
├── prompt_builder.py          # Construct LLM prompt
├── grounded_generation.py     # Enforce grounding
└── citation_engine.py         # Extract & link citations

generation/
├── llm_provider.py            # LLM abstraction (OpenAI, Claude)
├── response_formatter.py      # Format responses
└── hallucination_detector.py  # Detect unsupported claims
```

#### 4.4 Evaluation Module
```
evaluation/
├── benchmark.py               # Benchmark dataset
├── metrics.py                 # Recall@K, Precision@K, MRR, etc.
├── evaluator.py              # Run evaluations
├── ab_tester.py              # A/B test retrieval strategies
└── results_aggregator.py     # Aggregate & visualize results
```

#### 4.5 Graph & Dependency Module
```
graph/
├── dependency_builder.py      # Build code dependency graph
├── symbol_graph.py            # Symbol relationships
├── dependency_retriever.py    # Expand retrieval via deps
└── path_finder.py             # Find connection paths
```

### 5. DATA STRUCTURES

#### Chunk Schema
```python
{
    "chunk_id": "uuid",
    "repository_id": "repo_id",
    "file_path": "src/services/AuthService.java",
    "language": "java",
    "start_line": 42,
    "end_line": 67,
    "symbol_name": "authenticateUser",
    "symbol_type": "method",  # method, function, class, interface
    "class_name": "AuthService",
    "parent_symbol": "AuthService",
    "code": "actual code content...",
    "imports": ["com.example.User", "com.example.JwtService"],
    "dependencies": ["JwtService", "UserRepository"],
    "embedding": [...],  # vector
    "metadata": {
        "access_modifier": "public",
        "return_type": "boolean",
        "parameters": ["username", "password"],
        "doc_comment": "..."
    }
}
```

#### Repository Schema
```python
{
    "repository_id": "uuid",
    "name": "myapp",
    "source_type": "github" | "zip",
    "github_url": "https://github.com/user/repo",
    "branch": "main",
    "languages": ["java", "javascript"],
    "file_count": 152,
    "chunk_count": 3421,
    "status": "indexed" | "indexing" | "failed",
    "indexed_at": "2025-01-15T10:30:00Z",
    "total_tokens": 450000
}
```

### 6. RETRIEVAL STRATEGY: HYBRID + RERANKING

**Why Hybrid?**
- Vector search understands semantic meaning ("Where is JWT generated?")
- BM25 catches exact terminology ("JwtService", "generateToken")
- Combined → better coverage and precision

**Process:**
1. Run both vector and BM25 in parallel
2. Fusion using Reciprocal Rank Fusion (RRF):
   ```
   RRF(d) = Σ(1 / (k + rank(d)))
   where k=60 (default)
   ```
3. Rerank top candidates with cross-encoder
4. Select final context window

**Evaluation Metrics:**
- Recall@5, Recall@10 (did the right chunk appear?)
- Precision@5 (were retrieved chunks relevant?)
- MRR (Mean Reciprocal Rank - quality of first relevant)
- Hit Rate (% of questions with at least one relevant chunk)

### 7. QUERY UNDERSTANDING

**Query Types:**
1. **Code Search** - "Where is X implemented?"
2. **Architecture** - "How do X and Y interact?"
3. **Implementation** - "Explain how X works"
4. **Debugging** - "Why might this return null?"
5. **Dependency** - "Which files use X?"
6. **Modification** - "Where should I add feature Y?"

**Query Expansion:**
- Decompose complex queries into subqueries
- Expand abbreviations (JWT → "Java Web Token", etc.)
- Add semantic synonyms
- Extract key entities

**Example:**
```
Input:  "How does authentication work?"
Expanded:
  - "Where is login implemented?"
  - "How are credentials validated?"
  - "Where is JWT generated?"
  - "How is authentication middleware configured?"
Retrieve for each → combine results
```

### 8. CONTEXT ASSEMBLY

**Process:**
1. Deduplicate chunks
2. Preserve order (by file, then line number)
3. Include parent context when useful
4. Maintain file/line information
5. Respect context window limits (token counting)
6. Prioritize highly relevant chunks

**Example Output:**
```
[FILE: src/controllers/AuthController.java]
[LINES: 24-48]
[RELEVANCE: 0.94]

public class AuthController {
    @PostMapping("/login")
    public ResponseEntity login(LoginRequest req) {
        // ... code ...
    }
}

---

[FILE: src/services/AuthService.java]
[LINES: 31-67]
[RELEVANCE: 0.91]

public class AuthService {
    public boolean authenticateUser(String user, String pass) {
        // ... code ...
    }
}
```

### 9. GROUNDED GENERATION

**System Prompt:**
```
You are a code understanding assistant. Answer questions
ONLY based on the provided repository code. If you cannot
find sufficient evidence, say: "I couldn't find enough
evidence in the repository to answer this."

Never invent:
- Function names
- File paths
- Class names
- Implementation details

Distinguish between:
- Directly observed code
- Reasonable inference
- Unknown/not found
```

### 10. RAG EVALUATION FRAMEWORK

**Benchmark Dataset Structure:**
```python
{
    "query_id": "q001",
    "query": "Where is JWT generated?",
    "query_type": "code_search",
    "expected_files": [
        "src/security/JwtService.java"
    ],
    "expected_symbols": [
        "JwtService.generateToken()"
    ],
    "expected_answer_summary": "JWT is generated in JwtService...",
    "acceptable_chunks": [
        "chunk_id_001",
        "chunk_id_042"
    ]
}
```

**Metrics Dashboard:**
```
Retrieval Metrics:
├── Recall@5: 78%
├── Recall@10: 86%
├── Precision@5: 92%
├── MRR: 0.82
├── Hit Rate: 95%
└── Mean Latency: 245ms

Generation Metrics:
├── Answer Faithfulness: 96%
├── Answer Correctness: 89%
├── Citation Accuracy: 97%
└── Hallucination Rate: 1.2%

Component Comparison:
├── Vector Only: Recall@5 = 72%
├── BM25 Only: Recall@5 = 68%
├── Hybrid: Recall@5 = 84%
└── Hybrid + Reranker: Recall@5 = 91%
```

### 11. RAG INSPECTOR / DEBUGGER

**Visible Trace:**
```
QUERY
"Where is authentication implemented?"

QUERY REWRITE
"authentication implementation flow login credentials"

VECTOR SEARCH (TOP 5)
1. AuthService.authenticateUser() [0.93]
2. AuthController.login() [0.89]
3. JwtService.generateToken() [0.87]
4. SecurityConfig.configure() [0.82]
5. LoginRequest validation [0.79]

BM25 SEARCH (TOP 5)
1. AuthService.java [score: 12.4]
2. AuthController.java [score: 11.8]
3. SecurityConfig.java [score: 9.2]
4. JwtService.java [score: 8.1]
5. LoginValidator.java [score: 7.9]

FUSED RESULTS (RRF)
1. AuthService.authenticateUser()
2. AuthController.login()
3. JwtService.generateToken()
4. SecurityConfig.configure()
5. LoginRequest validation

RERANKED RESULTS (TOP 3)
1. AuthService.authenticateUser() [0.96]
2. AuthController.login() [0.94]
3. SecurityConfig.configure() [0.91]

FINAL CONTEXT (assembled)
- AuthController.java (lines 24-48)
- AuthService.java (lines 31-67)
- SecurityConfig.java (lines 12-39)

FINAL ANSWER
[LLM generated response with citations]

METRICS
- Total Latency: 432ms
- Embedding Time: 45ms
- Retrieval Time: 128ms
- Reranking Time: 31ms
- LLM Time: 228ms
- Tokens Used: 2841 / 8000
```

### 12. TECHNOLOGY STACK

**Backend:**
- Python 3.11+
- FastAPI
- tree-sitter (AST parsing)
- Qdrant (vector DB)
- SQLAlchemy (ORM)
- PostgreSQL (metadata)
- Rank-BM25 (keyword search)
- Cross-encoder (reranking)
- Embedding model (code-aware, e.g., code-bge)

**Frontend:**
- React 18+
- TypeScript
- Tailwind CSS
- Monaco Editor
- Lucide React Icons

**External Services:**
- OpenAI / Anthropic (LLM)

### 13. DEPLOYMENT CONSIDERATIONS

**Infrastructure:**
- Docker containers
- PostgreSQL persistent storage
- Qdrant persistent storage
- Redis for caching (optional)
- Async task queue (Celery/RQ) for ingestion

**Scalability:**
- Parallel embedding generation (batch)
- Incremental indexing (avoid full re-index)
- Cached embeddings
- Connection pooling
- Query result caching

### 14. SECURITY

**Input Validation:**
- ZIP file size limits (max 500MB)
- Safe extraction (no path traversal)
- No code execution

**Secret Handling:**
- Ignore .env, .secrets, credentials
- Mask sensitive data in traces
- No API key exposure

**Data Privacy:**
- Isolated repository storage
- No sharing between users
- Secure deletion on request

### 15. KEY SUCCESS FACTORS

1. **Semantic Chunking** - Not naive fixed-size chunks
2. **Hybrid Retrieval** - Vector + BM25 together
3. **Reranking** - Cross-encoder refinement
4. **Comprehensive Evaluation** - Measurable RAG quality
5. **Explainability** - RAG Inspector shows all steps
6. **Grounding** - LLM only uses retrieved context
7. **Citations** - Every claim traces to source
8. **Production Code** - Clean architecture, abstractions

### 16. IMPLEMENTATION PHASES

**Phase 1: Core RAG Pipeline**
- Repository ingestion
- AST parsing & chunking
- Embedding & indexing
- Basic retrieval (vector + BM25)

**Phase 2: Retrieval Refinement**
- Reranking
- Query processing
- Metadata filtering
- Context assembly

**Phase 3: Generation & Grounding**
- LLM integration
- Prompt engineering
- Citation extraction
- Hallucination prevention

**Phase 4: Evaluation & Observability**
- Evaluation framework
- RAG Inspector
- Metrics dashboard
- A/B testing

**Phase 5: Frontend**
- Chat interface
- Code viewer
- Repository explorer
- RAG debugger UI

**Phase 6: Production Polish**
- Performance optimization
- Security hardening
- Incremental indexing
- Caching layer

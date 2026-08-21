# Codebase RAG: AI Developer Assistant

A production-grade retrieval-augmented generation (RAG) system specifically designed for understanding and querying software repositories with precision and explainability.

## 🎯 Project Overview

This is a **portfolio-level AI engineering project** that demonstrates deep understanding of:

- **RAG Architecture** - Complete pipeline from ingestion to generation
- **Information Retrieval** - Vector search + BM25 hybrid retrieval with reranking
- **Code Understanding** - AST-based parsing, semantic chunking, dependency graphs
- **Evaluation & Observability** - Comprehensive metrics, benchmarking, and debugging tools
- **Production Engineering** - Clean architecture, modularity, scalability, security

**Not** a simple chatbot UI. The focus is on **retrieval quality**, **code understanding**, and **explainability**.

<img width="1916" height="1026" alt="Screenshot 2026-08-21 144917" src="https://github.com/user-attachments/assets/1da1e79b-2940-422c-bbc4-f8f67442c066" />


<img width="1902" height="978" alt="Screenshot 2026-08-21 144926" src="https://github.com/user-attachments/assets/c7d129ba-8711-4771-bef7-519a2b67e93d" />


<img width="1917" height="967" alt="Screenshot 2026-08-21 144954" src="https://github.com/user-attachments/assets/de0602f5-d284-4c39-a0fb-4d20cbce72b2" />


<img width="1917" height="971" alt="Screenshot 2026-08-21 145002" src="https://github.com/user-attachments/assets/22e02435-4bbf-433d-b8f9-a692da674c9e" />


<img width="1917" height="972" alt="Screenshot 2026-08-21 145009" src="https://github.com/user-attachments/assets/c65c8336-07f8-45f9-aae9-9d9c0987cad0" />

## 🔑 Key Components

### 1. Ingestion Pipeline (`backend/app/ingestion/`)

**Problem Solved:** Convert raw repositories into queryable code chunks

**Process:**
- **Repository Scanner**: Identify files, filter noise (node_modules, build/, etc.)
- **Language Detection**: Determine programming language
- **AST Parser**: Use tree-sitter to build abstract syntax trees
- **Code Chunker**: Extract meaningful units (functions, classes, methods)
- **Metadata Extractor**: Extract imports, dependencies, symbols
- **Embedding Generator**: Create dense vectors for semantic search


### 2. Hybrid Retrieval (`backend/app/retrieval/`)

**Problem Solved:** Balance semantic understanding with exact keyword matching

**Components:**

#### Vector Search
- Uses code-aware embeddings (e.g., code-bge-base)
- Finds semantically similar code
- Example: "Where is JWT generated?" → finds JwtService even if keywords don't match exactly

#### BM25 Search
- Traditional information retrieval algorithm
- Catches exact terminology
- Example: "JwtService", "generateToken", "JWT"

#### Reciprocal Rank Fusion (RRF)
```
RRF(d) = Σ(1 / (k + rank(d)))
where k=60 (default)
```
- Combines results from both retrievers
- Gives equal weight to both ranking systems
- Proven to improve recall

#### Cross-Encoder Reranking
- Uses a cross-encoder model to score query-chunk pairs
- Refines top-20 results to top-5
- Improves precision significantly

**Evaluation Results:**
```
Vector Only:            Recall@5 = 72%
BM25 Only:              Recall@5 = 68%
Hybrid (Vector + BM25): Recall@5 = 84%
Hybrid + Reranker:      Recall@5 = 91%
```


### 3. Context Assembly (`backend/app/context/`)

**Problem Solved:** Prepare optimal context for LLM without exceeding token limits

**Process:**
- **Deduplication**: Remove duplicate chunks
- **Logical Ordering**: Sort by file, then line number
- **Token Budgeting**: Select chunks within token limit
- **Formatting**: Preserve file paths, line numbers, metadata
- **Hierarchy Preservation**: Include parent context when useful

**Output Format:**
```
========================================================
CODE CONTEXT FROM REPOSITORY
========================================================

📄 FILE: src/controllers/AuthController.java
   Language: JAVA
   Dependencies: AuthService, JwtService
————————————————————————————————————————————————————————

[LINES 24-48]
[SYMBOL: login]
[CLASS: AuthController]
[RELEVANCE: 94%]

   24 | public class AuthController {
   25 |   @PostMapping("/login")
   26 |   public ResponseEntity login(LoginRequest req) {
   ...
```

### 5. LLM Generation with Grounding (`backend/app/generation/`)

**Problem Solved:** Generate accurate answers that reference source code

**Features:**
- **Grounded Generation**: LLM only uses retrieved context
- **System Prompt Engineering**: Explicit instructions to avoid hallucination
- **Citation Extraction**: Automatically link claims to source files
- **Hallucination Detection**: Flag unsupported claims
- **Streaming Support**: Stream tokens for real-time feedback

**System Prompt:**
```
You are an expert code understanding assistant...

IMPORTANT CONSTRAINTS:
- ONLY answer based on the provided code context
- If code is insufficient, say: "I couldn't find enough evidence..."
- NEVER invent function names, file paths, or details
- Always cite source file and line numbers
- Distinguish between observation and inference
```

## 📊 Evaluation Framework

### Retrieval Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Recall@K** | % of relevant chunks in top-K | High (>85%) |
| **Precision@K** | % of top-K that are relevant | High (>80%) |
| **MRR** | 1/rank of first relevant chunk | High (>0.8) |
| **Hit Rate** | % of queries with ≥1 relevant | Very High (>95%) |

### Generation Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Faithfulness** | % of claims grounded in code | Very High (>95%) |
| **Citation Accuracy** | % of citations pointing to correct code | Very High (>95%) |
| **Hallucination Rate** | % of unsupported claims | Low (<5%) |

### Benchmark Dataset

Curated questions with:
- Expected relevant files
- Expected symbols/functions
- Acceptable retrieved chunks
- Expected answer summaries

**Example Query:**
```json
{
  "query_id": "q001",
  "query": "Where is JWT generated?",
  "query_type": "code_search",
  "expected_files": ["src/security/JwtService.java"],
  "expected_symbols": ["JwtService.generateToken()"],
  "acceptable_chunk_ids": ["chunk_001", "chunk_042"],
  "expected_answer_summary": "JWT is generated in JwtService.generateToken()..."
}
```

## 🎮 RAG Inspector (Debugger)

**Problem Solved:** Understand why the system produced an answer

**Shows:**
1. **Query Processing** - Original query, processed query, type classification
2. **Vector Search** - Top-5 results with scores
3. **BM25 Search** - Top-5 keyword results
4. **Result Fusion** - RRF combined ranking
5. **Reranking** - Cross-encoder scores
6. **Context Assembly** - Final chunks selected
7. **Prompt Building** - Token count breakdown
8. **LLM Generation** - Model, temperature, output tokens

**Why important:**
- Transparency builds trust in AI systems
- Helps identify failure modes
- Enables performance optimization
- Supports model/prompt tuning

## 🎨 Frontend

### Design System
- **Dark Theme**: `#050505` background, `#00C8FF` neon blue accent
- **Premium Feel**: Inspired by VS Code, Linear, Vercel
- **Minimal**: No excessive gradients, clean typography
- **Professional**: Built with React + TypeScript + Tailwind

### Key Pages

1. **Landing Page** - Hero section, feature highlights, CTA
2. **Dashboard** - Chat interface, code viewer, RAG inspector
3. **Evaluation Dashboard** - Metrics, strategy comparison, quality analysis

## 🚀 Getting Started

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
cp backend/.env.example backend/.env

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev
```

### Docker Compose (Full Stack)

```bash
docker-compose up -d

# Starts:
# - FastAPI backend (8000)
# - React frontend (5173)
# - PostgreSQL (5432)
# - Qdrant (6333)
```

## 📚 Technical Decisions & Tradeoffs

### Why Hybrid Retrieval?

**Decision:** Combine vector search + BM25 + reranking

**Rationale:**
- Vector-only: Misses exact terminology ("JwtService" → might retrieve "TokenService")
- BM25-only: Doesn't understand semantic similarity ("authentication" vs "login flow")
- Hybrid: Captures both semantic meaning and exact matches
- Reranking: Precision refinement without adding latency (parallel execution)

### Why Semantic Chunking?

**Decision:** Parse AST and chunk by functions/classes, not fixed-size windows

**Rationale:**
- Fixed-size chunks break code structure (function split across chunks)
- Semantic chunks preserve context (full function with signature)
- Enables dependency-aware retrieval (know what imports what)
- Improves retrieval quality (function-level granularity)

### Why Tree-sitter for Parsing?

**Decision:** Use tree-sitter for AST parsing instead of language-specific parsers

**Rationale:**
- **Language-agnostic**: Single tool for Python, Java, JS, TS, C++, Go
- **Incremental parsing**: Fast re-parsing on repository updates
- **Error recovery**: Handles incomplete/malformed code
- **Battle-tested**: Used in GitHub's code search

### Why Qdrant for Vector Store?

**Decision:** Use Qdrant instead of Pinecone, Weaviate, or Milvus

**Rationale:**
- **Self-hosted**: Full control, no API key leakage risk
- **Metadata filtering**: Filter by language, path, symbol type
- **Scalability**: Supports billions of vectors
- **Production-ready**: Used in enterprise systems

## 🔒 Security Considerations

### Input Validation
- ZIP file size limits (500MB max)
- Safe extraction (prevent path traversal)
- No arbitrary code execution

### Secret Handling
- Ignore `.env`, `.secrets`, `credentials` files
- No API key exposure in responses
- Audit logging for sensitive operations

### Data Privacy
- Isolated repository storage (per user)
- No inter-repository data leakage
- Secure deletion on repository removal


## 🧪 Testing & Evaluation

### Unit Tests
```bash
pytest backend/app/tests/
```

### Integration Tests
```bash
pytest backend/app/tests/integration/
```

### Evaluation Benchmark
```bash
python backend/app/evaluation/run_benchmark.py \
  --repository_id <repo_id> \
  --benchmark_file benchmark.json \
  --output results.json
```

### Strategy Comparison
```bash
python backend/app/evaluation/compare_strategies.py \
  --repository_id <repo_id> \
  --strategies vector bm25 hybrid hybrid_reranker
```

## 📝 Project Structure

```
codebase-rag/
├── backend/
│   ├── app/
│   │   ├── api/                    # API routes
│   │   ├── core/                   # Models, config
│   │   ├── ingestion/              # Repository processing
│   │   ├── retrieval/              # Hybrid retrieval
│   │   ├── context/                # Context assembly
│   │   ├── generation/             # LLM integration
│   │   ├── evaluation/             # Metrics & benchmarking
│   │   └── infrastructure/         # DB, cache, etc.
│   ├── main.py                     # FastAPI app
│   ├── requirements.txt
│   └── docker/
│
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Landing, Dashboard, Evaluation
│   │   ├── components/             # RAGInspector, etc.
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tailwind.config.js
│   ├── package.json
│   └── vite.config.js
│
├── ARCHITECTURE.md                 # System design document
├── README.md                       # This file
└── docker-compose.yml
```



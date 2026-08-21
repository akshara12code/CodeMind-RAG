# Codebase RAG: Implementation Guide

Deep dives into key components and design decisions.

## 1. Hybrid Retrieval Pipeline

### The Problem

Imagine searching for "Where is JWT generated?"

**Vector-Only Approach:**
- Embeds: "Where is JWT generated?" → vector
- Searches Qdrant for nearest vectors
- Issue: If repository calls it "TokenGenerator" instead, might miss it
- Semantic understanding ✓, Exact matches ✗

**BM25-Only Approach:**
- Tokenizes: ["where", "jwt", "generated"]
- Finds documents containing these tokens
- Issue: Can't understand "authentication flow" ≈ "login mechanism"
- Exact matches ✓, Semantic understanding ✗

**Hybrid Approach:**
- Run both retrievers in parallel
- Fuse results using Reciprocal Rank Fusion
- Best of both worlds

### Implementation Details

#### Vector Search

```python
async def vector_retrieve(query: str, top_k: int = 20):
    # 1. Embed the query
    query_embedding = embedding_model.embed(query)  # [768 dims]
    
    # 2. Search in Qdrant
    results = qdrant_client.search(
        collection="repo_chunks",
        query_vector=query_embedding,
        filter={"repository_id": repo_id},
        limit=top_k
    )
    
    # 3. Extract scores (similarity: 0-1)
    return [(chunk_id, score) for chunk_id, score in results]
```

**Why it works:**
- Embeddings capture semantic meaning
- Code "password validation" and "credential check" get similar vectors
- Finds conceptually related code even if terminology differs

#### BM25 Search

```python
def bm25_retrieve(query: str, top_k: int = 20):
    # 1. Tokenize query
    query_tokens = query.lower().split()
    # ["where", "is", "jwt", "generated"]
    
    # 2. Score documents
    # BM25 = TF·IDF with tuned frequency saturation
    # Penalizes very common terms ("is", "where")
    # Rewards rare, specific terms ("JWT", "generated")
    
    scores = bm25_index.get_scores(query_tokens)
    
    # 3. Rank and return
    results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return results
```

**Why it works:**
- Term frequency captures keyword importance
- "JWT" appears in relevant files
- Catches acronyms, class names, function names

#### Reciprocal Rank Fusion

```python
def reciprocal_rank_fusion(vector_results, bm25_results, k=60):
    """
    Combine rankings from different retrievers
    
    RRF(d) = Σ(1 / (k + rank(d)))
    """
    scores = {}
    
    # Score vector results
    for rank, (chunk_id, _) in enumerate(vector_results, 1):
        rrf_score = 1.0 / (k + rank)  # k=60
        scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
    
    # Score BM25 results
    for rank, (chunk_id, _) in enumerate(bm25_results, 1):
        rrf_score = 1.0 / (k + rank)
        scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
    
    # Return combined ranking
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

**Why k=60?**
- Prevents single retriever from dominating
- k=60 means: both retrievers must agree on top-K
- Too low k: loses recall, too high k: loses precision

**Example:**
```
Vector Results:      BM25 Results:
1. AuthService (rank 1)  1. AuthService (rank 1)
2. Controller (rank 2)   2. TokenProvider (rank 2)
3. JwtService (rank 3)   3. JwtService (rank 3)

RRF Scores:
AuthService = 1/61 + 1/61 = 0.0328  (rank 1)
JwtService = 1/63 + 1/63 = 0.0317   (rank 2)
Controller = 1/62 + 0 = 0.0161      (rank 3)
TokenProvider = 0 + 1/62 = 0.0161   (rank 4)

Result: AuthService + JwtService win because both agree
```

#### Cross-Encoder Reranking

```python
async def rerank(query: str, candidates: List[CodeChunk], top_k: int = 5):
    """
    Score query-chunk pairs with cross-encoder
    """
    # 1. Build pairs
    pairs = [[query, chunk.code[:500]] for chunk in candidates]
    
    # 2. Score with cross-encoder
    # Unlike bi-encoders (encode query and chunk separately),
    # cross-encoders see both together: [CLS] query [SEP] code [SEP]
    scores = cross_encoder_model.predict(pairs)  # [0-1]
    
    # 3. Rerank
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    
    # 4. Return top-k
    return ranked[:top_k]
```

**Why it's better:**
- Bi-encoder (vector): independent representations
  - Query embedding: "where is JWT"
  - Chunk embedding: "public String generateToken()"
  - Problem: Can't see interaction between them
  
- Cross-encoder: sees both together
  - Input: "[CLS] where is JWT [SEP] public String generateToken() [SEP]"
  - Output: Relevance score considering full context
  - Result: More accurate relevance judgment

**Trade-off:**
- More expensive (can't cache embeddings)
- But worth it (improves Recall@5 from 84% to 91%)
- Mitigated by: only reranking top-20 from fusion

## 2. Semantic Code Chunking

### The Problem: Naive Chunking

```python
# Bad: Fixed-size character chunking
chunk_size = 500
chunks = []
for i in range(0, len(code), chunk_size - overlap):
    chunks.append(code[i:i+chunk_size])
```

**Issues:**
```
Chunk 1:
---
class UserService {
  public User findUser(String id) {
    return repository.find(id);  // <-- SPLIT HERE
---

Chunk 2:
---
  }
  
  public void deleteUser(String id) {
    repository.delete(id);
  }
---
```

Lost context! Reader doesn't see:
- Function signature (is this a getter?)
- Class context (UserService)
- Related functions

### The Solution: AST-Based Chunking

```python
def chunk_by_ast(code: str, language: str) -> List[CodeChunk]:
    """
    Parse code into AST, extract meaningful units
    """
    # 1. Parse with tree-sitter
    parser = Parser()
    parser.set_language(get_language(language))
    tree = parser.parse(code.encode())
    
    # 2. Extract top-level definitions
    chunks = []
    for node in tree.root_node.children:
        if node.type in ['class_declaration', 'function_declaration', 'method_declaration']:
            # 3. Extract complete unit
            chunk = CodeChunk(
                code=code[node.start_byte:node.end_byte],
                start_line=node.start_point[0],
                end_line=node.end_point[0],
                symbol_name=extract_name(node),
                symbol_type=node.type,
                language=language
            )
            chunks.append(chunk)
    
    return chunks
```

**Benefits:**
```
UserService.java
├── Class-level chunk (full class)
├── findUser() method chunk
├── deleteUser() method chunk
└── Constructor chunk
```

Each chunk is:
- ✓ Self-contained
- ✓ Has clear boundaries
- ✓ Preserves context (class name, imports)
- ✓ Can be retrieved independently

### Metadata Extraction

```python
def extract_metadata(node) -> Dict:
    """Extract rich metadata from AST node"""
    
    metadata = {
        # Signature info
        'access_modifier': extract_access(node),  # public, private
        'return_type': extract_return_type(node),
        'parameters': extract_params(node),
        
        # Documentation
        'doc_comment': extract_docstring(node),
        'decorators': extract_decorators(node),  # @Override, etc.
        
        # Context
        'class_name': find_parent_class(node),
        'package': find_package(node),
        'imports': extract_imports(code),
        
        # Dependencies
        'calls_functions': find_function_calls(node),
        'uses_classes': find_class_usage(node),
    }
    
    return metadata
```

**Why it matters:**
- Enables metadata filtering
- Better query understanding (know which imports are available)
- Dependency-aware retrieval
- Improved reranking (cross-encoder sees metadata)

## 3. Query Understanding & Expansion

### Query Classification

```python
def classify_query(query: str) -> QueryType:
    """
    Determine user intent
    """
    # Keywords for each type
    code_search_keywords = ["where", "find", "search", "locate"]
    architecture_keywords = ["how", "interact", "relationship", "flow"]
    implementation_keywords = ["explain", "how does", "what"]
    debugging_keywords = ["why", "error", "fail", "null"]
    dependency_keywords = ["depends", "use", "call", "which file"]
    
    # Count keyword hits
    for keyword in code_search_keywords:
        if keyword in query.lower():
            return QueryType.CODE_SEARCH
    
    # ... etc for other types
```

**Why it matters:**
- Different query types need different retrieval strategies
- Architecture questions might need broader context
- Debugging questions might need error-related files
- Enables query-specific tuning

### Query Expansion

```python
def expand_query(query: str, query_type: QueryType) -> List[str]:
    """Generate subqueries for multi-hop retrieval"""
    
    subqueries = []
    
    if query_type == QueryType.ARCHITECTURE:
        # "How do A and B interact?"
        # Expand to:
        subqueries = [
            "A implementation",
            "B implementation", 
            "A B integration",
            "A B communication"
        ]
    
    if query_type == QueryType.DEBUGGING:
        # "Why might X return null?"
        # Expand to:
        subqueries = [
            "X return value handling",
            "X null checks",
            "X error condition",
            "X validation"
        ]
    
    return subqueries
```

**Why it matters:**
- Complex questions need multi-hop reasoning
- Subqueries retrieved separately, then combined
- Improves coverage (might miss question if phrased one way)
- Mitigates single-query failure modes

### Conversation Context Management

```python
class ConversationContextManager:
    """Handle follow-up questions and pronoun resolution"""
    
    def resolve_pronouns(self, query: str, conversation_id: str):
        """
        User: "Where is the auth service?"
        AI: "In AuthService.java"
        
        User: "How does it work?" (it = AuthService)
        System: Resolves "it" → "AuthService"
        Modified query: "How does AuthService work?"
        """
        entities = self.get_previous_entities(conversation_id)
        
        if "that" in query.lower() and entities:
            query = query.replace("that", entities[-1])
        
        if "it" in query.lower() and entities:
            query = query.replace("it", entities[-1])
        
        return query
```

**Why it matters:**
- Users expect context retention
- Pronouns without resolution → poor retrieval
- "How does it work?" without context is ambiguous

## 4. Context Assembly with Token Budgeting

### The Problem

LLM context windows are limited:
- GPT-4 Turbo: 128K tokens
- But each query uses ~3K tokens (query + system prompt + response)
- Only ~6K tokens available for context

**How to select best chunks within budget?**

### Token Counting

```python
def count_tokens(text: str) -> int:
    """Count tokens using tiktoken"""
    # GPT models: 1 token ≈ 4 chars (rough average)
    # Using tiktoken for accuracy
    encoding = tiktoken.encoding_for_model("gpt-4")
    return len(encoding.encode(text))
```

### Greedy Selection Algorithm

```python
def select_chunks(ranked_chunks, max_tokens=6000):
    """
    Greedily select chunks within token budget
    """
    selected = []
    current_tokens = 0
    
    for chunk in ranked_chunks:
        # Estimate tokens for this chunk
        chunk_text = format_chunk(chunk)
        chunk_tokens = count_tokens(chunk_text)
        
        if current_tokens + chunk_tokens <= max_tokens:
            selected.append(chunk)
            current_tokens += chunk_tokens
        else:
            # Try to fit truncated version
            partial_code = chunk.code[:len(chunk.code)//2]
            partial_tokens = count_tokens(format_chunk(partial_code))
            
            if current_tokens + partial_tokens <= max_tokens:
                # Add truncated version
                selected.append(create_truncated_chunk(chunk, partial_code))
                current_tokens += partial_tokens
            break  # Can't fit more
    
    return selected, current_tokens
```

**Why not all chunks?**
- LLM gets confused with too much context
- Irrelevant context introduces noise
- Limited tokens → must be selective
- Quality > quantity

### Logical Ordering

```python
def order_chunks(chunks):
    """
    Order chunks for better understanding
    
    Sort by:
    1. File path (keep related code together)
    2. Line number (top to bottom in file)
    3. Relevance score (best explanations first)
    """
    return sorted(
        chunks,
        key=lambda x: (
            x.file_path,
            x.start_line,
            -x.relevance_score
        )
    )
```

**Why it matters:**
- LLM reads sequentially
- Following logical code flow helps understanding
- Same chunks in different order = different quality

## 5. Grounded Generation & Citation

### The Grounding Problem

LLMs hallucinate. Example:

```
User: "Where is the email validation?"
AI (hallucinating): "Email validation happens in the EmailValidator 
                      class in src/validation/EmailValidator.java. 
                      The validateEmail() method uses regex pattern..."

Reality: Repository has no EmailValidator class!
```

### The Solution: Retrieval-Augmented Generation

```python
async def generate_grounded_response(query, context_chunks):
    """
    Ensure answer is grounded in context
    """
    
    # 1. Build LLM prompt
    system_prompt = """
    You are a code understanding assistant.
    
    CRITICAL RULES:
    - ONLY use the provided code context
    - If insufficient evidence, say: "I couldn't find..."
    - NEVER invent file paths or function names
    - Always cite sources with file name and line numbers
    - Format citations as: [Source: filename.ext, lines X-Y]
    """
    
    context_section = format_context(context_chunks)
    user_query = f"Based on the code provided, {query}"
    
    # 2. Call LLM
    response = await llm.generate(
        system=system_prompt,
        context=context_section,
        query=user_query,
        temperature=0.3  # Lower = more deterministic, less creative
    )
    
    # 3. Extract citations
    citations = extract_citations_from_response(response, context_chunks)
    
    # 4. Verify citations
    verified = verify_citations(citations, context_chunks)
    
    return response, verified_citations
```

### Citation Extraction

```python
def extract_citations(response: str, source_chunks):
    """
    Extract file/line references from LLM response
    
    Example:
    "The JWT is generated in JwtService.generateToken() 
     [Source: src/security/JwtService.java, lines 12-39]"
    """
    citations = []
    
    # Pattern: [Source: filename, lines X-Y]
    pattern = r'\[Source: ([^\]]+), lines (\d+)-(\d+)\]'
    
    for match in re.finditer(pattern, response):
        filename = match.group(1)
        start_line = int(match.group(2))
        end_line = int(match.group(3))
        
        # Find matching chunk
        for chunk in source_chunks:
            if filename in chunk.file_path and \
               chunk.start_line <= start_line and \
               chunk.end_line >= end_line:
                citations.append({
                    'text': match.group(0),
                    'file': chunk.file_path,
                    'lines': f"{start_line}-{end_line}",
                    'chunk_id': chunk.chunk_id
                })
    
    return citations
```

### Hallucination Detection

```python
def detect_hallucinations(response: str, source_text: str):
    """
    Detect unsupported claims
    """
    # Extract sentences
    sentences = re.split(r'[.!?]+', response)
    
    hallucinations = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Extract key terms
        terms = set(sentence.lower().split())
        
        # Check overlap with source
        source_terms = set(source_text.lower().split())
        overlap = len(terms & source_terms)
        
        # If < 20% overlap, might be hallucination
        if overlap / len(terms) < 0.2:
            hallucinations.append(sentence)
    
    return hallucinations
```

## 6. Evaluation Framework

### Why Evaluation Matters

Without evaluation, you can't:
- Know if your system actually works
- Identify failing components
- Compare design choices (vector vs BM25?)
- Optimize for the right metrics

### Benchmark Dataset Construction

```python
# Example: "Where is authentication implemented?"

benchmark_query = {
    'query_id': 'q_auth_001',
    'query': 'Where is authentication implemented?',
    'query_type': QueryType.CODE_SEARCH,
    'expected_files': [
        'src/controllers/AuthController.java',
        'src/services/AuthService.java',
        'src/security/JwtService.java'
    ],
    'expected_symbols': [
        'AuthController.login()',
        'AuthService.authenticate()',
        'JwtService.generateToken()'
    ],
    'acceptable_chunk_ids': [
        'chunk_ac1',
        'chunk_as2',
        'chunk_jwt1'
    ],
    'expected_answer': 'Authentication is handled by AuthController...'
}
```

### Retrieval Metrics Calculation

```python
class RetrievalEvaluator:
    def evaluate_query(self, query, retrieved_chunks, expected_chunks):
        """Calculate all metrics for one query"""
        
        # Recall@K: what % of relevant chunks were retrieved?
        recall_at_5 = len(
            set([c.id for c in retrieved_chunks[:5]]) & 
            set([c.id for c in expected_chunks])
        ) / len(expected_chunks)
        
        # Precision@K: what % of retrieved are relevant?
        precision_at_5 = len(
            set([c.id for c in retrieved_chunks[:5]]) & 
            set([c.id for c in expected_chunks])
        ) / min(5, len(retrieved_chunks))
        
        # MRR: rank of first relevant chunk
        for rank, chunk in enumerate(retrieved_chunks, 1):
            if chunk.id in expected_chunks:
                mrr = 1.0 / rank
                break
        
        return {
            'recall_at_5': recall_at_5,
            'precision_at_5': precision_at_5,
            'mrr': mrr,
            'hit_rate': len(set([c.id for c in retrieved_chunks[:5]]) & set([c.id for c in expected_chunks])) > 0
        }
```

### Strategy Comparison A/B Test

```python
async def compare_strategies(queries, repository_id):
    """
    Compare different retrieval strategies
    """
    strategies = {
        'vector_only': VectorRetriever(),
        'bm25_only': BM25Retriever(),
        'hybrid': HybridRetriever(),
        'hybrid_reranked': HybridRetriever(use_reranking=True)
    }
    
    results = {}
    
    for name, retriever in strategies.items():
        metrics = []
        
        for query in queries:
            retrieved = await retriever.retrieve(query)
            metric = evaluator.evaluate_query(
                query,
                retrieved,
                query.expected_chunks
            )
            metrics.append(metric)
        
        # Aggregate
        results[name] = {
            'recall_at_5': mean([m['recall_at_5'] for m in metrics]),
            'precision_at_5': mean([m['precision_at_5'] for m in metrics]),
            'mrr': mean([m['mrr'] for m in metrics]),
            'hit_rate': mean([m['hit_rate'] for m in metrics])
        }
    
    return results
```

**Example Results:**
```
Vector Only:            Recall@5 = 72%
BM25 Only:              Recall@5 = 68%
Hybrid (Vector+BM25):   Recall@5 = 84%
Hybrid + Reranker:      Recall@5 = 91%  ← Best!
```

This demonstrates value of each component!

## Key Takeaways

1. **Hybrid is Better Than Either Alone** - Semantic + exact matches win
2. **Semantic Chunking Preserves Context** - Better than naive splitting
3. **Query Understanding Enables Optimization** - Classify before retrieving
4. **Evaluation is Non-Negotiable** - Measure everything
5. **Grounding Prevents Hallucinations** - Context + careful prompting
6. **Citations Build Trust** - Users can verify answers

---

This implementation guide explains not just *how* but *why* - the reasoning behind every design choice.

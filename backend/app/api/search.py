"""Search API endpoint"""
from fastapi import APIRouter, HTTPException
from app.core.models import SearchRequest, SearchResult, RetrievedChunk, CodeChunk, CodeChunkMetadata

router = APIRouter()

# Mock search results
mock_search_results = {
    "chunk_001": {
        "chunk_id": "chunk_001",
        "repository_id": "repo_001",
        "file_path": "src/controllers/AuthController.java",
        "language": "java",
        "start_line": 24,
        "end_line": 48,
        "symbol_name": "login",
        "symbol_type": "method",
        "class_name": "AuthController",
        "parent_symbol": "AuthController",
        "code": "public class AuthController {\n  @PostMapping(\"/login\")\n  public ResponseEntity login(LoginRequest req) {\n    User user = authService.authenticate(req.username, req.password);\n    String token = jwtService.generateToken(user);\n    return ResponseEntity.ok(new LoginResponse(token));\n  }\n}",
        "imports": ["com.example.User", "com.example.JwtService"],
        "dependencies": ["JwtService", "UserRepository"],
        "metadata": {
            "access_modifier": "public",
            "return_type": "ResponseEntity",
            "parameters": ["LoginRequest"],
            "doc_comment": None
        }
    },
    "chunk_002": {
        "chunk_id": "chunk_002",
        "repository_id": "repo_001",
        "file_path": "src/services/AuthService.java",
        "language": "java",
        "start_line": 31,
        "end_line": 67,
        "symbol_name": "authenticateUser",
        "symbol_type": "method",
        "class_name": "AuthService",
        "parent_symbol": "AuthService",
        "code": "public boolean authenticateUser(String username, String password) {\n  User user = userRepository.findByUsername(username);\n  if (user == null) return false;\n  return passwordEncoder.matches(password, user.getPassword());\n}",
        "imports": ["com.example.User"],
        "dependencies": ["UserRepository", "PasswordEncoder"],
        "metadata": {
            "access_modifier": "public",
            "return_type": "boolean",
            "parameters": ["username", "password"],
            "doc_comment": "Authenticates user credentials"
        }
    }
}

@router.post("/", response_model=SearchResult)
async def search(request: SearchRequest):
    """Search codebase"""
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Mock search - in production this would call the hybrid retriever
    results = []
    for chunk_id, chunk_data in list(mock_search_results.items())[:request.limit]:
        chunk = CodeChunk(**chunk_data)
        retrieved = RetrievedChunk(
            chunk=chunk,
            vector_score=0.92,
            bm25_score=11.5,
            fusion_score=0.0312,
            rerank_score=0.94,
            final_score=0.94
        )
        results.append(retrieved)
    
    return SearchResult(
        chunks=results,
        total_results=len(results),
        latency_ms=145
    )

@router.get("/{repository_id}")
async def search_repository(repository_id: str, q: str = ""):
    """Search specific repository"""
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # Mock search
    return {
        "repository_id": repository_id,
        "query": q,
        "results": [],
        "total": 0
    }

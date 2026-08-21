"""
Application configuration settings
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/codebase_rag"
    )
    
    # Vector Store (Qdrant)
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    
    # Embeddings
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/code-bge-base-en-v1"
    )
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_BATCH_SIZE: int = 32
    
    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    
    # Reranker
    RERANKER_MODEL: str = os.getenv(
        "RERANKER_MODEL",
        "cross-encoder/ms-marco-MiniLM-L-12-v2"
    )
    
    # Retrieval
    VECTOR_TOP_K: int = 20  # Initial vector search results
    BM25_TOP_K: int = 20    # Initial BM25 results
    RERANKER_TOP_K: int = 5 # Final reranked results
    RRF_K: int = 60         # Reciprocal Rank Fusion parameter
    
    # Chunking
    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 100
    
    # Context
    MAX_CONTEXT_TOKENS: int = 6000
    MAX_SOURCE_CHARS: int = 50000
    
    # Processing
    MAX_UPLOAD_SIZE_MB: int = 500
    TEMP_UPLOAD_DIR: str = os.getenv("TEMP_UPLOAD_DIR", "/tmp/codebase_rag")
    
    # Language Support
    SUPPORTED_LANGUAGES: List[str] = [
        "python",
        "java",
        "javascript",
        "typescript",
        "cpp",
        "go",
        "rust",
        "csharp"
    ]
    
    # Parsing
    PARSERS: dict = {
        "python": "python",
        "java": "java",
        "javascript": "typescript",
        "typescript": "typescript",
        "cpp": "cpp",
        "c++": "cpp",
        "go": "go",
        "rust": "rust",
        "csharp": "c_sharp",
    }
    
    # Files to ignore
    IGNORED_PATTERNS: List[str] = [
        "*.pyc",
        "__pycache__",
        ".git",
        ".gitignore",
        "node_modules",
        "package-lock.json",
        "yarn.lock",
        ".lock",
        "build",
        "dist",
        "target",
        ".egg-info",
        "*.o",
        "*.so",
        ".env",
        ".env.local",
        "secrets",
        "credentials",
        ".DS_Store",
        "*.jpg",
        "*.png",
        "*.jpeg",
        "*.gif",
        "*.pdf",
    ]
    
    # Evaluation
    EVALUATION_BATCH_SIZE: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

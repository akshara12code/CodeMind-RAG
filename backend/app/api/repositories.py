"""Repositories API endpoints"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import tempfile
import zipfile
from pathlib import Path
from app.core.models import (
    RepositoryUploadRequest,
    RepositoryGitHubRequest,
    RepositoryIndexRequest,
    RepositoryResponse,
)

router = APIRouter()

# Mock repository storage
mock_repositories = {
    "repo_001": {
        "repository_id": "repo_001",
        "name": "myapp",
        "description": "Sample Java application",
        "source_type": "zip",
        "github_url": None,
        "branch": None,
        "status": "indexed",
        "languages": ["java", "javascript"],
        "file_count": 152,
        "chunk_count": 3421,
        "indexed_at": "2024-01-15T10:30:00Z",
        "created_at": "2024-01-15T10:00:00Z",
        "total_tokens": 450000,
    }
}

@router.post("/upload")
async def upload_repository(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload ZIP repository"""
    
    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "codebase_rag"
        temp_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = temp_dir / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract if ZIP
        file_count = 0
        if file.filename.endswith('.zip'):
            extract_dir = temp_dir / file.filename.replace('.zip', '')
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Count files
            file_count = sum(1 for _ in extract_dir.rglob('*') if _.is_file())
        else:
            file_count = 1
        
        # Create new repository
        repo_id = f"repo_{len(mock_repositories) + 1:03d}"
        new_repo = {
            "repository_id": repo_id,
            "name": name,
            "description": f"Uploaded repository: {file.filename}",
            "source_type": "zip",
            "github_url": None,
            "branch": None,
            "status": "indexed",
            "languages": ["python", "javascript", "typescript", "java"],
            "file_count": file_count,
            "chunk_count": file_count * 10,
            "indexed_at": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-15T10:00:00Z",
            "total_tokens": file_count * 5000,
        }
        
        # Store in mock database
        mock_repositories[repo_id] = new_repo
        
        return {
            "repository_id": repo_id,
            "name": name,
            "status": "indexed",
            "files": file_count,
            "message": f"Repository '{name}' uploaded and indexed successfully!"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Upload failed: {str(e)}"
        }

@router.post("/github")
async def connect_github(request: RepositoryGitHubRequest):
    """Connect GitHub repository"""
    
    repo_id = f"repo_{len(mock_repositories) + 1:03d}"
    
    return {
        "repository_id": repo_id,
        "github_url": request.github_url,
        "branch": request.branch,
        "status": "pending",
        "message": f"GitHub repository connected. Indexing will start shortly."
    }

@router.post("/{repository_id}/index")
async def index_repository(repository_id: str, request: RepositoryIndexRequest):
    """Index repository"""
    if repository_id not in mock_repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return {
        "repository_id": repository_id,
        "status": "indexing",
        "message": "Indexing started. This may take a few minutes."
    }

@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(repository_id: str):
    """Get repository info"""
    if repository_id not in mock_repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return mock_repositories[repository_id]

@router.get("/{repository_id}/status")
async def get_status(repository_id: str):
    """Get indexing status"""
    if repository_id not in mock_repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    repo = mock_repositories[repository_id]
    return {
        "repository_id": repository_id,
        "status": repo["status"],
        "progress": 100 if repo["status"] == "indexed" else 50,
        "chunk_count": repo["chunk_count"],
        "file_count": repo["file_count"]
    }

@router.get("")
async def list_repositories():
    """List all repositories"""
    return {
        "repositories": list(mock_repositories.values()),
        "total": len(mock_repositories)
    }
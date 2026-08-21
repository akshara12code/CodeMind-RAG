"""Health check endpoint"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational (mock)",
            "vector_store": "operational (mock)",
            "embeddings": "operational (mock)",
            "llm": "operational (mock)"
        }
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check - can handle requests"""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/live")
async def liveness_check():
    """Liveness check - application is alive"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }

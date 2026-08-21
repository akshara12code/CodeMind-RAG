"""Database module"""

async def init_db():
    """Initialize database"""
    pass

async def get_db():
    """Get database connection"""
    return MockDB()

class MockDB:
    """Mock database for demo"""
    
    async def get_repository(self, repo_id: str):
        return {
            "repository_id": repo_id,
            "name": "sample-repo",
            "status": "indexed"
        }

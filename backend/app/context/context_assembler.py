"""Context assembly and token budgeting"""
from typing import List, Optional
from pydantic import BaseModel
from app.core.models import CodeChunk, RetrievedChunk

class TokenCounter:
    """Simple token counter (approximate)"""
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Approximate token count (1 token ≈ 4 characters)"""
        return len(text) // 4

class ContextAssembler:
    """Assembles final context for LLM"""
    
    def __init__(self, max_tokens: int = 6000):
        self.max_tokens = max_tokens
        self.token_counter = TokenCounter()
    
    def assemble(self, chunks: List[RetrievedChunk], query: str) -> str:
        """Assemble context from retrieved chunks"""
        context = f"Query: {query}\n\n"
        context += "Retrieved Code:\n"
        context += "=" * 50 + "\n\n"
        
        current_tokens = self.token_counter.count_tokens(context)
        
        for chunk in chunks:
            chunk_text = self._format_chunk(chunk.chunk)
            chunk_tokens = self.token_counter.count_tokens(chunk_text)
            
            if current_tokens + chunk_tokens > self.max_tokens:
                break
            
            context += chunk_text + "\n\n"
            current_tokens += chunk_tokens
        
        return context
    
    @staticmethod
    def _format_chunk(chunk: CodeChunk) -> str:
        """Format chunk for display"""
        return f"""
FILE: {chunk.file_path}
LANGUAGE: {chunk.language}
LINES: {chunk.start_line}-{chunk.end_line}
SYMBOL: {chunk.symbol_name} ({chunk.symbol_type})

{chunk.code}
---
"""

class CitationExtractor:
    """Extract citations from LLM response"""
    
    @staticmethod
    def extract_citations(response: str, chunks: List[CodeChunk]) -> List[dict]:
        """Extract file/line references from response"""
        citations = []
        
        for chunk in chunks:
            if chunk.file_path in response or chunk.symbol_name in response:
                citations.append({
                    "file": chunk.file_path,
                    "lines": f"{chunk.start_line}-{chunk.end_line}",
                    "symbol": chunk.symbol_name,
                    "type": chunk.symbol_type
                })
        
        return citations

class PromptBuilder:
    """Build prompts for LLM"""
    
    SYSTEM_PROMPT = """You are an expert code assistant. Answer questions about codebases based on the provided code context.

IMPORTANT RULES:
1. Only reference code that exists in the provided context
2. Cite the specific file and line numbers for all code references
3. If information is not in the context, say "I cannot find this in the provided code"
4. Be precise and accurate
5. Explain code clearly"""
    
    @staticmethod
    def build_prompt(context: str, query: str) -> tuple[str, str]:
        """Build system and user prompts"""
        system_prompt = PromptBuilder.SYSTEM_PROMPT
        
        user_prompt = f"""{context}

Question: {query}

Please answer based only on the code provided above."""
        
        return system_prompt, user_prompt
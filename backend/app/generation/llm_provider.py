"""LLM provider abstraction"""

from typing import Dict, Optional, Tuple, AsyncGenerator

class LLMProvider:
    """Abstract LLM provider"""
    
    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Tuple[str, Dict]:
        """
        Generate text
        
        Returns:
            (response_text, token_usage)
        """
        # Would call OpenAI/Anthropic API
        return "Sample response", {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150
        }
    
    async def stream_generate(
        self,
        prompt: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """Stream text generation"""
        # Would stream tokens from LLM
        yield "Sample "
        yield "response"

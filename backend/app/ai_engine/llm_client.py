"""LLM client for Ollama/vLLM"""
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
import structlog

logger = structlog.get_logger()


class LLMClient:
    """Client for interacting with self-hosted LLM"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None
    ) -> str:
        """Generate text using LLM"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature or self.temperature,
                        "num_predict": max_tokens or self.max_tokens,
                    }
                }
                
                if system_prompt:
                    payload["system"] = system_prompt
                
                if format:
                    payload["format"] = format
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            logger.error("LLM generation error", error=str(e))
            return ""
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ) -> str:
        """Chat completion using LLM"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature or self.temperature,
                        "num_predict": self.max_tokens,
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
        except Exception as e:
            logger.error("LLM chat error", error=str(e))
            return ""
    
    async def check_connection(self) -> bool:
        """Check if LLM server is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


# Global LLM client instance
llm_client = LLMClient()

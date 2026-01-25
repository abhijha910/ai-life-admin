"""LLM client for Ollama/vLLM"""
import httpx
import asyncio
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
        """Generate text using LLM with improved error handling and retry logic"""
        max_retries = 2
        retry_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    # Try chat API first (better for structured outputs)
                    if system_prompt:
                        messages = [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                        
                        payload = {
                            "model": self.model,
                            "messages": messages,
                            "stream": False,
                            "options": {
                                "temperature": temperature or self.temperature,
                                "num_predict": max_tokens or self.max_tokens,
                            }
                        }
                        
                        if format == "json":
                            payload["format"] = "json"
                        
                        response = await client.post(
                            f"{self.base_url}/api/chat",
                            json=payload
                        )
                        response.raise_for_status()
                        result = response.json()
                        content = result.get("message", {}).get("content", "")
                        
                        if content:
                            return content
                    
                    # Fallback to generate API
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
                    
                    if format == "json":
                        payload["format"] = "json"
                    
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result.get("response", "")
                    
            except httpx.TimeoutException:
                if attempt < max_retries:
                    logger.warning(f"LLM request timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                logger.error("LLM request timeout after retries")
                return ""
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.error(f"LLM model '{self.model}' not found. Available models: {await self._list_models()}")
                elif e.response.status_code >= 500 and attempt < max_retries:
                    logger.warning(f"LLM server error, retrying... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"LLM HTTP error: {e.response.status_code} - {e.response.text}")
                return ""
            except Exception as e:
                logger.error(f"LLM generation error: {str(e)}", exc_info=True)
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                return ""
        
        return ""
    
    async def _list_models(self) -> List[str]:
        """List available models"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model.get("name", "") for model in data.get("models", [])]
        except Exception:
            pass
        return []
    
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

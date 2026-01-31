"""LLM client for Gemini/Ollama/vLLM with fallback support"""
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from app.config import settings
import structlog

# Gemini imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

logger = structlog.get_logger()


class LLMClient:
    """Client for interacting with Gemini/Ollama with fallback support"""

    def __init__(self):
        # Initialize Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini AI initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")

        # Initialize Ollama settings
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
        """Generate text using Gemini/Ollama with fallback chain and Kill Switch"""
        
        # Level 7: Kill Switch Check
        if hasattr(settings, 'AI_KILL_SWITCH') and settings.AI_KILL_SWITCH:
            logger.warning("AI Kill Switch is ACTIVE. Generation aborted.")
            return ""

        # Try Gemini first if available
        if self.gemini_model:
            try:
                # Combine system prompt and user prompt for Gemini
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                else:
                    full_prompt = prompt

                # Configure generation parameters
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature or self.temperature,
                    max_output_tokens=max_tokens or self.max_tokens,
                )

                # Add JSON format instruction if needed
                if format == "json":
                    full_prompt = f"{full_prompt}\n\nReturn your response as valid JSON only, no additional text or markdown."

                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.gemini_model.generate_content(
                        full_prompt,
                        generation_config=generation_config
                    )
                )

                if response and response.text:
                    result = response.text.strip()
                    logger.debug("Gemini generation successful")
                    return result
                else:
                    logger.warning("Gemini returned empty response")

            except Exception as e:
                error_str = str(e)
                # Check for quota/rate limit errors
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    logger.warning("Gemini API quota/rate limit exceeded. Consider upgrading your plan or waiting for quota reset. Falling back to Ollama.")
                else:
                    logger.warning(f"Gemini generation failed: {e}, falling back to Ollama")
                # Continue to Ollama fallback

        # Fallback to Ollama
        return await self._generate_ollama(prompt, system_prompt, temperature, max_tokens, format)

    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None
    ) -> str:
        """Generate text using Ollama with improved error handling and retry logic"""
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
                    
            except httpx.ConnectError as e:
                # Only log on first and last attempt to reduce noise
                if attempt == 0:
                    logger.debug("LLM server not available, will retry...")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                # Don't log error if LLM is not configured - this is expected
                logger.debug("LLM server not available after retries (this is normal if LLM is not configured)")
                return ""
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
                # Only log full error on last attempt to reduce noise
                if attempt >= max_retries - 1:
                    logger.warning(f"LLM generation failed after {max_retries} attempts: {str(e)}")
                elif attempt == 0:
                    # Log once on first attempt
                    logger.debug(f"LLM connection attempt failed, will retry: {str(e)}")
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
        """Check if any LLM service is available (Gemini or Ollama)"""
        # Check Gemini first
        if self.gemini_model:
            try:
                # Simple test generation to verify Gemini works
                test_response = await self.generate("Hello", system_prompt="You are a helpful assistant. Respond with 'OK'.")
                if test_response and test_response.strip():
                    logger.info("Gemini connection check successful")
                    return True
            except Exception as e:
                logger.warning(f"Gemini connection check failed: {e}")

        # Fallback to Ollama check
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    logger.info("Ollama connection check successful")
                    return True
        except Exception as e:
            logger.debug(f"Ollama connection check failed: {e}")
        return False


# Global LLM client instance
llm_client = LLMClient()

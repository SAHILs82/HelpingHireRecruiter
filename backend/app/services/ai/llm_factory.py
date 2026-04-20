import json
import logging
from typing import Type, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import retry, wait_exponential, stop_after_attempt

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class ModelFailure(Exception):
    """Exception raised when the LLM fails to produce a valid schema after retries."""
    pass

class LLMFactory:
    def __init__(self):
        self.api_key = settings.resolved_api_key
        if not self.api_key:
            logger.warning("No LLM API key provided. Fallbacks will trigger.")
            
        self.client = AsyncOpenAI(
            api_key=self.api_key or "dummy-key",
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout_seconds
        )
        self.model = settings.llm_model

    @classmethod
    def create_llm_provider(cls):
        """Creates and returns the appropriate LLMFactory based on environment settings"""
        return cls()

    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True
    )
    async def generate_structured(
        self, 
        *, 
        system_prompt: str, 
        user_prompt: str, 
        output_schema: Type[T]
    ) -> T:
        if not self.api_key:
            raise ModelFailure("No API key available")
            
        try:
            # Inject JSON schema format instructions into the system prompt.
            json_schema = output_schema.model_json_schema()
            enhanced_sys_prompt = (
                f"{system_prompt}\n\n"
                f"You MUST return ONLY valid JSON matching this schema:\n{json.dumps(json_schema)}\n"
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": enhanced_sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
                
            return output_schema.model_validate_json(content)
            
        except Exception as e:
            logger.error(f"LLM generate_structured failed: {str(e)}")
            raise ModelFailure(f"Failed to generate structured output: {str(e)}") from e

    def generate_structured_sync(
        self, 
        *, 
        system_prompt: str, 
        user_prompt: str, 
        output_schema: Type[T]
    ) -> T:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
        
        return asyncio.run(
            self.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                output_schema=output_schema
            )
        )

llm_client = LLMFactory.create_llm_provider()

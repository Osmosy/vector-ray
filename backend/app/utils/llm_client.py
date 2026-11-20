"""
LLM Client Wrapper с Cascade Fallback
Unified OpenAI format API calls
Поддержка цепочки резервирования моделей
"""

import json
import os
import re
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM Client с автоматическим переключением на резервные модели"""

    # Cascade fallback: Primary → Fallback 1 → Fallback 2 (локальные)
    MODEL_CASCADE = [
        "qwen3:8b",           # Primary: Qwen 3 8B (локальная, бесплатно)
        "qwen2.5:7b",         # Fallback 1: Qwen 2.5 7B (локальная, бесплатно)
        "llama3.2:latest",    # Fallback 2: Llama 3.2 (локальная, бесплатно)
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 300.0
    ):
        self.api_key = api_key or Config.LLM_API_KEY or "ollama"
        self.base_url = base_url or Config.LLM_BASE_URL or "http://localhost:11434/v1"
        self.model = model or Config.LLM_MODEL_NAME or self.MODEL_CASCADE[0]

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

        # Ollama context window size — prevents prompt truncation
        self._num_ctx = int(os.environ.get('OLLAMA_NUM_CTX', '8192'))
        
        # Track current model index for fallback
        self._current_model_idx = 0
        self._set_model_index(self.model)

    def _set_model_index(self, model: str):
        """Set current model index based on model name"""
        for idx, m in enumerate(self.MODEL_CASCADE):
            if m in model or model in m:
                self._current_model_idx = idx
                return
        # Если модель не в cascade, используем её как primary
        self._current_model_idx = 0

    def _is_ollama(self) -> bool:
        """Check if we're talking to an Ollama server."""
        return '11434' in (self.base_url or '') or 'ollama' in (self.base_url or '')

    def _get_fallback_model(self) -> Optional[str]:
        """Get next model in cascade"""
        next_idx = self._current_model_idx + 1
        if next_idx < len(self.MODEL_CASCADE):
            return self.MODEL_CASCADE[next_idx]
        return None

    def _chat_with_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict]
    ) -> str:
        """Execute chat request with specific model"""
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        # For Ollama: pass num_ctx via extra_body
        if self._is_ollama() and self._num_ctx:
            kwargs["extra_body"] = {
                "options": {"num_ctx": self._num_ctx}
            }

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        # Remove <think> content if present (MiniMax M2.5)
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Send chat request with cascade fallback

        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max token count
            response_format: Response format (e.g., JSON mode)

        Returns:
            Model response text
        """
        last_error = None
        
        # Try current model first
        try:
            logger.debug(f"Trying model: {self.model}")
            return self._chat_with_model(
                self.model, messages, temperature, max_tokens, response_format
            )
        except Exception as e:
            last_error = e
            logger.warning(f"Model {self.model} failed: {e}")

        # Try fallback models
        current_idx = self._current_model_idx
        for idx in range(current_idx + 1, len(self.MODEL_CASCADE)):
            fallback_model = self.MODEL_CASCADE[idx]
            try:
                logger.info(f"Trying fallback model: {fallback_model}")
                result = self._chat_with_model(
                    fallback_model, messages, temperature, max_tokens, response_format
                )
                # Update current model on success
                self.model = fallback_model
                self._current_model_idx = idx
                logger.info(f"Switched to fallback model: {fallback_model}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Fallback model {fallback_model} failed: {e}")
                continue

        # All models failed
        raise Exception(f"All models in cascade failed. Last error: {last_error}")

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Send chat request and return JSON

        Args:
            messages: Message list
            temperature: Temperature parameter
            max_tokens: Max token count

        Returns:
            Parsed JSON object
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        # Clean markdown code block markers
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format from LLM: {cleaned_response}")

    def reset_to_primary(self):
        """Reset to primary model"""
        self.model = self.MODEL_CASCADE[0]
        self._current_model_idx = 0
        logger.info("Reset to primary model: {self.model}")
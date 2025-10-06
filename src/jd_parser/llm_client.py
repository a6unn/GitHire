"""LLM client abstraction with OpenAI and Anthropic implementations."""

import os
from abc import ABC, abstractmethod
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """
        Get completion from LLM.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Generated text response
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client implementation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o-mini for cost efficiency)
        """
        from openai import OpenAI

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY env var not set")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def complete(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Get completion from OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured job requirements from job descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"}  # Force JSON output
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic API client implementation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-3-haiku for cost efficiency)
        """
        from anthropic import Anthropic

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and ANTHROPIC_API_KEY env var not set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def complete(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Get completion from Anthropic."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text


def create_llm_client(provider: str = "openai", **kwargs) -> LLMClient:
    """
    Factory function to create LLM client.

    Args:
        provider: "openai" or "anthropic"
        **kwargs: Additional arguments for the client

    Returns:
        LLMClient instance
    """
    if provider.lower() == "openai":
        return OpenAIClient(**kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicClient(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'anthropic'")

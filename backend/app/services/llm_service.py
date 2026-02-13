"""Azure OpenAI LLM Service wrapper."""

import json
from typing import AsyncIterator, Any

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI

from app.config import settings

_AZURE_COGSERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


def _build_azure_openai_client() -> AsyncAzureOpenAI:
    """Build an AsyncAzureOpenAI client using DefaultAzureCredential."""
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, _AZURE_COGSERVICES_SCOPE)
    return AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version=settings.azure_openai_api_version,
    )


class LLMResponse:
    """Response wrapper that includes content and token usage."""
    def __init__(self, content: str, tokens_used: int = 0):
        self.content = content
        self.tokens_used = tokens_used


class LLMService:
    """Service for interacting with Azure OpenAI models."""

    def __init__(self):
        self.client = _build_azure_openai_client()
        # Model deployments
        self.chat_deployment = settings.azure_openai_deployment_name  # gpt-5.2-chat
        self.gpt5_deployment = settings.azure_openai_gpt5_deployment_name  # gpt-5.1
        self.codex_deployment = settings.azure_openai_codex_deployment_name  # gpt-5.1-codex-max
        self.embedding_deployment = settings.azure_openai_textembedding_deployment_name
        # Track total tokens for current session
        self.last_tokens_used = 0

    async def complete(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 1.0,  # GPT-5.x only supports temperature=1
        max_tokens: int = 4096,
        model: str = None,
        **kwargs,
    ) -> str:
        """Generate a completion from the LLM."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        deployment = model or self.chat_deployment

        response = await self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=max_tokens,  # GPT-5.x uses max_completion_tokens
            **kwargs,
        )

        # Track token usage
        if response.usage:
            self.last_tokens_used = response.usage.total_tokens
        
        return response.choices[0].message.content

    async def complete_with_usage(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 1.0,
        max_tokens: int = 4096,
        model: str = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate a completion and return with token usage."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        deployment = model or self.chat_deployment

        response = await self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=max_tokens,
            **kwargs,
        )

        tokens = response.usage.total_tokens if response.usage else 0
        self.last_tokens_used = tokens
        
        return LLMResponse(response.choices[0].message.content, tokens)

    async def complete_messages(
        self,
        messages: list[dict],
        temperature: float = 1.0,  # GPT-5.x only supports temperature=1
        max_tokens: int = 4096,
        model: str = None,
        **kwargs,
    ) -> str:
        """Generate a completion from a list of messages."""
        deployment = model or self.chat_deployment

        response = await self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=max_tokens,  # GPT-5.x uses max_completion_tokens
            **kwargs,
        )

        return response.choices[0].message.content

    async def stream(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream a completion token by token."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        deployment = model or self.chat_deployment

        stream = await self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def stream_with_callback(
        self,
        prompt: str,
        system_prompt: str = None,
        on_token: Any = None,
        model: str = None,
        **kwargs,
    ) -> str:
        """Stream a completion, calling on_token for each chunk, and return the full text.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.
            on_token: Async callable(token: str) invoked for each streamed chunk.
            model: Optional model override.

        Returns:
            The complete response text.
        """
        parts: list[str] = []
        async for token in self.stream(prompt, system_prompt=system_prompt, model=model, **kwargs):
            parts.append(token)
            if on_token is not None:
                await on_token(token)
        return "".join(parts)

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings for text."""
        response = await self.client.embeddings.create(
            model=self.embedding_deployment,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        response = await self.client.embeddings.create(
            model=self.embedding_deployment,
            input=texts,
        )
        return [item.embedding for item in response.data]

    async def structured_output(
        self,
        prompt: str,
        output_schema: dict,
        system_prompt: str = None,
        model: str = None,
    ) -> dict:
        """Get structured JSON output using response_format."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        deployment = model or self.chat_deployment

        response = await self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": output_schema,
            },
        )

        # Track token usage
        if response.usage:
            self.last_tokens_used = response.usage.total_tokens

        return json.loads(response.choices[0].message.content)

    async def complete_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        model: str = None,
        **kwargs,
    ) -> dict:
        """Generate completion with tool calling support."""
        deployment = model or self.chat_deployment

        response = await self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            tools=tools,
            **kwargs,
        )

        choice = response.choices[0]
        result = {
            "content": choice.message.content,
            "tool_calls": None,
            "finish_reason": choice.finish_reason,
        }

        if choice.message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments),
                    },
                }
                for tc in choice.message.tool_calls
            ]

        return result


# Singleton instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

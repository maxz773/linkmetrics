
import os
import instructor
from openai import OpenAI
from anthropic import Anthropic
from pydantic import BaseModel, Field
from schemas import EvaluationResult

class AihubmixClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://aihubmix.com"
    
    def chat_completion(self, model: str, messages: list, **kwargs):
        """Unified chat completion interface"""
        if model.startswith("claude"):
            response = self._claude_completion(model, messages, **kwargs)
            return response.model_dump()
        else:
            response = self._openai_completion(model, messages, **kwargs)
            return response.model_dump()
    
    def _claude_completion(self, model: str, messages: list, **kwargs):
        """Claude API"""
        claude_client = instructor.from_anthropic(
            Anthropic(
            api_key=self.api_key,
            base_url=self.base_url)
        )
        # NOTE: The Anthropic (Claude) API strictly forbids including a 'system' role within the 'messages' array.
        # Instead, it requires the system prompt to be passed as a separate, top-level parameter in the API request.
        system_msg = next((m['content'] for m in messages if m['role'] == 'system'), "")
        user_msgs = [m for m in messages if m['role'] != 'system']

        if "max_tokens" not in kwargs:
            kwargs["max_tokens"] = 1024

        return claude_client.messages.create(
            model=model,
            messages=user_msgs,
            system=system_msg,
            response_model=EvaluationResult,
            **kwargs)
    
    def _openai_completion(self, model: str, messages: list, **kwargs):
        """OpenAI API"""
        openai_client = instructor.from_openai(
            OpenAI(
            api_key=self.api_key,
            base_url=f"{self.base_url}/v1")
        )
        return openai_client.chat.completions.create(
            model=model,
            messages=messages,
            response_model=EvaluationResult,
            **kwargs)
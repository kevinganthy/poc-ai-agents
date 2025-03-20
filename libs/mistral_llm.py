import logging
from llama_index.core.llms import CustomLLM
from mistralai import Mistral, UserMessage, models
from llama_index.core.llms import CompletionResponse, LLMMetadata, CompletionResponseGen
from llama_index.core.llms.callbacks import llm_completion_callback
from typing import Any, Optional
from llama_index.llms.ollama import Ollama
from .retry_utils import retry_with_exponential_backoff

logger = logging.getLogger(__name__)

class MistralLLM(CustomLLM):
    client: Mistral
    model: str = ""

    def __init__(self, model: str, api_key: str):
        mistral_client = Mistral(api_key=api_key)
        super().__init__(client=mistral_client)
        self.model = model
        self.client = mistral_client
    
    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=8192,
            num_output=1024,
            model_name=self.model
        )
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=2.0)
    def _call_mistral_api(self, messages):
        """Helper method to call Mistral API with retries"""
        try:
            return self.client.chat.complete(
                model=self.model,
                messages=messages,
            )
        except (models.HTTPValidationError, models.SDKError) as e:
            logger.warning(f"Mistral API error: {str(e)}")
            raise
    
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete the prompt."""
        messages = [UserMessage(role="user", content=prompt)]
        
        try:
            response = self._call_mistral_api(messages)
            return CompletionResponse(
                text=response.choices[0].message.content,
            )
        except Exception as e:
            logger.warning(f"Failed to use Mistral API: {str(e.message)}")
            raise

    @retry_with_exponential_backoff(max_retries=3, initial_delay=2.0)  
    def _call_mistral_stream_api(self, messages):
        """Helper method to call Mistral streaming API with retries"""
        try:
            return self.client.chat.stream(
                model=self.model,
                messages=messages,
                stream=True
            )
        except (models.HTTPValidationError, models.SDKError) as e:
            logger.warning(f"Mistral API error: {str(e.message)}")
            raise

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        """Stream complete the prompt."""
        messages = [UserMessage(role="user", content=prompt)]
        
        try:
            response_stream = self._call_mistral_stream_api(messages)
            
            response = ""
            for chunk in response_stream:
                if chunk.data.choices:
                    response += chunk.data.choices[0].delta.content
                    yield CompletionResponse(text=response)
                    
        except Exception as e:
            logger.warning(f"Failed to use Mistral streaming API: {str(e.message)}")
            raise


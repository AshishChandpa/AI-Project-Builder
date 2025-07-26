from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.models.ai_models import AIRequest, AIResponse


class BaseAIProvider(ABC):
    def __init__(self, api_key: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.config = config
        self.name = config.get("name", "Unknown Provider")
        self.models = config.get("models", {})
        self.rate_limit = config.get("rate_limit", 60)

    @abstractmethod
    async def generate_completion(self, request: AIRequest) -> AIResponse:
        """Generate code completion"""
        pass

    @abstractmethod
    async def explain_code(self, request: AIRequest) -> AIResponse:
        """Explain code functionality"""
        pass

    @abstractmethod
    async def review_code(self, request: AIRequest) -> AIResponse:
        """Review code for issues and improvements"""
        pass

    @abstractmethod
    async def chat(self, request: AIRequest) -> AIResponse:
        """Handle chat conversation"""
        pass

    @abstractmethod
    async def generate_code(self, request: AIRequest) -> AIResponse:
        """Generate code from natural language"""
        pass

    def get_model_for_task(self, task_type: str) -> str:
        """Get the appropriate model for a specific task"""
        return self.models.get(task_type, list(self.models.values())[0])

    async def health_check(self) -> bool:
        """Check if the provider is healthy"""
        try:
            # Implement basic health check
            return True
        except Exception:
            return False

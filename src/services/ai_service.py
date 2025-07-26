import asyncio
from typing import Dict, Any, Optional, List
from src.providers.base_provider import BaseAIProvider
from src.providers.gemini_provider import GeminiProvider
from src.models.ai_models import AIRequest, AIResponse, AIProvider, AITaskType
from src.cache.redis_client import RedisClient
from src.utils.logger import get_logger
from config.settings import settings
import json

logger = get_logger(__name__)


class AIService:
    def __init__(self):
        self.providers: Dict[AIProvider, BaseAIProvider] = {}
        self.redis_client = RedisClient()
        self._load_providers()

    def _load_providers(self):
        """Load and initialize AI providers"""
        try:
            with open("config/ai_providers.json", "r") as f:
                config = json.load(f)

            # Initialize Gemini
            if settings.GEMINI_API_KEY:
                self.providers[AIProvider.GEMINI] = GeminiProvider(
                    settings.GEMINI_API_KEY,
                    config["providers"]["gemini"]
                )

            # Initialize other providers if keys are available
            if settings.OPENAI_API_KEY:
                # self.providers[AIProvider.OPENAI] = OpenAIProvider(...)
                pass

            logger.info(f"Loaded {len(self.providers)} AI providers")

        except Exception as e:
            logger.error(f"Failed to load AI providers: {str(e)}")

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process AI request with the specified provider"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = await self.redis_client.get(cache_key)

            if cached_response and request.task_type != AITaskType.CHAT:
                logger.info(f"Cache hit for request: {cache_key}")
                return AIResponse.parse_raw(cached_response)

            # Get provider
            provider = self.providers.get(request.provider)
            if not provider:
                raise ValueError(f"Provider {request.provider} not available")

            # Route to appropriate method
            response = await self._route_request(provider, request)

            # Cache response (except for chat)
            if response.success and request.task_type != AITaskType.CHAT:
                await self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hour cache
                    response.json()
                )

            return response

        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            return AIResponse(
                request_id=request.session_id or "unknown",
                task_type=request.task_type,
                provider=request.provider,
                response="",
                processing_time=0,
                tokens_used=0,
                created_at=0,
                success=False,
                error_message=str(e)
            )

    async def _route_request(self, provider: BaseAIProvider, request: AIRequest) -> AIResponse:
        """Route request to appropriate provider method"""
        method_map = {
            AITaskType.CODE_COMPLETION: provider.generate_completion,
            AITaskType.CODE_EXPLANATION: provider.explain_code,
            AITaskType.CODE_REVIEW: provider.review_code,
            AITaskType.CODE_GENERATION: provider.generate_code,
            AITaskType.CHAT: provider.chat,
        }

        method = method_map.get(request.task_type)
        if not method:
            raise ValueError(f"Unsupported task type: {request.task_type}")

        return await method(request)

    def _generate_cache_key(self, request: AIRequest) -> str:
        """Generate cache key for request"""
        import hashlib
        key_data = f"{request.task_type}:{request.provider}:{request.prompt}:{request.context}:{request.language}"
        return f"ai_cache:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def get_provider_health(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}

        for provider_name, provider in self.providers.items():
            try:
                health_status[provider_name.value] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {provider_name}: {str(e)}")
                health_status[provider_name.value] = False

        return health_status

    async def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [provider.value for provider in self.providers.keys()]

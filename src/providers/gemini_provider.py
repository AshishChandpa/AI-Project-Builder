import asyncio
import time
from typing import Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.providers.base_provider import BaseAIProvider
from src.models.ai_models import AIRequest, AIResponse, AITaskType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, config: Dict[str, Any]):
        super().__init__(api_key, config)
        genai.configure(api_key=api_key)

        # Safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # Initialize models
        self._models = {}
        for task, model_name in self.models.items():
            self._models[task] = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=self.safety_settings
            )

    async def generate_completion(self, request: AIRequest) -> AIResponse:
        """Generate code completion using Gemini"""
        start_time = time.time()

        try:
            model = self._models.get("code_completion")

            prompt = self._build_completion_prompt(request)

            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=request.model_params.get("temperature", 0.7),
                    max_output_tokens=request.model_params.get("max_tokens", 2048),
                    top_p=request.model_params.get("top_p", 0.95),
                )
            )

            processing_time = time.time() - start_time

            return AIResponse(
                request_id=request.session_id or "unknown",
                task_type=request.task_type,
                provider=request.provider,
                response=response.text,
                metadata={
                    "model": self.models["code_completion"],
                    "language": request.language,
                    "prompt_tokens": len(prompt.split()),
                },
                processing_time=processing_time,
                tokens_used=len(response.text.split()),
                created_at=time.time(),
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini completion error: {str(e)}")
            return AIResponse(
                request_id=request.session_id or "unknown",
                task_type=request.task_type,
                provider=request.provider,
                response="",
                processing_time=time.time() - start_time,
                tokens_used=0,
                created_at=time.time(),
                success=False,
                error_message=str(e)
            )

    async def explain_code(self, request: AIRequest) -> AIResponse:
        """Explain code using Gemini"""
        start_time = time.time()

        try:
            model = self._models.get("code_explanation")

            prompt = f"""
            As an expert software engineer, please explain the following {request.language or 'code'} code:

            ```
            {request.prompt}
            ```

            Please provide:
            1. A clear explanation of what this code does
            2. How it works step by step
            3. Any important concepts or patterns used
            4. Potential improvements or best practices
            5. Any potential issues or edge cases

            Context: {request.context or 'No additional context provided'}
            """

            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                )
            )

            processing_time = time.time() - start_time

            return AIResponse(
                request_id=request.session_id or "unknown",
                task_type=request.task_type,
                provider=request.provider,
                response=response.text,
                metadata={
                    "model": self.models["code_explanation"],
                    "language": request.language,
                },
                processing_time=processing_time,
                tokens_used=len(response.text.split()),
                created_at=time.time(),
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini explanation error: {str(e)}")
            return self._error_response(request, str(e), time.time() - start_time)

    async def review_code(self, request: AIRequest) -> AIResponse:
        """Review code using Gemini"""
        start_time = time.time()

        try:
            model = self._models.get("code_review")

            prompt = f"""
            As a senior code reviewer, please review the following {request.language or 'code'}:

            ```
            {request.prompt}
            ```

            Please provide a comprehensive review including:
            1. **Code Quality** (1-10 score)
            2. **Issues Found** (bugs, security issues, performance problems)
            3. **Best Practices** (adherence to coding standards)
            4. **Suggestions** (improvements and optimizations)
            5. **Overall Assessment**

            Context: {request.context or 'No additional context provided'}

            Format your response as structured feedback with clear sections.
            """

            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=3000,
                )
            )

            processing_time = time.time() - start_time

            return AIResponse(
                request_id=request.session_id or "unknown",
                task_type=request.task_type,
                provider=request.provider,
                response=response.text,
                metadata={
                    "model": self.models["code_review"],
                    "language": request.language,
                },
                processing_time=processing_time,
                tokens_used=len(response.text.split()),
                created_at=time.time(),
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini review error: {str(e)}")
            return self._error_response(request, str(e), time.time() - start_time)

    async def chat(self, request: AIRequest) -> AIResponse:
        """Handle chat conversation using Gemini"""
        start_time = time.time()

        try:
            model = self._models.get("chat")

            # Create chat session if needed
            chat = model.start_chat(history=[])

            response = await asyncio.to_thread(
                chat.send_message,
                request.prompt
            )

            processing_time = time.time() - start_time

            return AIResponse(
                request_id=request.session_id or "unknown",
                task_type=request.task_type,
                provider=request.provider,
                response=response.text,
                metadata={
                    "model": self.models["chat"],
                    "session_id": request.session_id,
                },
                processing_time=processing_time,
                tokens_used=len(response.text.split()),
                created_at=time.time(),
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini chat error: {str(e)}")
            return self._error_response(request, str(e), time.time() - start_time)

    async def generate_code(self, request: AIRequest) -> AIResponse:
        """Generate code from natural language using Gemini"""
        start_time = time.time()

        try:
            model = self._models.get("code_completion")

            prompt = f"""
            Generate {request.language or 'code'} code based on the following requirements:

            **Requirements:** {request.prompt}

            **Context:** {request.context or 'No additional context'}

            Please provide:
            1. Clean, well-commented code
            2. Follow best practices for {request.language or 'the language'}
            3. Include error handling where appropriate
            4. Add brief explanation of the solution

            Generate only the code with minimal explanation unless specifically asked for more details.
            """

            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=4000,
                )
            )

            processing_time = time.time() - start_time

            return AIResponse(
                request_id=request.session_id or "unknown",
                task_type=request.task_type,
                provider=request.provider,
                response=response.text,
                metadata={
                    "model": self.models["code_completion"],
                    "language": request.language,
                },
                processing_time=processing_time,
                tokens_used=len(response.text.split()),
                created_at=time.time(),
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini code generation error: {str(e)}")
            return self._error_response(request, str(e), time.time() - start_time)

    def _build_completion_prompt(self, request: AIRequest) -> str:
        """Build prompt for code completion"""
        context_part = f"\nContext: {request.context}" if request.context else ""
        language_part = f"\nLanguage: {request.language}" if request.language else ""

        return f"""
        Complete the following code intelligently. Provide only the completion, no explanations:

        ```
        {request.prompt}
        ```
        {context_part}
        {language_part}

        Complete the code with best practices and proper formatting.
        """

    def _error_response(self, request: AIRequest, error_message: str, processing_time: float) -> AIResponse:
        """Create error response"""
        return AIResponse(
            request_id=request.session_id or "unknown",
            task_type=request.task_type,
            provider=request.provider,
            response="",
            processing_time=processing_time,
            tokens_used=0,
            created_at=time.time(),
            success=False,
            error_message=error_message
        )

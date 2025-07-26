from fastapi import APIRouter, HTTPException
from typing import List, Optional
from src.services.ai_service import AIService
from src.models.ai_models import AIRequest, AIResponse, AITaskType, AIProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
ai_service = AIService()


# Mock user for testing (remove auth dependency temporarily)
def get_mock_user():
    return {"id": "test_user", "email": "test@example.com", "username": "testuser"}


@router.post("/complete", response_model=AIResponse)
async def code_completion(request: AIRequest):
    """Generate code completion"""
    try:
        current_user = get_mock_user()
        request.user_id = current_user["id"]
        request.task_type = AITaskType.CODE_COMPLETION

        response = await ai_service.process_request(request)
        return response

    except Exception as e:
        logger.error(f"Code completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=AIResponse)
async def explain_code(request: AIRequest):
    """Explain code functionality"""
    try:
        current_user = get_mock_user()
        request.user_id = current_user["id"]
        request.task_type = AITaskType.CODE_EXPLANATION

        response = await ai_service.process_request(request)
        return response

    except Exception as e:
        logger.error(f"Code explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review", response_model=AIResponse)
async def review_code(request: AIRequest):
    """Review code for issues and improvements"""
    try:
        current_user = get_mock_user()
        request.user_id = current_user["id"]
        request.task_type = AITaskType.CODE_REVIEW

        response = await ai_service.process_request(request)
        return response

    except Exception as e:
        logger.error(f"Code review error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=AIResponse)
async def generate_code(request: AIRequest):
    """Generate code from natural language"""
    try:
        current_user = get_mock_user()
        request.user_id = current_user["id"]
        request.task_type = AITaskType.CODE_GENERATION

        response = await ai_service.process_request(request)
        return response

    except Exception as e:
        logger.error(f"Code generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(request: AIRequest):
    """Chat with AI assistant"""
    try:
        current_user = get_mock_user()
        request.user_id = current_user["id"]
        request.task_type = AITaskType.CHAT

        response = await ai_service.process_request(request)
        return response

    except Exception as e:
        logger.error(f"AI chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_available_providers():
    """Get list of available AI providers"""
    try:
        providers = await ai_service.get_available_providers()
        return {"providers": providers}

    except Exception as e:
        logger.error(f"Get providers error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_providers_health():
    """Get health status of all AI providers"""
    try:
        health_status = await ai_service.get_provider_health()
        return {"health": health_status}

    except Exception as e:
        logger.error(f"Provider health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import time  # Add this import

class AITaskType(str, Enum):
    CODE_COMPLETION = "code_completion"
    CODE_EXPLANATION = "code_explanation"
    CODE_REVIEW = "code_review"
    CODE_GENERATION = "code_generation"
    CODE_REFACTOR = "code_refactor"
    CODE_DEBUG = "code_debug"
    CHAT = "chat"

class AIProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"

class AIRequest(BaseModel):
    task_type: AITaskType
    provider: AIProvider = Field(default=AIProvider.GEMINI)
    prompt: str
    context: Optional[str] = None
    language: Optional[str] = None
    model_params: Dict[str, Any] = {}
    user_id: str = "anonymous"
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    request_id: str
    task_type: AITaskType
    provider: AIProvider
    response: str
    metadata: Dict[str, Any] = {}
    processing_time: float
    tokens_used: int
    created_at: float = Field(default_factory=time.time)  # Use timestamp
    success: bool = True
    error_message: Optional[str] = None

class ChatMessage(BaseModel):
    id: str
    session_id: str
    user_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = Field(default_factory=time.time)  # Use timestamp
    metadata: Dict[str, Any] = {}

class ChatSession(BaseModel):
    id: str
    user_id: str
    title: str
    messages: List[ChatMessage] = []
    created_at: float = Field(default_factory=time.time)  # Use timestamp
    updated_at: float = Field(default_factory=time.time)  # Use timestamp
    is_active: bool = True

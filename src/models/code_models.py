from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    HTML = "html"
    CSS = "css"
    SQL = "sql"

class CodeRequest(BaseModel):
    content: str = Field(..., description="Code content")
    language: Language = Field(..., description="Programming language")
    context: Optional[str] = Field(None, description="Additional context")
    file_path: Optional[str] = Field(None, description="File path for context")

class CodeCompletion(BaseModel):
    original_code: str
    completion: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    suggestions: List[str] = []
    language: Language

class CodeExplanation(BaseModel):
    code: str
    explanation: str
    complexity: str
    suggestions: List[str] = []
    language: Language

class CodeReview(BaseModel):
    code: str
    issues: List[Dict[str, Any]] = []
    suggestions: List[str] = []
    overall_score: float = Field(..., ge=0.0, le=10.0)
    language: Language

class FileInfo(BaseModel):
    id: str
    name: str
    path: str
    content: str
    language: Language
    size: int
    created_at: datetime
    updated_at: datetime
    project_id: str

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    files: List[FileInfo] = []
    created_at: datetime
    updated_at: datetime
    is_public: bool = False

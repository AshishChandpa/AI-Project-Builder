import os
import aiofiles
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import uuid
from datetime import datetime

from config.settings import settings
from src.models.code_models import FileInfo, Language
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileService:
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_FILE_EXTENSIONS

    def _get_language_from_extension(self, filename: str) -> Language:
        """Determine programming language from file extension"""
        extension = Path(filename).suffix.lower()

        language_map = {
            '.py': Language.PYTHON,
            '.js': Language.JAVASCRIPT,
            '.ts': Language.TYPESCRIPT,
            '.jsx': Language.JAVASCRIPT,
            '.tsx': Language.TYPESCRIPT,
            '.java': Language.JAVA,
            '.cpp': Language.CPP,
            '.c': Language.CPP,
            '.go': Language.GO,
            '.rs': Language.RUST,
            '.html': Language.HTML,
            '.css': Language.CSS,
            '.sql': Language.SQL,
        }

        return language_map.get(extension, Language.PYTHON)

    def _validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed"
            )

        return True

    async def save_file(self, file: UploadFile, user_id: str, project_id: str) -> FileInfo:
        """Save uploaded file"""
        try:
            # Validate file
            self._validate_file(file)

            # Generate unique filename
            file_id = str(uuid.uuid4())
            original_name = file.filename
            safe_filename = f"{file_id}_{original_name}"
            file_path = self.upload_dir / user_id / project_id / safe_filename

            # Create directories
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Read and validate file size
            content = await file.read()
            if len(content) > self.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size is {self.max_file_size} bytes"
                )

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            # Create file info
            file_info = FileInfo(
                id=file_id,
                name=original_name,
                path=str(file_path),
                content=content.decode('utf-8', errors='ignore'),
                language=self._get_language_from_extension(original_name),
                size=len(content),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                project_id=project_id
            )

            logger.info(f"File saved: {file_info.name} ({file_info.size} bytes)")
            return file_info

        except Exception as e:
            logger.error(f"File save error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_file(self, file_id: str, user_id: str) -> Optional[FileInfo]:
        """Get file by ID"""
        # Implementation depends on your storage choice
        # This is a simplified example
        pass

    async def update_file_content(self, file_id: str, content: str, user_id: str) -> FileInfo:
        """Update file content"""
        # Implementation depends on your storage choice
        pass

    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete file"""
        # Implementation depends on your storage choice
        pass

    async def list_files(self, user_id: str, project_id: Optional[str] = None) -> List[FileInfo]:
        """List user files"""
        # Implementation depends on your storage choice
        pass


file_service = FileService()

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List

from src.services.file_service import file_service
from src.models.code_models import FileInfo
from src.api.middleware.auth import get_current_user

router = APIRouter()

@router.post("/upload", response_model=FileInfo)
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload file to project"""
    try:
        file_info = await file_service.save_file(file, current_user["id"], project_id)
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}", response_model=FileInfo)
async def get_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get file by ID"""
    file_info = await file_service.get_file(file_id, current_user["id"])
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    return file_info

@router.put("/{file_id}/content", response_model=FileInfo)
async def update_file_content(
    file_id: str,
    content: str,
    current_user: dict = Depends(get_current_user)
):
    """Update file content"""
    try:
        file_info = await file_service.update_file_content(file_id, content, current_user["id"])
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete file"""
    success = await file_service.delete_file(file_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    return {"message": "File deleted successfully"}

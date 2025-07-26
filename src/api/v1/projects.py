from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional

from src.services.project_service import project_service
from src.models.code_models import Project
from src.api.middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=Project)
async def create_project(
    name: str,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create new project"""
    try:
        project = await project_service.create_project(name, description, current_user["id"])
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Project])
async def list_projects(
    include_public: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """List user projects"""
    try:
        projects = await project_service.list_projects(current_user["id"], include_public)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get project by ID"""
    project = await project_service.get_project(project_id, current_user["id"])
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update project"""
    project = await project_service.update_project(project_id, updates, current_user["id"])
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete project"""
    success = await project_service.delete_project(project_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return {"message": "Project deleted successfully"}

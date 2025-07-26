from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.models.code_models import Project, FileInfo
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectService:
    def __init__(self):
        # In-memory storage for demo (use database in production)
        self.projects: Dict[str, Project] = {}

    async def create_project(self, name: str, description: Optional[str], owner_id: str) -> Project:
        """Create new project"""
        project_id = str(uuid.uuid4())

        project = Project(
            id=project_id,
            name=name,
            description=description,
            owner_id=owner_id,
            files=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_public=False
        )

        self.projects[project_id] = project
        logger.info(f"Created project: {name} (ID: {project_id})")

        return project

    async def get_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Get project by ID"""
        project = self.projects.get(project_id)

        if not project:
            return None

        # Check access permissions
        if project.owner_id != user_id and not project.is_public:
            return None

        return project

    async def update_project(self, project_id: str, updates: Dict[str, Any], user_id: str) -> Optional[Project]:
        """Update project"""
        project = await self.get_project(project_id, user_id)

        if not project or project.owner_id != user_id:
            return None

        # Update fields
        for field, value in updates.items():
            if hasattr(project, field):
                setattr(project, field, value)

        project.updated_at = datetime.utcnow()
        self.projects[project_id] = project

        return project

    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete project"""
        project = await self.get_project(project_id, user_id)

        if not project or project.owner_id != user_id:
            return False

        del self.projects[project_id]
        logger.info(f"Deleted project: {project_id}")

        return True

    async def list_projects(self, user_id: str, include_public: bool = False) -> List[Project]:
        """List user projects"""
        projects = []

        for project in self.projects.values():
            if project.owner_id == user_id or (include_public and project.is_public):
                projects.append(project)

        return sorted(projects, key=lambda p: p.updated_at, reverse=True)

    async def add_file_to_project(self, project_id: str, file_info: FileInfo, user_id: str) -> bool:
        """Add file to project"""
        project = await self.get_project(project_id, user_id)

        if not project or project.owner_id != user_id:
            return False

        project.files.append(file_info)
        project.updated_at = datetime.utcnow()

        return True


project_service = ProjectService()

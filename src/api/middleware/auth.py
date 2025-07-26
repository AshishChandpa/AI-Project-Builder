from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from src.services.auth_service import auth_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        payload = auth_service.verify_token(credentials.credentials)

        # For demo purposes, return a mock user
        # In production, fetch from database
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username")
        }

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user (optional for public endpoints)"""
    if not credentials:
        return {"id": "anonymous", "email": None, "username": "anonymous"}

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return {"id": "anonymous", "email": None, "username": "anonymous"}

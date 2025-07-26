from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import uuid

from config.settings import settings
from src.models.user_models import User, UserCreate, UserLogin
from src.database.connection import AsyncSession
from src.utils.logger import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expire_minutes = settings.JWT_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt


    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )


    async def create_user(self, user_data: UserCreate, db: AsyncSession) -> User:
        """Create new user"""
        # Check if user exists
        # Implementation depends on your user storage choice
        # This is a simplified example

        hashed_password = self.get_password_hash(user_data.password)

        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )

        # Save to database (implement based on your choice)
        # db.add(user)
        # await db.commit()

        return user


    async def authenticate_user(self, credentials: UserLogin, db: AsyncSession) -> Optional[User]:
        """Authenticate user with credentials"""
        # Implementation depends on your user storage choice
        # This is a simplified example

        # user = await get_user_by_email(db, credentials.email)
        # if not user or not self.verify_password(credentials.password, user.hashed_password):
        #     return None

        # return user
        pass


    def create_user_token(self, user: User) -> str:
        """Create token for authenticated user"""
        token_data = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "type": "access_token"
        }
        return self.create_access_token(token_data)


auth_service = AuthService()

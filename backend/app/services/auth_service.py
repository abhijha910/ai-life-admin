"""Authentication service"""
from datetime import datetime, timedelta, time
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.auth import UserRegister, UserLogin
from app.config import settings
from app.utils.validators import validate_email_address, validate_password_strength
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    async def register_user(
        self,
        db: AsyncSession,
        user_data: UserRegister
    ) -> User:
        """Register a new user"""
        # Validate email
        if not validate_email_address(user_data.email):
            raise ValueError("Invalid email address")
        
        # Validate password
        is_valid, message = validate_password_strength(user_data.password)
        if not is_valid:
            raise ValueError(message)
        
        # Check if user exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        hashed_password = self.get_password_hash(user_data.password)
        new_user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            timezone="UTC"
        )
        
        db.add(new_user)
        
        # Create default settings in the same transaction
        default_settings = UserSettings(
            id=uuid.uuid4(),
            user_id=new_user.id,
            notification_preferences={},
            ai_preferences={},
            daily_plan_time=time(8, 0, 0),  # 8:00 AM default
            timezone="UTC"
        )
        db.add(default_settings)
        
        # Commit both user and settings together
        try:
            await db.commit()
            await db.refresh(new_user)
        except Exception as e:
            await db.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")
        
        return new_user
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        login_data: UserLogin
    ) -> User:
        """Authenticate user"""
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Invalid email or password")
        
        if not self.verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        return user
    
    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: str
    ) -> User:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        return result.scalar_one_or_none()


# Global auth service instance
auth_service = AuthService()

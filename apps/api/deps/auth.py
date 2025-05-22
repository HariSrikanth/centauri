from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.config import settings
from apps.api.core.database import get_db
from apps.api.models.user import User
from apps.api.schemas.auth import TokenPayload

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify JWT token
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.CLERK_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_data = TokenPayload(**payload)

        # Get user from database
        result = await db.execute(
            select(User).where(User.id == token_data.sub)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        return user

    except JWTError:
        raise credentials_exception

# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_active_user(
    current_user: CurrentUser,
) -> AsyncGenerator[User, None]:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    yield current_user

# Type alias for dependency injection
ActiveUser = Annotated[User, Depends(get_current_active_user)] 
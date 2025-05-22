from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.config import settings
from apps.api.core.database import get_db
from apps.api.deps.auth import ActiveUser
from apps.api.models.user import User
from apps.api.schemas.auth import (
    Integration,
    IntegrationCreate,
    Token,
    User as UserSchema,
    UserCreate,
)

router = APIRouter()

def create_token(
    user_id: str,
    token_type: str = "access",
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    """Create a JWT token."""
    if expires_delta is None:
        expires_delta = (
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            if token_type == "access"
            else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": token_type,
        "jti": str(uuid4()),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.CLERK_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt, expire

@router.post("/login", response_model=Token)
async def login(
    clerk_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Exchange Clerk session token for JWT."""
    # TODO: Validate clerk_token with Clerk API
    # For now, we'll assume it's valid and contains the user's email

    # Get or create user
    result = await db.execute(
        select(User).where(User.clerk_id == clerk_token)
    )
    user = result.scalar_one_or_none()

    if user is None:
        # Create new user (in real app, get user data from Clerk)
        user = User(
            email="user@example.com",  # Get from Clerk
            clerk_id=clerk_token,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Create tokens
    access_token, access_expire = create_token(str(user.id), "access")
    refresh_token, refresh_expire = create_token(str(user.id), "refresh")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int((access_expire - datetime.utcnow()).total_seconds()),
    )

@router.post("/googleAuth", response_model=dict)
async def google_auth(redirect_uri: str) -> dict:
    """Initiate Google OAuth flow."""
    # TODO: Implement Google OAuth flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth not implemented yet",
    )

@router.post("/googleAuth/callback", response_model=Integration)
async def google_auth_callback(
    code: str,
    state: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Integration:
    """Handle Google OAuth callback."""
    # TODO: Implement Google OAuth callback
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth callback not implemented yet",
    )

@router.post("/twitterConnect", response_model=Integration)
async def twitter_connect(
    oauth_token: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Integration:
    """Connect Twitter account."""
    # TODO: Implement Twitter OAuth flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Twitter OAuth not implemented yet",
    )

@router.post("/githubConnect", response_model=Integration)
async def github_connect(
    oauth_token: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Integration:
    """Connect GitHub account."""
    # TODO: Implement GitHub OAuth flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GitHub OAuth not implemented yet",
    )

@router.delete("/integration/{provider}")
async def delete_integration(
    provider: str,
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Delete an integration."""
    # TODO: Implement integration deletion
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Integration deletion not implemented yet",
    )

@router.get("/integration", response_model=list[Integration])
async def list_integrations(
    current_user: ActiveUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Integration]:
    """List user's integrations."""
    # TODO: Implement integration listing
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Integration listing not implemented yet",
    ) 
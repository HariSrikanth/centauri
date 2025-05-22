from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: UUID  # User ID
    exp: datetime
    type: str = "access"  # access or refresh
    jti: str  # JWT ID

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    display_name: str | None = None
    bio: str | None = None
    location: str | None = None
    website: str | None = None
    avatar_url: str | None = None
    tags: List[str] = Field(default_factory=list)

class UserCreate(UserBase):
    """User creation schema."""
    clerk_id: str

class UserUpdate(UserBase):
    """User update schema."""
    pass

class UserInDB(UserBase):
    """User database schema."""
    id: UUID
    clerk_id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDB):
    """User response schema."""
    pass

class IntegrationBase(BaseModel):
    """Base integration schema."""
    provider: str
    external_id: str
    scopes: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class IntegrationCreate(IntegrationBase):
    """Integration creation schema."""
    access_token: str
    refresh_token: str | None = None
    expires_at: datetime | None = None

class IntegrationUpdate(IntegrationBase):
    """Integration update schema."""
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None

class IntegrationInDB(IntegrationBase):
    """Integration database schema."""
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Integration(IntegrationInDB):
    """Integration response schema."""
    pass 
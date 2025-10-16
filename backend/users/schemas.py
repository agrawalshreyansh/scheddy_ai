from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base User schema with common attributes"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of the user")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user in database (with hashed password)"""
    hashed_password: str


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str
    user_id: UUID
    username: str
    email: str
    full_name: Optional[str] = None


class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None

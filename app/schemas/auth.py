"""Authentication request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRegister(BaseModel):
    """Payload for creating a user account."""

    organization_id: str
    email: str = Field(min_length=5, max_length=255)
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="member", min_length=3, max_length=50)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize and lightly validate email addresses."""
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Email address must contain @.")
        return normalized


class UserLogin(BaseModel):
    """Payload for requesting an access token."""

    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize login email addresses."""
        return value.strip().lower()


class UserResponse(BaseModel):
    """Public user account response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"

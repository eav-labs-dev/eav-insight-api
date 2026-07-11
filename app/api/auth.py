"""Authentication routes for EAV Insight API."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser
from app.core.exceptions import conflict, forbidden, not_found, unauthorized
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models import Organization, User
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: DbSession) -> User:
    """Create a user account for an existing organization."""
    organization = db.get(Organization, payload.organization_id)
    if organization is None:
        raise not_found("Organization not found.")

    existing_user = _get_user_by_email(db, payload.email)
    if existing_user is not None:
        raise conflict("A user with this email already exists.")

    user = User(
        organization_id=payload.organization_id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse)
def create_token(payload: UserLogin, db: DbSession) -> TokenResponse:
    """Authenticate a user and return a bearer token."""
    user = _get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise unauthorized("Invalid email or password.")

    if not user.is_active:
        raise forbidden("User account is inactive.")

    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUser) -> User:
    """Return the currently authenticated user."""
    return current_user

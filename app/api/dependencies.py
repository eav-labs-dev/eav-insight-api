"""Reusable FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import User

DbSession = Annotated[Session, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def authentication_error() -> HTTPException:
    """Return a consistent authentication failure response."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    """Resolve the current active user from a bearer token."""
    user_id = decode_access_token(token)
    if user_id is None:
        raise authentication_error()

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise authentication_error()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

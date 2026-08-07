from sqlalchemy.orm import Session

from app.database import SessionLocal

from fastapi import Depends, HTTPException

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.repositories.user_repository import user_repository

from app.security import verify_access_token

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    description="Paste your JWT access token here. Do not include the 'Bearer ' prefix."
)

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_access_token(
        credentials.credentials
    )

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )

    user = user_repository.get_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user

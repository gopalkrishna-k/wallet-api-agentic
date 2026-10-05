from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate
from app.services.auth_service import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    return auth_service.register(
        db,
        user_data
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    return auth_service.login(
        db,
        login_data
    )
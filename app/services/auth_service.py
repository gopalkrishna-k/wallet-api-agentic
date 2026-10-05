from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import user_repository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.security import (
    verify_password,
    create_access_token,
)
from app.services.user_service import user_service


class AuthService:

    def register(
        self,
        db: Session,
        user_data: UserCreate
    ) -> dict:
        new_user = user_service.register_user(db, user_data)
        token = create_access_token(
            {
                "user_id": new_user.id,
                "username": new_user.username
            }
        )
        return {
            "access_token": token,
            "token_type": "bearer"
        }

    def login(
        self,
        db: Session,
        login_data: LoginRequest
    ) -> dict:

        user = user_repository.get_by_username(
            db,
            login_data.username
        )

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password."
            )

        if not verify_password(
            login_data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password."
            )

        token = create_access_token(
            {
                "user_id": user.id,
                "username": user.username
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }


auth_service = AuthService()
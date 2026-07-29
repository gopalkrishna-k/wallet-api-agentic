from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import user_repository
from app.schemas.auth import LoginRequest
from app.security import (
    verify_password,
    create_access_token,
)


class AuthService:

    def login(
        self,
        db: Session,
        login_data: LoginRequest
    ):

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
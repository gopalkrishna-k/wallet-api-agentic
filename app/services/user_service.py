from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate
from app.security import hash_password
from app.repositories.wallet_repository import wallet_repository


class UserService:

    def register_user(
        self,
        db: Session,
        user_data: UserCreate
    ) -> User:

        existing_username = user_repository.get_by_username(
            db,
            user_data.username
        )

        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already exists."
            )

        existing_email = user_repository.get_by_email(
            db,
            user_data.email
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists."
            )

        hashed_password = hash_password(
            user_data.password
        )

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        try:
            user_repository.create(
                db,
                new_user
            )

            db.flush()

            wallet_repository.create(
                db,
                user_id=new_user.id
            )

            db.commit()

            db.refresh(new_user)

            return new_user

        except Exception:
            db.rollback()
            raise
        


user_service = UserService()
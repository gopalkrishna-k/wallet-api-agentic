from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.repositories.wallet_repository import wallet_repository


class WalletService:

    def get_balance(
        self,
        db: Session,
        user_id: int
    ) -> Wallet:

        wallet = wallet_repository.get_by_user_id(
            db,
            user_id
        )

        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found."
            )

        return wallet


wallet_service = WalletService()
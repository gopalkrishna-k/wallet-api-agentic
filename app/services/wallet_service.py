from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.repositories.wallet_repository import wallet_repository
from app.repositories.ledger_repository import ledger_repository
from app.schemas.wallet import WalletTransactionRequest

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

    def get_ledger(
        self,
        db: Session,
        user_id: int
    ):

        wallet = wallet_repository.get_by_user_id(
            db,
            user_id
        )

        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found."
            )

        return ledger_repository.get_by_wallet_id(
            db,
            wallet.id
        )

    def credit(
        self,
        db: Session,
        user_id: int,
        transaction: WalletTransactionRequest
    ):

        wallet = wallet_repository.get_by_user_id_for_update(
            db,
            user_id
        )

        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found."
            )
        try:
            # Update balance
            wallet.balance += transaction.amount

            # Create ledger entry
            ledger_repository.create(
                db=db,
                wallet_id=wallet.id,
                transaction_type="CREDIT",
                amount=transaction.amount,
                balance_after=wallet.balance
            )

            db.commit()

            db.refresh(wallet)

            return {
                "message": "Wallet credited successfully.",
                "balance": wallet.balance
            }
        except Exception:
            db.rollback()
            raise


    def debit(
        self,
        db: Session,
        user_id: int,
        transaction: WalletTransactionRequest
    ):

        wallet = wallet_repository.get_by_user_id_for_update(
            db,
            user_id
        )

        if wallet is None:
            raise HTTPException(
                status_code=404,
                detail="Wallet not found."
            )

        if wallet.balance < transaction.amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance."
            )

        try:

            # Decrease balance
            wallet.balance -= transaction.amount

            # Create ledger entry
            ledger_repository.create(
                db=db,
                wallet_id=wallet.id,
                transaction_type="DEBIT",
                amount=transaction.amount,
                balance_after=wallet.balance
            )

            db.commit()

            db.refresh(wallet)

            return {
                "message": "Wallet debited successfully.",
                "balance": wallet.balance
            }

        except Exception:

            db.rollback()

            raise


wallet_service = WalletService()

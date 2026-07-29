from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.wallet import Wallet


class WalletRepository:

    def create(
        self,
        db: Session,
        user_id: int
    ) -> Wallet:

        wallet = Wallet(
            user_id=user_id,
            balance=Decimal("0.00")
        )

        db.add(wallet)

        return wallet

    def get_by_user_id(
        self,
        db: Session,
        user_id: int
    ) -> Wallet | None:

        return (
            db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .first()
        )

    def get_by_user_id_for_update(
        self,
        db: Session,
        user_id: int
    ) -> Wallet | None:

        return (
            db.query(Wallet)
            .filter(Wallet.user_id == user_id)
            .with_for_update()
            .first()
        )
    
wallet_repository = WalletRepository()
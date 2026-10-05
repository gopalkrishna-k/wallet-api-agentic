from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.ledger import Ledger


class LedgerRepository:

    def create(
        self,
        db: Session,
        wallet_id: int,
        transaction_type: str,
        amount: Decimal,
        balance_after: Decimal
    ) -> Ledger:

        ledger = Ledger(
            wallet_id=wallet_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=balance_after
        )

        db.add(ledger)

        return ledger

    def get_by_wallet_id(
        self,
        db: Session,
        wallet_id: int
    ) -> list[Ledger]:

        return (
            db.query(Ledger)
            .filter(Ledger.wallet_id == wallet_id)
            .order_by(Ledger.created_at.desc(), Ledger.id.desc())
            .all()
        )


ledger_repository = LedgerRepository()

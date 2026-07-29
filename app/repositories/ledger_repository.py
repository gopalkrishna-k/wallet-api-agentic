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


ledger_repository = LedgerRepository()
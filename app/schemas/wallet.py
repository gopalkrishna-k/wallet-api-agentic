from decimal import Decimal

from pydantic import BaseModel, Field


class WalletBalanceResponse(BaseModel):
    user_id: int
    balance: Decimal

    model_config = {
        "from_attributes": True
    }

class WalletTransactionRequest(BaseModel):
    amount: Decimal = Field(
        gt=0,
        decimal_places=2
    )


class WalletTransactionResponse(BaseModel):
    message: str
    balance: Decimal
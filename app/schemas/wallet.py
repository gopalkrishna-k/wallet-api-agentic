from decimal import Decimal

from pydantic import BaseModel


class WalletBalanceResponse(BaseModel):
    user_id: int
    balance: Decimal

    model_config = {
        "from_attributes": True
    }
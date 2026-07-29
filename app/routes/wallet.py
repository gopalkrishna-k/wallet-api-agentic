from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.wallet import (
    WalletBalanceResponse,
    WalletTransactionRequest,
    WalletTransactionResponse,
)
from app.services.wallet_service import wallet_service

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)


@router.get(
    "/{user_id}/balance",
    response_model=WalletBalanceResponse
)
def get_balance(
    user_id: int,
    db: Session = Depends(get_db)
):
    return wallet_service.get_balance(
        db,
        user_id
    )

@router.post(
    "/{user_id}/credit",
    response_model=WalletTransactionResponse
)
def credit_wallet(
    user_id: int,
    transaction: WalletTransactionRequest,
    db: Session = Depends(get_db)
):

    return wallet_service.credit(
        db,
        user_id,
        transaction
    )

@router.post(
    "/{user_id}/debit",
    response_model=WalletTransactionResponse
)
def debit_wallet(
    user_id: int,
    transaction: WalletTransactionRequest,
    db: Session = Depends(get_db)
):
    return wallet_service.debit(
        db,
        user_id,
        transaction
    )
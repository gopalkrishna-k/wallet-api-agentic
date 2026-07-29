from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.wallet import (
    WalletBalanceResponse,
    WalletTransactionRequest,
    WalletTransactionResponse,
)
from app.services.wallet_service import wallet_service

from app.models.user import User

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)


@router.get("/balance")
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return wallet_service.get_balance(
        db=db,
        user_id=current_user.id
    )

@router.post("/credit")
def credit_wallet(
    transaction: WalletTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return wallet_service.credit(
        db=db,
        user_id=current_user.id,
        transaction=transaction
    )

@router.post("/debit")
def debit_wallet(
    transaction: WalletTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return wallet_service.debit(
        db=db,
        user_id=current_user.id,
        transaction=transaction
    )
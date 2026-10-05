from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.wallet import (
    LedgerEntryResponse,
    WalletBalanceResponse,
    WalletTransactionRequest,
    WalletTransactionResponse,
)
from app.services.wallet_service import wallet_service

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)


@router.get("/balance", response_model=WalletBalanceResponse)
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return wallet_service.get_balance(
        db=db,
        user_id=current_user.id
    )


@router.get("/ledger", response_model=list[LedgerEntryResponse])
def get_ledger(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return wallet_service.get_ledger(
        db=db,
        user_id=current_user.id
    )


@router.post("/credit", response_model=WalletTransactionResponse)
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


@router.post("/debit", response_model=WalletTransactionResponse)
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

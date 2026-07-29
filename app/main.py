from fastapi import FastAPI

from app.database import Base, engine
from app.routes.users import router as user_router

from app.routes.wallet import router as wallet_router

from app.routes.auth import router as auth_router

import app.models

app = FastAPI()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(user_router)

app.include_router(wallet_router)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Wallet API"}
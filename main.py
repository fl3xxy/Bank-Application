from fastapi import FastAPI
import models
from database import engine
from routers import auth, bankaccount, transactions
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(bankaccount.router)
app.include_router(transactions.router)


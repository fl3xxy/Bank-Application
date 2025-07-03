import random
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from .auth import get_current_user
from database import db_dependency
from models import BankAccount
router = APIRouter(tags=["bankaccount"])
user_dependency = Annotated[dict, Depends(get_current_user)]
def account_number_generator():
   return random.randint(10000000, 99999999)
@router.post("/create-account/", status_code=status.HTTP_201_CREATED)
async def create_bank_account(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    existing_account = db.query(BankAccount).filter(BankAccount.owner==user["id"]).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="User has a bank account")
    
    new_account = BankAccount(
      owner=user["id"],
      account_number=account_number_generator(),
      balance=0.0
    )
    db.add(new_account)
    db.commit()
    return {"message": "Account created", "account_number": new_account.account_number}

@router.get("/accounts")
async def read_account_by_user(user: user_dependency, db: db_dependency):
    if user is not None:
      return db.query(BankAccount).filter(BankAccount.owner==user["id"]).first()
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
@router.delete("/detete")
async def delete_bank_account(db:db_dependency, user: user_dependency):
   if user is None:
      raise HTTPException(status_code=401, detail="Unauthorized")
   account_to_delete = db.query(BankAccount).filter(user.get("id") == BankAccount.owner).first()
   if account_to_delete:
      db.delete(account_to_delete)
      db.commit()
   else:
      raise HTTPException(status_code=400, detail="Bank account does not exists")
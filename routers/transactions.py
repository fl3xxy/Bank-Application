from fastapi import APIRouter, HTTPException,status
from .bankaccount import user_dependency
from database import db_dependency
from models import BankAccount, Transactions
router = APIRouter(tags=["transactions"])



@router.post("/deposit/", status_code=status.HTTP_204_NO_CONTENT)
async def deposit_money(balance_to_deposit: float, user: user_dependency, db: db_dependency):
   if user is None:
      raise HTTPException(status_code=401, detail="Unauthorized")
   
   account = db.query(BankAccount).filter(BankAccount.owner == user.get('id')).first()
   if not account:
      raise HTTPException(status_code=400, detail="Account does not exist")
   account.balance += balance_to_deposit
   to_bank_acc = db.query(BankAccount).filter(BankAccount.owner == user.get('id')).first()
   transcation=Transactions(
      to_bank_account=to_bank_acc.account_number,
      balance=balance_to_deposit
   )
   db.add(transcation)
   db.commit()
   db.refresh(account)
   return {
        "message": f"Deposited {balance_to_deposit} successfully.",
        "new_balance": account.balance
    }

@router.post("/send/{bank_number}", status_code=status.HTTP_204_NO_CONTENT)
async def send_money(bank_number:int, balance:float, user: user_dependency, db:db_dependency):
   if user is None:
      raise HTTPException(status_code=401, detail="Unauthorized")
   
   from_account = db.query(BankAccount).filter(BankAccount.owner == user.get('id')).first()
   if not from_account:
      raise HTTPException(status_code=400, detail="Account does not exist")
   
   to_account = db.query(BankAccount).filter(BankAccount.account_number == bank_number).first()
   if not to_account:
      raise HTTPException(status_code=400, detail="Account does not exist")
   transaction = Transactions(
      from_bank_account=from_account.account_number,
      to_bank_account=to_account.account_number,
      balance=balance
   )
   from_account.balance -= balance
   to_account.balance += balance
   db.add(transaction)
   db.commit()
   db.refresh(from_account)
   db.refresh(to_account)
   return {
        "message": f"{balance} was sent successfully.",
        "new_balance": from_account.balance,
         "transactions": [
         {
            "transaction_id": t.transaction_id,
            "to": t.to_bank_account,
            "amount": t.balance

         }
         for t in transaction
      ]
    }

@router.get("/transactions-history", status_code=status.HTTP_200_OK)
async def read_history_of_transactions(user: user_dependency, db:db_dependency):
   if user is None:
      raise HTTPException(status_code=404, detail="Unauthorized")
   
   account = db.query(BankAccount).filter(BankAccount.owner == user.get('id')).first()
   transactions = db.query(Transactions).filter(
    (Transactions.from_bank_account == account.account_number) |
    (Transactions.to_bank_account == account.account_number)
    ).all()
   return {
      "account_number: ": account.account_number,
      "transactions": [
         {
            "transaction_id": t.transaction_id,
            "from": t.from_bank_account,
            "to": t.to_bank_account,
            "amount": t.balance

         }
         for t in transactions
      ]
   }

@router.post("/withrdaw/", status_code=status.HTTP_204_NO_CONTENT)
async def withrdaw_money(amount: float, user: user_dependency, db: db_dependency):
   if user is None:
      raise HTTPException(status_code=401, detail="Unauthorized")
   
   curr_bank_acc = db.query(BankAccount).filter(BankAccount.owner == user.get('id')).first()
   if curr_bank_acc.balance < amount:
      raise HTTPException(status_code=400, detail="Not enough money")
   curr_bank_acc.balance -= amount
   
   transaction = Transactions(
      from_bank_account=curr_bank_acc.account_number,
      balance=amount
   )
   db.add(transaction)
   db.commit()
   db.refresh(curr_bank_acc)
   return {"account_number: ": curr_bank_acc.account_number,
           "withdraw: ": amount,
           "balance_after_withdraw: ": curr_bank_acc.balance
           }

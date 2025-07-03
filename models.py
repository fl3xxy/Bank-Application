from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float

class Users(Base):
   __tablename__ = "users"

   id = Column(Integer, primary_key=True, index=True)
   username = Column(String, unique=True)
   first_name = Column(String)
   last_name = Column(String)
   hashed_password = Column(String)
class BankAccount(Base):
   __tablename__ = "bankaccount"

   id = Column(Integer, primary_key=True, index=True)
   account_number = Column(Integer, unique=True)
   owner = Column(Integer, ForeignKey('users.id'), nullable=False)
   balance = Column(Float, default=0.0)

class Transactions(Base):
   __tablename__ = "transactions"

   transaction_id = Column(Integer, primary_key=True, index=True)
   from_bank_account = Column(Integer, ForeignKey("bankaccount.account_number"))
   to_bank_account = Column(Integer, ForeignKey("bankaccount.account_number"))
   balance = Column(Float)
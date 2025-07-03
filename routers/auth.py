from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from database import db_dependency
from schema import Token, UserRequest
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
router = APIRouter(tags=['auth'])

SECRET_KEY = '0a5935eaa2d6f666eb69622464e3f21f2046238f5251b6b75aed2513678ff9e1'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

def authenticate_user(username: str, password: str, db: db_dependency):
   user = db.query(Users).filter(Users.username == username).first()
   if not user:
      raise HTTPException(status_code=404, detail="User not found")
   if not bcrypt_context.verify(password, user.hashed_password):
      raise HTTPException(status_code=404, detail="Password is not correct")
   return user

def create_access_token(username: str, user_id:int, expires_delta: timedelta):
   
   encode = {'sub': username, 'id': user_id}
   expires = datetime.now(timezone.utc) + expires_delta
   encode.update({'exp': expires})
   return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
   try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
      username: str = payload.get('sub')
      user_id: int = payload.get('id')
      if username is None or user_id is None:
         raise HTTPException(status_code=401, detail="Could not validate user.")
      return {'username': username, 'id': user_id}
   except JWTError:
         raise HTTPException(status_code=401, detail="Could not validate user.")

      


@router.post("/create-user/", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserRequest, db: db_dependency):
   new_user = Users(
      username=body.username,
      first_name=body.first_name,
      last_name=body.last_name,
      hashed_password=bcrypt_context.hash(body.password)
   )
   db.add(new_user)
   db.commit()

   return {"message: ": "New user was created"}

@router.get("/get-users", status_code=status.HTTP_200_OK)
async def read_all_users(db:db_dependency):
   return db.query(Users).all()


@router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
   user=authenticate_user(form_data.username,form_data.password, db)
   if not user:
      raise HTTPException(status_code=404, detail="User not found")
   token = create_access_token(user.username, user.id, timedelta(minutes=20))
   
   return {'access_token': token, 'token_type': 'bearer'}
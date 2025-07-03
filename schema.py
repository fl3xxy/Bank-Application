from pydantic import BaseModel, Field

class UserRequest(BaseModel):

   username: str = Field(max_length=25)
   first_name: str = Field(max_length=25)
   last_name: str = Field(max_length=25)
   password: str = Field(min_length=8)

class Token(BaseModel):
   access_token: str
   token_type:str


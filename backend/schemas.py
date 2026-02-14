from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UsuarioRegister (BaseModel):
    password : str
    email : EmailStr
    
class UsuarioOut (BaseModel): #devuelve una vez registrado el usuario. 
    email:EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    token_acceso : str
    token_type : str

class TokenData(BaseModel):
    id : Optional[str] = None
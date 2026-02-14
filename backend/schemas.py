from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UsuarioRegister (BaseModel):
    password : str
    email : EmailStr
    tipo : Optional[str] = None
    
class UsuarioOut (BaseModel): #devuelve una vez registrado el usuario. 
    email:EmailStr

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None    
    
class Token(BaseModel):
    token_acceso : str
    token_type : str

class TokenData(BaseModel):
    id : str
    user_type : str
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
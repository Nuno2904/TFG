from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def crear_token(data:dict):
    para_cifrar = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    para_cifrar.update({"exp": expire})
    token = jwt.encode(para_cifrar, SECRET_KEY, algorithm = ALGORITHM)
    return token
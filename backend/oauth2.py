from jose import JWTError, jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from . import schemas
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

tokenBearer = OAuth2PasswordBearer(tokenUrl='login') #aquí lo que estamos haciendo es indicar de dónde tiene que obtener el token barer, que es de login. 
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def crear_token(data:dict):
    para_cifrar = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    para_cifrar.update({"exp": expire}) #añadimos al diccionario el campo exp para que el token caduque.
    token = jwt.encode(para_cifrar, SECRET_KEY, algorithm = ALGORITHM)
    return token

def verificar_token(token: str, credenciales_exception):
    try:
        #token = Header + Payload + Friam donde Firma =HMAC(Header + Payload + Clave Secreta). 
        #Si alguien intercepta el token y cambia el header o el payload por otro id, cuando decodifiquemos la propia función se encarga de crear la firma con el payload y header que le ha llegado jutno con la clave
        #si han sido modifiicados las firmas no coinciden y por tanto slata el error.
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        id : str = payload.get("user_id")
        if id is None:
            raise credenciales_exception
        token_data = schemas.TokenData(id = id)
    except JWTError:
        raise credenciales_exception
    return token_data
    

def usuario_actual(token :str = Depends(tokenBearer)):   #vamos a coger el token, extraer el id y coger el usuario directamente de la base de datos
    credenciales_excepcion = HTTPException(status.HTTP_401_UNAUTHORIZED, detail = f"Could not validate credenials", headers={"WWW-Authenticate": "Bearer"})
    verificar_token(token, credenciales_excepcion)
from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags = ['Authentication'])

@router.post('/login')
def login(user_credential :OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.scalars(select(models.Usuario).where(models.Usuario.email == user_credential.username)).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Credenciales inválidas")
    if not utils.verify(user_credential.password, user.password):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Credenciales inválidas")
    token_acceso = oauth2.crear_token(data = {"user_id": user.id}) #enviamos un diccionario, porque jwt.encode necesita un diccionario.
    return {"token": token_acceso, "token_type": "bearer"}
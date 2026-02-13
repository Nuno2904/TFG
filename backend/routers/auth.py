from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
router = APIRouter(tags = ['Authentication'])

@router.post('/login')
def login(user_credential : schemas.UserLogin, db : Session = Depends(get_db)):
    user = db.scalars(select(models.Usuario).where(models.Usuario.email == user_credential.email)).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Credenciales inválidas")
    if not utils.verify(user_credential.password, user.password):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Credenciales inválidas")
    token_acceso = oauth2.crear_token(data = {"user_id": user.id})
    return {"token": token_acceso, "token_type": "bearer"}
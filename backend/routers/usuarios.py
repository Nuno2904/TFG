from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, utils
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/usuarios")

#Registro de usuarios
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.UsuarioOut)
def crear_usuario(user : schemas.UsuarioRegister, db:Session = Depends(get_db)):
    print(user.password)
    hashContrasena = utils.hash(user.password)
    user.password = hashContrasena 
    nuevo_usuario = models.Usuario(**user.dict()) #**user.dict() convierte el objeto user en un diccionario y luego lo descompone en argumentos de palabra clave para el constructor de Usuario. Esto es útil para crear una instancia de Usuario a partir de los datos proporcionados por el usuario.
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario) #actualiza el objeto nuevo_usuario con los datos de la base de datos, como el id generado automáticamente.    
    return nuevo_usuario

#Borrar usuario


#Nodificar datos usuario
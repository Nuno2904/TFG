from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from .. import schemas, models, utils
from ..database import get_db
from sqlalchemy.orm import Session
from .. import oauth2

router = APIRouter(prefix="/usuarios")

#Registro de usuarios
@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.UsuarioOut)
def crear_usuario(user : schemas.UsuarioRegister, db:Session = Depends(get_db)):
    #print(user.password)
    if db.scalars(select(models.Usuario).where(models.Usuario.email == user.email)).first():
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "El email ya está registrado")
    
    hashContrasena = utils.hash(user.password)
    user.password = hashContrasena 
    user.tipo = "usuario"
    nuevo_usuario = models.Usuario(**user.dict()) #**user.dict() convierte el objeto user en un diccionario y luego lo descompone en argumentos de palabra clave para el constructor de Usuario. Esto es útil para crear una instancia de Usuario a partir de los datos proporcionados por el usuario.
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario) #actualiza el objeto nuevo_usuario con los datos de la base de datos, como el id generado automáticamente.    
    return nuevo_usuario


#get usuario
@router.get("/{email}", response_model = schemas.UsuarioOut)
def buscar_usuario(email : EmailStr, db : Session = Depends(get_db)):
    
    user = db.scalars(select(models.Usuario).where(models.Usuaario.email == email))
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
    return user
    
    
#Borrar usuario
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def borrar_usuario(db : Session = Depends(get_db), current_user : models.Usuario = Depends(oauth2.usuario_actual)):
    db.delete(current_user)
    db.commit()
    return {"detail": "Usuario borrado correctamente"}
    


#Modificar datos usuario
@router.put("/me", response_model = schemas.UsuarioOut)
def modificar_usuario(datos : schemas.UsuarioUpdate, db : Session = Depends(get_db), current_user : models.Usuario = Depends(oauth2.usuario_actual)):
    
    #si se ha modificado la contraseña quiero hashearla antes de guardarla en la base de datos.
    if datos.password:
        hashContrasena = utils.hash(datos.password)
        datos.password = hashContrasena
    
    for key, value in datos.dict().items():
        setattr(current_user, key, value) #actualiza los atributos del objeto usuario_a_modificar con los valores del objeto user.
    db.commit()
    db.refresh(current_user)
    return current_user

#Borrar usuario siendo admin
@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_usuario_admin(email : EmailStr, db : Session = Depends(get_db), current_user : models.Usuario = Depends(oauth2.usuario_actual)):
        if current_user.tipo != "admin":
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "No tienes permisos para realizar esta acción")
        user = db.scalars(select(models.Usuario).where(models.Usuario.email == email)).first()
        if not user:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
        db.delete(user)
        db.commit()
        return {"detail": "Usuario borrado correctamente"}
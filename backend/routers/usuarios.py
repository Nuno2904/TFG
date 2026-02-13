from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/usuarios")

@router.post("/", status_code = status.HTTP_201_CREATED)
def crear_usuario():
    return {"message": "Usuario creado exitosamente"}


@router.get("/{usuario_id}", status_code = status.HTTP_302_FOUND)
def obtener_usario(usuario_id : int):
    return {"message": f"Usuario con id {usuario_id} encontrado"}
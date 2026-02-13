from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)

def verify(contrasena_plana, contrasena_hsd):
    return pwd_context.verify(contrasena_plana, contrasena_hsd)


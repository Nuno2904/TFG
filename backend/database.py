from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase
import os #es el intermediario entre el sistema operativo y el programa, es lo que permite leer variables de entrono, manejar archivos, etc. En este caso lo usamos para la url de l abase de datos. 

load_dotenv() # Carga las variables de entorno desde el archivo .env
DATABASE_URL = os.getenv("DATABASE_URL") # Obtiene la URL de la base de datos desde las variables de entorno
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base (DeclarativeBase): pass #DeclarativeBase es una clase base para los modelos de SQLAlchemy, que proporciona funcionalidades comunes a todas las tablas de la base de datos. Al heredar de DeclarativeBase, las clases de modelo pueden definir sus propias tablas y columnas, pero también pueden aprovechar las características proporcionadas por DeclarativeBase, como la gestión de sesiones y la creación automática de tablas.
#Permite a sqlalchemy entender que todo aquello que herede de Base es una tabla de la base de datos. 


# Dependencia para obtener la sesión
#cada petición tendrá su sesión aisalda  y cuando temrine se cerrará
def get_db():
    db = SessionLocal() #se crea la sesión
    try:
        yield db #fastapi entrega la sesión al endpoin con yield la ejecución se bloquea aquí y cuando se libera el recurso que entrega, continua con la ejecución 
    finally:
        db.close()
        
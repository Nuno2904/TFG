from fastapi import FastAPI
from . database import engine
from . import models
from .routers import usuarios, auth

models.Base.metadata.create_all(bind = engine) #crea las tablas en la base de datos, si no existen, a partir de los modelos definidos en models.py.
app = FastAPI() 

app.include_router(usuarios.router) #incluye el router de usuarios en la aplicación principal, lo que permite que las rutas definidas en usuarios.py estén disponibles en la aplicación FastAPI.    
app.include_router(auth.router)

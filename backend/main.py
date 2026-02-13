from fastapi import FastAPI
from . database import engine
from . import models


models.Base.metadata.create_all(bind = engine) #crea las tablas en la base de datos, si no existen, a partir de los modelos definidos en models.py.
app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}


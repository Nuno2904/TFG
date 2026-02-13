from .database import Base, engine
from sqlalchemy import Column, Integer, String, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Usuario(Base):
    __tablename__ = "usuarios"
    id : Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    #mapped es sqlalchemy moderno, pone en Mapped[X], donde X es como lo ves en python y Integer es como se almacena en la base de datos. 
    email : Mapped[String] = mapped_column(String, nullable = False)
    password : Mapped[String] = mapped_column(String, nullable = False)
    created_at : Mapped[TIMESTAMP] = mapped_column ( TIMESTAMP(timezone = True), server_default = func.now())
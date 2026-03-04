#crear una tabla que tenga como rimary key un id, como foregin key el id del usaurio, que cada fila corresponda con una entrada de datos, 
#dnde además tenga un campo de fecha y otro con el valor asignado a esa fecha. 
#la foclumna con la fecha se ha de llamar DS y la columna con el valor se ha de llamar y.

#escribe la tabla:
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.usuario import Usuario

class Data(Base):
    """
    Data database model.
    
    Represents a data entry associated with a user, including a timestamp and value.
    
    Attributes:
        id: Primary key - unique data entry identifier
        user_id: Foreign key referencing the associated user
        DS: Timestamp of the data entry (format: YYYY-MM-DD)
        y: Value assigned to the data entry
    """
    
    __tablename__ = "data"
    
    # 🔑 Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique data entry identifier"
    )
    
    # 🔗 Foreign Key to Usuario
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
        doc="Foreign key referencing the associated user"
    )
    
    # ⏰ Timestamp (DS) - formato YYYY-MM-DD
    DS: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Timestamp of the data entry (YYYY-MM-DD format)"
    )
    
    # 📊 Value (y)
    y: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Value assigned to the data entry"
    )
    
    # 🔄 Relationship to Usuario
    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="data_entries",
        doc="Relationship to the associated user"
    )
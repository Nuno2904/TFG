from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.data import Data


class Dataset(Base):
    """
    Dataset database model.
    
    Represents a dataset file uploaded by a user, containing metadata about the dataset.
    
    Attributes:
        id: Primary key - unique dataset identifier
        user_id: Foreign key referencing the associated user
        name: Name of the dataset file (original filename)
    """
    
    __tablename__ = "datasets"
    
    # 🔑 Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique dataset identifier"
    )
    
    # 🔗 Foreign Key to Usuario
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
        doc="Foreign key referencing the associated user"
    )
    
    # 📝 Dataset Name
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Name of the dataset file"
    )

    
    # 🔄 Relationships
    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="datasets",
        doc="Relationship to the associated user"
    )
    
    data_entries: Mapped[List["Data"]] = relationship(
        "Data",
        back_populates="dataset",
        cascade="all, delete-orphan",
        doc="Relationship to data entries in this dataset"
    )

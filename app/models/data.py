from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class Data(Base):
    """
    Data database model.
    
    Represents a single data entry (row) within a dataset, containing a timestamp and value.
    
    Attributes:
        id: Primary key - unique data entry identifier
        dataset_id: Foreign key referencing the associated dataset
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
    
    # 🔗 Foreign Key to Dataset
    dataset_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("datasets.id"),
        nullable=False,
        doc="Foreign key referencing the associated dataset"
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
    
    # 🔄 Relationship to Dataset
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="data_entries",
        doc="Relationship to the associated dataset"
    )
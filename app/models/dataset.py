"""
📊 Dataset ORM Model

Represents uploaded CSV files and their metadata.

Responsibilities:
- Define database table structure for datasets
- Store file metadata (path, size, row count)
- Track time series properties (date range, frequency)
- Maintain relationship to user who uploaded it
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Dataset(Base):
    """
    Dataset ORM Model
    
    Represents a CSV file uploaded by a user containing univariate time series data.
    
    Attributes:
        id: Primary key
        user_id: FK to User who uploaded
        name: User-friendly name
        description: Optional description
        file_path: Path to stored CSV file
        file_size_bytes: Size of uploaded file
        original_filename: Original filename from upload
        num_records: Number of rows in CSV
        date_column_name: Column header for date/time
        value_column_name: Column header for values to predict
        frequency: Time series frequency (D, H, W, M, Y)
        date_range_start: Min date in dataset
        date_range_end: Max date in dataset
        status: Dataset status (active, archived, deleted)
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    
    Relationships:
        - user: User who owns this dataset
        - predictions: List of predictions run on this dataset
    """
    
    __tablename__ = "dataset"
    
    # ═══════════════════════════════════════════════════════════════
    # 🔑 PRIMARY KEY
    # ═══════════════════════════════════════════════════════════════
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 🧑 OWNERSHIP
    # ═══════════════════════════════════════════════════════════════
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    
    # ═══════════════════════════════════════════════════════════════
    # 📝 DATASET METADATA
    # ══════════════════════
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 📂 FILE INFORMATION
    # ═══════════════════════════════════════════════════════════════
    
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    original_filename = Column(String(255), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 TIME SERIES PROPERTIES
    # ═══════════════════════════════════════════════════════════════
    
    num_records = Column(Integer, nullable=True)
    date_column_name = Column(String(100), nullable=False)
    value_column_name = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 📅 DATE RANGE
    # ═══════════════════════════════════════════════════════════════
    
    date_range_start = Column(DateTime, nullable=True)
    date_range_end = Column(DateTime, nullable=True)
    
    # ═══════════════════════════════════════════════════════════════
    # 🏷️ STATUS & TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════
    
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ═══════════════════════════════════════════════════════════════
    # 🔗 RELATIONSHIPS
    # ═══════════════════════════════════════════════════════════════
    
    # TODO: Define relationship to User model
    user = relationship("Usuario", back_populates="datasets")
    
    # TODO: Define relationship to Prediction model (back_populates)
    predictions = relationship("Prediction", back_populates="dataset")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Dataset(id={self.id}, name={self.name}, user_id={self.user_id})>"

"""
🏷️ Enumeration Types

Additional enumerations used across the application.
Keeps core/constants.py focused on constants only.
"""

from enum import Enum


class SortOrder(str, Enum):
    """Sorting order for list endpoints."""
    
    ASC = "asc"
    DESC = "desc"


class TrialStatus(str, Enum):
    """Status for hyperparameter tuning trials (future feature)."""
    
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    # TODO: Use this when implementing model hyperparameter optimization

"""
⚠️ Custom Exception Classes

Application-specific exceptions.

Responsibilities:
- Define custom error types
- Provide meaningful error messages
- Enable proper error handling in endpoints
"""


# ═══════════════════════════════════════════════════════════════════════════
# 📄 FILE EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════

class InvalidFileError(Exception):
    """Raised when uploaded file is invalid."""
    pass


class FileTooLargeError(Exception):
    """Raised when file exceeds size limit."""
    pass


class InvalidCSVError(Exception):
    """Raised when CSV format/structure is invalid."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 🗄️ DATABASE EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════

class DatasetNotFoundError(Exception):
    """Raised when dataset doesn't exist."""
    pass


class PredictionNotFoundError(Exception):
    """Raised when prediction doesn't exist."""
    pass


class ModelNotFoundError(Exception):
    """Raised when model doesn't exist."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 AUTHORIZATION EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════

class PermissionError(Exception):
    """Raised when user doesn't own resource."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# 🤖 ML EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════

class ModelNotFittedError(Exception):
    """Raised when predict called before fit."""
    pass


class InsufficientDataError(Exception):
    """Raised when dataset has too few points."""
    pass


class InvalidParametersError(Exception):
    """Raised when model parameters are invalid."""
    pass


class PredictionError(Exception):
    """Raised when prediction generation fails."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# ✅ VALIDATION EXCEPTIONS
# ═══════════════════════════════════════════════════════════════════════════

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

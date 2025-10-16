#exceptions.py
from fastapi import HTTPException
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.utcnow()
        logger.error(f"CustomException: {status_code} - {detail} - {error_code}")

class ValidationError(CustomException):
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")

class AuthenticationError(CustomException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail, error_code="AUTHENTICATION_ERROR")

class AuthorizationError(CustomException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=403, detail=detail, error_code="AUTHORIZATION_ERROR")
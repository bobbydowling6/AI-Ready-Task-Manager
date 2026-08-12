from fastapi import HTTPException

class AppException(Exception):
    def __init__(self, detail: str, status_code: int = 400):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

class NotFoundException(AppException):
    """Resource not found (404)."""
    def __init__(self, resource: str, resource_id):
        super().__init__(
            detail=f"{resource} with id {resource_id} not found",
            status_code=404
        )

class DuplicateException(AppException):
    """Duplicate resource conflict (409)."""
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            detail=f"{resource} with {field} '{value}' already exists",
            status_code=409
        )

class UnauthorizedException(AppException):
    """Authentication required (401)."""
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail=detail, status_code=401)

class ForbiddenException(AppException):
    """Insufficient permissions (403)."""
    def __init__(self, detail: str = "You don't have permission"):
        super().__init__(detail=detail, status_code=403)

class BadRequestException(AppException):
    """Bad request (400)."""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail=detail, status_code=400)
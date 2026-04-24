from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    message = "Application error"

    def __init__(
        self,
        message: str | None = None,
        *,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        self.status_code = status_code or self.status_code
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)

    def to_response(self, request: Request) -> dict[str, Any]:
        return {
            "error": {
                "type": self.__class__.__name__,
                "message": self.message,
                "status_code": self.status_code,
                "details": self.details,
            }
        }


class PetNotFoundError(AppError):
    status_code = 404
    message = "Pet not found"


class UserNotFoundError(AppError):
    status_code = 404
    message = "User not found"


class InviteNotFoundError(AppError):
    status_code = 404
    message = "Invite not found"


class SharedPetsNotFoundError(AppError):
    status_code = 404
    message = "Shared pets not found"


class SharedUsersNotFoundError(AppError):
    status_code = 404
    message = "Shared users not found"


class SharedAccessNotFoundError(AppError):
    status_code = 404
    message = "Shared access not found"


class PetAccessDeniedError(AppError):
    status_code = 403
    message = "Access to this pet is denied"


class PetOwnerOnlyError(AppError):
    status_code = 403
    message = "Only the pet owner can perform this action"


class AuthenticationError(AppError):
    status_code = 401
    message = "Authentication failed"


class InvalidCredentialsError(AuthenticationError):
    message = "Invalid credentials"


class InvalidTokenError(AuthenticationError):
    message = "Invalid or expired token"


class InvalidBotTokenError(AuthenticationError):
    message = "Invalid bot token"


class RefreshTokenError(AuthenticationError):
    message = "Invalid refresh token"


class RefreshTokenNotFoundError(AppError):
    status_code = 404
    message = "Refresh token not found"


class ConflictError(AppError):
    status_code = 409
    message = "Conflict"


class UserConflictError(ConflictError):
    message = "Email or phone already exists"


class AuthProviderMismatchError(AppError):
    status_code = 400
    message = "This account uses a different sign-in method"


class InviteExpiredError(AppError):
    status_code = 400
    message = "Invite has expired"


class InviteOwnerAcceptError(AppError):
    status_code = 400
    message = "Owner cannot accept the invite"


class InviteAlreadyAcceptedError(AppError):
    status_code = 400
    message = "Already have access"


class DatabaseIntegrityAppError(AppError):
    status_code = 400
    message = "Database integrity error"

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_response(request))


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    details = exc.detail
    message = details if isinstance(details, str) else "HTTP error"
    error = AppError(
        message,
        status_code=exc.status_code,
        details=details if not isinstance(details, str) else None,
    )
    return JSONResponse(status_code=error.status_code, content=error.to_response(request))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error = AppError(
        "Request validation failed",
        status_code=422,
        details=exc.errors(),
    )
    return JSONResponse(status_code=error.status_code, content=error.to_response(request))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error = AppError(
        "Internal server error",
        status_code=500,
        details={
            "exception_type": exc.__class__.__name__,
            "exception_message": str(exc),
        },
    )
    return JSONResponse(status_code=error.status_code, content=error.to_response(request))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

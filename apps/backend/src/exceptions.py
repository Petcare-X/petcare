from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.config import settings

logger = logging.getLogger(__name__)


def _sanitize_for_json(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(key): _sanitize_for_json(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_sanitize_for_json(item) for item in value]

    if isinstance(value, BaseException):
        return str(value)

    return str(value)


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
        is_production_5xx = settings.ENV != "dev" and self.status_code >= 500
        return {
            "error": {
                "type": "InternalServerError" if is_production_5xx else self.__class__.__name__,
                "message": self.message,
                "status_code": self.status_code,
                "details": None if is_production_5xx else _sanitize_for_json(self.details),
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
    message = "Credential already exists"


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

class AssistantMessageNotFound(AppError):
    status_code = 404
    message = "Assistant message not found"

class AssistantMessageError(AppError):
    status_code = 400
    message = "Assistant message is not valid"

class MessageGenerationError(AppError):
    status_code = 400
    message = "Error generating message"

class UserMessageNotFound(AppError):
    status_code = 404
    message = "User message not found"

class UserMessageError(AppError):
    status_code = 400
    message = "User message is not valid"

class UserPermissionError(AppError):
    status_code = 403
    message = "User does not have permission to access this content"

class ChatNotFound(AppError):   
    status_code = 404
    message = "Chat not found"

class ChatHistoryNotFound(AppError):
    status_code = 404
    message = "Chat history not found"

class OpenRouterApiError(AppError):
    status_code = 500
    message = "OpenRouter API error"

class OpenRouterResponseError(AppError):
    status_code = 500
    message = "OpenRouter response error"

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    if exc.status_code >= 500:
        logger.exception(
            "Application error on %s %s: %s",
            request.method,
            request.url.path,
            exc.message,
            exc_info=exc,
        )
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
        details=_sanitize_for_json(exc.errors()),
    )
    return JSONResponse(status_code=error.status_code, content=error.to_response(request))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import api_router
from src.exceptions import register_exception_handlers
from src.core.config import settings

app = FastAPI()
register_exception_handlers(app)


def get_cors_origins() -> list[str]:
    if settings.ENV == "dev":
        return [
            "http://localhost:5173",
            "http://172.17.0.1:5173",
            "http://192.168.0.105:5173",
        ]

    if settings.BACKEND_CORS_ORIGINS:
        return [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    if settings.INVITE_BASE_URL:
        invite_origin = settings.INVITE_BASE_URL.split("/", 3)[:3]
        if len(invite_origin) == 3:
            return ["/".join(invite_origin)]

    return []


origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

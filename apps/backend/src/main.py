from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import api_router
from src.exceptions import register_exception_handlers
from src.core.config import settings

app = FastAPI()
register_exception_handlers(app)

if settings.ENV == "dev":
    origins = [
        "http://localhost:5173",
        "http://172.17.0.1:5173",
        "http://192.168.0.105:5173"
    ]
else:
    origins = ["https://prod_domain.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
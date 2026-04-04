from fastapi import FastAPI
from src.api.router import api_router
from src.exceptions import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(api_router)

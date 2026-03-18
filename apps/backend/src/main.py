from fastapi import FastAPI
from src.api.router import common_router
from src.exceptions import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(common_router)

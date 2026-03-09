from fastapi import FastAPI
from src.api.users import router as users_router

app = FastAPI(title="PetCare API", redoc_url=None)
app.include_router(users_router)
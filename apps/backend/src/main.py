from fastapi import FastAPI
from src.api.users import router as users_router


app = FastAPI()

app = FastAPI()
app.include_router(users_router)
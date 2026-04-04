from fastapi import APIRouter

from src.api.auth import auth_router
from src.api.llm_chat import chat_router
from src.api.map import map_router
from src.api.pet_documents import document_types_router
from src.api.pets import pets_router
from src.api.sharing import invites_router
from src.api.upload_data import upload_router
from src.api.users import users_router

api_router = APIRouter()

api_router.include_router(users_router)
api_router.include_router(pets_router)
api_router.include_router(document_types_router)
api_router.include_router(invites_router)
api_router.include_router(auth_router)
api_router.include_router(upload_router)
api_router.include_router(map_router)
api_router.include_router(chat_router)

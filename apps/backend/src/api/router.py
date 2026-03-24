from fastapi import APIRouter

from src.api import (users_router, 
                     pets_router, 
                     sharing_router, 
                     pet_documents_router, 
                     upload_router,
                     map_router,
                     chat_router)
from src.api.auth import auth_router

common_router = APIRouter()

common_router.include_router(users_router)
common_router.include_router(pets_router)
common_router.include_router(pet_documents_router)
common_router.include_router(sharing_router)
common_router.include_router(auth_router)
common_router.include_router(upload_router)
common_router.include_router(map_router)
common_router.include_router(chat_router)
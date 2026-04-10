from .animals import animal_types_router
from .auth import auth_router
from .llm_chat import chat_router
from .map import map_router
from .pet_documents import document_types_router, pet_documents_router
from .pet_photos import pet_photos_router
from .pets import pets_router
from .router import api_router
from .sharing import invites_router, pet_shares_router
from .upload_data import upload_router
from .users import users_router

__all__ = (
    'api_router',
    'animal_types_router',
    'auth_router',
    'chat_router',
    'document_types_router',
    'invites_router',
    'map_router',
    'pet_documents_router',
    'pet_photos_router',
    'pet_shares_router',
    'pets_router',
    'upload_router',
    'users_router',
)

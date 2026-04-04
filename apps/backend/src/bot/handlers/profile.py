from aiogram import Router

from .pet_delete import router as pet_delete_router
from .pet_details import router as pet_details_router
from .pet_documents import router as pet_documents_router
from .pet_photo import router as pet_photo_router


router = Router()
router.include_router(pet_photo_router)
router.include_router(pet_delete_router)
router.include_router(pet_documents_router)
router.include_router(pet_details_router)
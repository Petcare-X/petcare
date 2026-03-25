from aiogram import Router

from .common import router as common_router
from .llm_chat import router as llm_chat_router
from .navigation import router as navigation_router
from .profile import router as profile_router
from .registration import router as registration_router
from .sharing import router as sharing_router


router = Router()
router.include_router(common_router)
router.include_router(navigation_router)
router.include_router(llm_chat_router)
router.include_router(sharing_router)
router.include_router(registration_router)
router.include_router(profile_router)

__all__ = ("router",)

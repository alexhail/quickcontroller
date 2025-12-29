from fastapi import APIRouter

from . import audit, controllers, system, users

router = APIRouter()
router.include_router(controllers.router)
router.include_router(users.router)
router.include_router(system.router)
router.include_router(audit.router)

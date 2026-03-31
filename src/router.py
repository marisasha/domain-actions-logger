from fastapi import APIRouter

from src.auth.service import router as auth_router
from src.domain.service import router as domain_router

main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(domain_router)

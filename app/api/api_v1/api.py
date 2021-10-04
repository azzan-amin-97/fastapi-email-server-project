from fastapi import APIRouter

from app.api.api_v1.endpoints import services

router = APIRouter()

router.include_router(services.router, prefix="/v1")


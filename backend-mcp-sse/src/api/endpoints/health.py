"""
헬스체크 엔드포인트
"""
from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_api_router
from core.api_router import APIRouter as CoreAPIRouter
from core.config import settings
from models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    api_router: Annotated[CoreAPIRouter, Depends(get_api_router)]
):
    """
    헬스체크 엔드포인트

    서비스 상태와 로드된 API 개수를 반환합니다.
    """
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        loaded_apis=len(api_router.apis)
    )

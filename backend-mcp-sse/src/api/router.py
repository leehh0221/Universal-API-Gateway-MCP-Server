"""
메인 API 라우터
"""
from fastapi import APIRouter

from api.endpoints import apis, health, proxy

api_router = APIRouter()

# 헬스체크 엔드포인트 등록
api_router.include_router(health.router)

# API 관리 엔드포인트 등록
api_router.include_router(apis.router)

# 프록시 엔드포인트 등록
api_router.include_router(proxy.router)

"""
FastAPI 의존성 주입
"""
from typing import Annotated

from fastapi import Depends

from core.api_router import APIRouter
from services.api_service import APIService
from services.proxy_service import ProxyService


# 전역 APIRouter 인스턴스 (main.py에서 설정됨)
_api_router_instance: APIRouter = None


def set_api_router(api_router: APIRouter) -> None:
    """
    전역 APIRouter 인스턴스 설정

    Args:
        api_router: APIRouter 인스턴스
    """
    global _api_router_instance
    _api_router_instance = api_router


def get_api_router() -> APIRouter:
    """
    APIRouter 인스턴스 반환

    Returns:
        APIRouter 인스턴스
    """
    return _api_router_instance


def get_api_service(
    api_router: Annotated[APIRouter, Depends(get_api_router)]
) -> APIService:
    """
    APIService 인스턴스 반환

    Args:
        api_router: 주입된 APIRouter

    Returns:
        APIService 인스턴스
    """
    return APIService(api_router)


def get_proxy_service(
    api_router: Annotated[APIRouter, Depends(get_api_router)]
) -> ProxyService:
    """
    ProxyService 인스턴스 반환

    Args:
        api_router: 주입된 APIRouter

    Returns:
        ProxyService 인스턴스
    """
    return ProxyService(api_router)

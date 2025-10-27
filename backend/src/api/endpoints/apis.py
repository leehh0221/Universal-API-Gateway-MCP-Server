"""
API 관리 엔드포인트
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_api_service
from models.api_definition import APIEndpoint
from models.responses import APIListResponse, APIDetailResponse
from services.api_service import APIService

router = APIRouter(prefix="/apis", tags=["APIs"])


@router.get("", response_model=APIListResponse)
async def list_apis(
    service: Annotated[APIService, Depends(get_api_service)]
):
    """
    등록된 모든 API 목록 조회

    모든 등록된 API 서비스의 정보를 반환합니다.
    """
    apis = await service.get_all_apis()
    return APIListResponse(
        total=len(apis),
        apis=apis
    )


@router.get("/{service_name}", response_model=APIDetailResponse)
async def get_api_detail(
    service_name: str,
    service: Annotated[APIService, Depends(get_api_service)]
):
    """
    특정 API 상세 정보 조회

    서비스 이름으로 특정 API의 상세 정보를 조회합니다.
    """
    api = await service.get_api(service_name)
    if not api:
        raise HTTPException(
            status_code=404,
            detail=f"API not found: {service_name}"
        )

    return APIDetailResponse(api=api)


@router.get("/{service_name}/endpoints", response_model=List[APIEndpoint])
async def list_endpoints(
    service_name: str,
    service: Annotated[APIService, Depends(get_api_service)]
):
    """
    특정 API의 모든 엔드포인트 조회

    서비스 이름으로 해당 API의 모든 엔드포인트 목록을 조회합니다.
    """
    endpoints = await service.get_endpoints(service_name)
    if endpoints is None:
        raise HTTPException(
            status_code=404,
            detail=f"API not found: {service_name}"
        )

    return endpoints

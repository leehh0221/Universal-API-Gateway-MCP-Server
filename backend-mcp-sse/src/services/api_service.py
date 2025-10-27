"""
API 관리 서비스
"""
from typing import List, Optional

from core.api_router import APIRouter
from models.api_definition import APIDefinition, APIEndpoint


class APIService:
    """API 관리 서비스"""

    def __init__(self, api_router: APIRouter):
        """
        Args:
            api_router: APIRouter 인스턴스
        """
        self.api_router = api_router

    async def get_all_apis(self) -> List[APIDefinition]:
        """
        등록된 모든 API 목록 조회

        Returns:
            API 정의 목록
        """
        return list(self.api_router.apis.values())

    async def get_api(self, service_name: str) -> Optional[APIDefinition]:
        """
        특정 API 상세 정보 조회

        Args:
            service_name: 서비스 이름

        Returns:
            API 정의 또는 None
        """
        return self.api_router.get_api(service_name)

    async def get_endpoints(self, service_name: str) -> Optional[List[APIEndpoint]]:
        """
        특정 API의 모든 엔드포인트 조회

        Args:
            service_name: 서비스 이름

        Returns:
            엔드포인트 목록 또는 None
        """
        api_def = self.api_router.get_api(service_name)
        if not api_def:
            return None

        return api_def.endpoints

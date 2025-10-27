"""
API 프록시 서비스
"""
from typing import Any, Dict

from core.api_router import APIRouter


class ProxyService:
    """API 프록시 서비스"""

    def __init__(self, api_router: APIRouter):
        """
        Args:
            api_router: APIRouter 인스턴스
        """
        self.api_router = api_router

    async def call_endpoint(
        self,
        service_name: str,
        endpoint_id: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        API 엔드포인트 호출

        Args:
            service_name: 서비스 이름
            endpoint_id: 엔드포인트 ID
            arguments: 호출 인자

        Returns:
            API 응답 데이터

        Raises:
            ValueError: 잘못된 서비스 또는 엔드포인트
            Exception: API 호출 실패
        """
        # 엔드포인트 조회
        endpoint = self.api_router.get_endpoint(service_name, endpoint_id)
        if not endpoint:
            raise ValueError(
                f"Endpoint not found: {service_name}/{endpoint_id}"
            )

        # Tool 이름으로 호출
        tool_name = endpoint.name
        return await self.api_router.route_request(tool_name, arguments)

"""
API 프록시 엔드포인트
"""
from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_proxy_service
from models.requests import ProxyRequest
from models.responses import ProxyResponse
from services.proxy_service import ProxyService
from utils.logger import setup_logger

router = APIRouter(prefix="/proxy", tags=["Proxy"])
logger = setup_logger(__name__)


@router.post("/test", response_model=ProxyResponse)
async def test_api_endpoint(
    request: ProxyRequest,
    service: Annotated[ProxyService, Depends(get_proxy_service)]
):
    """
    API 엔드포인트 테스트 호출

    대시보드에서 "Test" 버튼 클릭 시 사용됩니다.
    실제 외부 API를 호출하고 결과를 반환합니다.
    """
    try:
        logger.info(
            f"Testing endpoint: {request.service_name}/{request.endpoint_id}"
        )

        result = await service.call_endpoint(
            service_name=request.service_name,
            endpoint_id=request.endpoint_id,
            arguments=request.arguments
        )

        return ProxyResponse(
            success=True,
            data=result
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return ProxyResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        logger.error(f"API call error: {e}", exc_info=True)
        return ProxyResponse(
            success=False,
            error=str(e)
        )

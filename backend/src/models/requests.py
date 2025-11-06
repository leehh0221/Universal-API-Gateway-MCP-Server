"""
요청 데이터 모델
"""
from typing import Any, Dict

from pydantic import BaseModel, Field


class ProxyRequest(BaseModel):
    """API 프록시 요청 모델"""

    service_name: str = Field(..., description="서비스 이름 (예: steam)")
    endpoint_id: str = Field(..., description="엔드포인트 ID (예: get_popular_games)")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="API 호출 인자"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "steam",
                "endpoint_id": "get_popular_games",
                "arguments": {
                    "count": 5
                }
            }
        }

"""
응답 데이터 모델
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models.api_definition import APIDefinition


class APIListResponse(BaseModel):
    """API 목록 응답 모델"""

    total: int = Field(..., description="전체 API 개수")
    apis: List[APIDefinition] = Field(..., description="API 목록")


class APIDetailResponse(BaseModel):
    """API 상세 정보 응답 모델"""

    api: APIDefinition = Field(..., description="API 정의")


class ProxyResponse(BaseModel):
    """API 프록시 응답 모델"""

    success: bool = Field(..., description="성공 여부")
    data: Optional[Any] = Field(None, description="응답 데이터")
    error: Optional[str] = Field(None, description="에러 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "ranks": [
                        {
                            "rank": 1,
                            "appid": 730,
                            "concurrent_in_game": 1234567
                        }
                    ]
                },
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""

    status: str = Field(..., description="서비스 상태")
    version: str = Field(..., description="버전")
    loaded_apis: int = Field(..., description="로드된 API 개수")

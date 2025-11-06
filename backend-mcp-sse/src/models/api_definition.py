"""
API 정의 데이터 모델
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ParameterDefinition(BaseModel):
    """API 파라미터 정의"""

    type: str = Field(..., description="파라미터 타입 (string, integer, number, boolean)")
    description: str = Field(..., description="파라미터 설명")
    required: bool = Field(default=False, description="필수 여부")
    default: Optional[Any] = Field(None, description="기본값")
    min: Optional[float] = Field(None, description="최소값 (숫자 타입)")
    max: Optional[float] = Field(None, description="최대값 (숫자 타입)")
    enum: Optional[List[Any]] = Field(None, description="허용된 값 목록")


class ResponseMapping(BaseModel):
    """API 응답 매핑 정의"""

    path: Optional[str] = Field(None, description="JSONPath 경로 (예: $.response.data)")
    format: str = Field(default="json", description="응답 포맷 (json, text)")


class RateLimit(BaseModel):
    """Rate Limit 정의"""

    max_calls: int = Field(..., description="최대 호출 횟수")
    per_seconds: int = Field(..., description="기간(초)")


class APIEndpoint(BaseModel):
    """API 엔드포인트 정의"""

    id: str = Field(..., description="엔드포인트 고유 ID")
    name: str = Field(..., description="MCP Tool 이름")
    display_name: str = Field(..., description="사용자용 표시 이름")
    description: str = Field(..., description="기능 설명")
    http_method: str = Field(..., description="HTTP 메서드 (GET, POST, PUT, DELETE)")
    path: str = Field(..., description="API 경로")
    parameters: Dict[str, ParameterDefinition] = Field(
        default_factory=dict,
        description="파라미터 정의"
    )
    response_mapping: Optional[ResponseMapping] = Field(
        None,
        description="응답 매핑 규칙"
    )
    timeout_seconds: int = Field(default=10, description="타임아웃(초)")
    rate_limit: Optional[RateLimit] = Field(None, description="Rate Limit 설정")


class APIDefinition(BaseModel):
    """API 서비스 정의"""

    service_name: str = Field(..., description="서비스 고유 이름")
    display_name: str = Field(..., description="서비스 표시 이름")
    base_url: str = Field(..., description="API 베이스 URL")
    description: str = Field(..., description="서비스 설명")
    auth_required: bool = Field(default=False, description="인증 필요 여부")
    endpoints: List[APIEndpoint] = Field(
        default_factory=list,
        description="엔드포인트 목록"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "steam",
                "display_name": "Steam Web API",
                "base_url": "https://api.steampowered.com",
                "description": "Steam 게임 정보를 조회합니다",
                "auth_required": False,
                "endpoints": [
                    {
                        "id": "get_popular_games",
                        "name": "steam_get_popular_games",
                        "display_name": "Get Popular Games",
                        "description": "현재 인기있는 Steam 게임 목록을 조회합니다",
                        "http_method": "GET",
                        "path": "/ISteamChartsService/GetMostPlayedGames/v1/",
                        "parameters": {
                            "count": {
                                "type": "integer",
                                "description": "반환할 게임 개수",
                                "required": False,
                                "default": 10,
                                "min": 1,
                                "max": 100
                            }
                        },
                        "timeout_seconds": 10
                    }
                ]
            }
        }

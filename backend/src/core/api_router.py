"""
API 라우팅 및 호출 로직
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import aiohttp
from pydantic import ValidationError as PydanticValidationError

from core.config import settings
from core.security import check_security, SecurityError
from models.api_definition import APIDefinition, APIEndpoint
from utils.json_path import extract_json_path
from utils.logger import setup_logger
from utils.validators import validate_parameters, ValidationError

logger = setup_logger(__name__)


class APIRouter:
    """
    API 라우팅 및 호출 관리자
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Args:
            data_dir: API 정의 JSON 파일이 있는 디렉토리
        """
        self.data_dir = data_dir or settings.DATA_DIR
        self.apis: Dict[str, APIDefinition] = {}
        self.tool_map: Dict[str, Tuple[str, str]] = {}  # tool_name -> (service_name, endpoint_id)
        self.session: Optional[aiohttp.ClientSession] = None

    async def load_api_definitions(self) -> None:
        """
        JSON 파일에서 API 정의 로드
        """
        if not self.data_dir.exists():
            logger.warning(f"Data directory not found: {self.data_dir}")
            return

        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Pydantic 모델로 검증
                api_def = APIDefinition(**data)

                service_name = api_def.service_name
                self.apis[service_name] = api_def

                # Tool 이름 매핑 생성
                for endpoint in api_def.endpoints:
                    tool_name = endpoint.name
                    self.tool_map[tool_name] = (service_name, endpoint.id)

                logger.info(
                    f"Loaded API: {service_name} "
                    f"with {len(api_def.endpoints)} endpoints"
                )

            except (json.JSONDecodeError, PydanticValidationError) as e:
                logger.error(f"Failed to load {json_file}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading {json_file}: {e}")

    async def create_session(self) -> None:
        """HTTP 클라이언트 세션 생성"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.HTTP_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("HTTP session created")

    async def close_session(self) -> None:
        """HTTP 클라이언트 세션 종료"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("HTTP session closed")

    def get_api(self, service_name: str) -> Optional[APIDefinition]:
        """
        서비스 이름으로 API 정의 조회

        Args:
            service_name: 서비스 이름

        Returns:
            API 정의 또는 None
        """
        return self.apis.get(service_name)

    def get_endpoint(
        self,
        service_name: str,
        endpoint_id: str
    ) -> Optional[APIEndpoint]:
        """
        엔드포인트 조회

        Args:
            service_name: 서비스 이름
            endpoint_id: 엔드포인트 ID

        Returns:
            엔드포인트 정의 또는 None
        """
        api_def = self.apis.get(service_name)
        if not api_def:
            return None

        for endpoint in api_def.endpoints:
            if endpoint.id == endpoint_id:
                return endpoint

        return None

    async def route_request(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Tool 이름으로 적절한 API 호출

        Args:
            tool_name: MCP Tool 이름
            arguments: 호출 인자

        Returns:
            API 응답 데이터

        Raises:
            ValueError: Tool을 찾을 수 없거나 잘못된 인자
            SecurityError: 보안 검사 실패
            Exception: API 호출 실패
        """
        # Tool 찾기
        if tool_name not in self.tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        service_name, endpoint_id = self.tool_map[tool_name]
        api_def = self.apis[service_name]
        endpoint = self.get_endpoint(service_name, endpoint_id)

        if not endpoint:
            raise ValueError(f"Endpoint not found: {endpoint_id}")

        # API 호출
        return await self._call_api(api_def, endpoint, arguments)

    async def _call_api(
        self,
        api_def: APIDefinition,
        endpoint: APIEndpoint,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        실제 외부 API 호출

        Args:
            api_def: API 정의
            endpoint: 엔드포인트 정의
            arguments: 호출 인자

        Returns:
            API 응답 데이터
        """
        # URL 구성
        url = f"{api_def.base_url}{endpoint.path}"

        # 보안 검사
        try:
            check_security(url)
        except SecurityError as e:
            logger.error(f"Security check failed: {e}")
            raise

        # HTTP 메서드 확인
        method = endpoint.http_method.upper()

        # 파라미터 검증 및 기본값 적용
        params = {}
        try:
            validate_parameters(arguments, endpoint.parameters)
        except ValidationError as e:
            logger.error(f"Parameter validation failed: {e}")
            raise ValueError(str(e))

        # 파라미터 처리
        for param_name, param_def in endpoint.parameters.items():
            value = None
            if param_name in arguments:
                value = arguments[param_name]
            elif param_def.default is not None:
                value = param_def.default

            if value is not None:
                # GET 요청의 경우 boolean을 문자열로 변환
                if method == "GET" and isinstance(value, bool):
                    params[param_name] = "true" if value else "false"
                else:
                    params[param_name] = value

        # NewsAPI의 경우 서버 측 API 키 자동 추가
        from core.config import settings
        if api_def.service_name == "news" and settings.NEWSAPI_KEY:
            params["apiKey"] = settings.NEWSAPI_KEY

        # 세션 확인
        if not self.session or self.session.closed:
            await self.create_session()

        # 타임아웃 설정
        timeout = aiohttp.ClientTimeout(total=endpoint.timeout_seconds)

        # HTTP 요청
        try:
            logger.info(f"Calling API: {method} {url} with params: {params}")

            async with self.session.request(
                method=method,
                url=url,
                params=params if method == "GET" else None,
                json=params if method in ("POST", "PUT", "PATCH") else None,
                timeout=timeout
            ) as response:
                response.raise_for_status()
                data = await response.json()

                # 응답 매핑
                if endpoint.response_mapping and endpoint.response_mapping.path:
                    data = extract_json_path(data, endpoint.response_mapping.path)

                logger.info(f"API call successful: {endpoint.name}")
                return data

        except aiohttp.ClientResponseError as e:
            logger.error(f"API call failed: {endpoint.name}: HTTP {e.status}")
            raise Exception(f"API returned error: HTTP {e.status}")
        except aiohttp.ClientError as e:
            logger.error(f"API call failed: {endpoint.name}: {e}")
            raise Exception(f"API request failed: {str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"API call timeout: {endpoint.name}")
            raise Exception(
                f"API request timeout after {endpoint.timeout_seconds}s"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {endpoint.name}: {e}")
            raise


# asyncio import 추가
import asyncio

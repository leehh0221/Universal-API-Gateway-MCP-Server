# Part 2: Backend (stdio) - 핵심 MCP 기능

## 개요

Backend stdio 방식의 핵심 MCP 서버 기능을 구현하는 단계입니다. Pydantic 모델 정의, API Router, MCP 서버, Tool 핸들러를 구현합니다.

---

## Issue #4: Pydantic 모델 정의 (API Definition, Request, Response)

### 목표
API 정의, 요청, 응답을 위한 Pydantic 모델을 정의합니다.

### 작업 내용

#### 4.1 API Definition 모델
**파일**: `backend/src/models/api_definition.py`

**주요 모델**:
```python
class ParameterDefinition(BaseModel):
    """API 파라미터 정의"""
    type: str  # string, integer, number, boolean
    description: str
    required: bool = False
    default: Optional[Any] = None
    min: Optional[float] = None
    max: Optional[float] = None
    enum: Optional[List[Any]] = None

class ResponseMapping(BaseModel):
    """응답 매핑 규칙"""
    path: Optional[str] = None  # JSONPath
    format: str = "json"

class RateLimit(BaseModel):
    """Rate Limiting 설정"""
    max_calls: int
    per_seconds: int

class APIEndpoint(BaseModel):
    """API 엔드포인트 정의"""
    id: str
    name: str
    display_name: str
    description: str
    http_method: str
    path: str
    parameters: Dict[str, ParameterDefinition] = {}
    response_mapping: Optional[ResponseMapping] = None
    timeout_seconds: int = 10
    rate_limit: Optional[RateLimit] = None

class APIDefinition(BaseModel):
    """API 서비스 정의"""
    service_name: str
    display_name: str
    base_url: str
    description: str
    auth_required: bool = False
    endpoints: List[APIEndpoint] = []
```

**파일 경로**: `backend/src/models/api_definition.py`

#### 4.2 Request 모델
**파일**: `backend/src/models/requests.py`

```python
from pydantic import BaseModel
from typing import Dict, Any

class ProxyRequest(BaseModel):
    """API 프록시 요청"""
    service_name: str
    endpoint_id: str
    arguments: Dict[str, Any] = {}
```

#### 4.3 Response 모델
**파일**: `backend/src/models/responses.py`

```python
from pydantic import BaseModel
from typing import List, Optional, Any

class APIListResponse(BaseModel):
    """API 목록 응답"""
    total: int
    apis: List[APIDefinition]

class APIDetailResponse(BaseModel):
    """API 상세 정보 응답"""
    api: APIDefinition

class ProxyResponse(BaseModel):
    """프록시 호출 결과"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    status: str
    version: str
    loaded_apis: int
```

#### 4.4 __init__.py 파일
**파일**: `backend/src/models/__init__.py`

```python
from .api_definition import (
    APIDefinition,
    APIEndpoint,
    ParameterDefinition,
    ResponseMapping,
    RateLimit
)
from .requests import ProxyRequest
from .responses import (
    APIListResponse,
    APIDetailResponse,
    ProxyResponse,
    HealthResponse
)

__all__ = [
    "APIDefinition",
    "APIEndpoint",
    "ParameterDefinition",
    "ResponseMapping",
    "RateLimit",
    "ProxyRequest",
    "APIListResponse",
    "APIDetailResponse",
    "ProxyResponse",
    "HealthResponse"
]
```

### 브랜치
- **이름**: `feature/004_pydantic_models`
- **베이스**: `develop` (Issue #3 머지 후)

### 커밋 메시지
```
feat: Pydantic 모델 정의 추가

- API Definition 모델 추가 (APIDefinition, APIEndpoint, ParameterDefinition 등)
- Request 모델 추가 (ProxyRequest)
- Response 모델 추가 (APIListResponse, ProxyResponse, HealthResponse 등)
- models/__init__.py 추가

Closes #4
```

### PR 제목
```
feat: Pydantic 모델 정의 추가 (#4)
```

### 파일 목록
```
backend/src/models/__init__.py
backend/src/models/api_definition.py
backend/src/models/requests.py
backend/src/models/responses.py
```

---

## Issue #5: API Router 핵심 로직 구현

### 목표
API 정의를 로딩하고, 외부 API를 호출하는 핵심 라우팅 로직을 구현합니다.

### 작업 내용

#### 5.1 JSON Path 유틸리티 구현
**파일**: `backend/src/utils/json_path.py`

```python
def extract_json_path(data: Any, path: str) -> Any:
    """
    간단한 JSONPath 추출 ($.property.nested 형식)

    Examples:
        $.response.ranks
        $.current_weather
        $.articles
    """
    if not path or path == "$":
        return data

    # $ 제거 후 . 으로 분할
    parts = path.lstrip('$').lstrip('.').split('.')

    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None

    return current
```

#### 5.2 Parameter Validator 구현
**파일**: `backend/src/utils/validators.py`

```python
from typing import Dict, Any
from ..models.api_definition import ParameterDefinition

class ValidationError(Exception):
    pass

def validate_parameters(
    arguments: Dict[str, Any],
    parameter_defs: Dict[str, ParameterDefinition]
) -> None:
    """파라미터 검증"""

    # 필수 파라미터 체크
    for param_name, param_def in parameter_defs.items():
        if param_def.required and param_name not in arguments:
            raise ValidationError(f"Required parameter missing: {param_name}")

    # 타입 및 제약 조건 검증
    for param_name, value in arguments.items():
        if param_name not in parameter_defs:
            raise ValidationError(f"Unknown parameter: {param_name}")

        param_def = parameter_defs[param_name]

        # 타입 검증
        if param_def.type == "integer" and not isinstance(value, int):
            raise ValidationError(f"{param_name} must be integer")

        # Min/Max 검증
        if param_def.min is not None and value < param_def.min:
            raise ValidationError(f"{param_name} must be >= {param_def.min}")

        # Enum 검증
        if param_def.enum and value not in param_def.enum:
            raise ValidationError(f"{param_name} must be one of {param_def.enum}")
```

#### 5.3 API Router 구현
**파일**: `backend/src/core/api_router.py`

**주요 기능**:
- `load_api_definitions()`: JSON 파일에서 API 정의 로드
- `create_session()`: aiohttp ClientSession 생성
- `close_session()`: 세션 종료
- `route_request()`: MCP Tool 호출을 API 엔드포인트로 라우팅
- `_call_api()`: 실제 외부 API 호출

**핵심 코드**:
```python
import json
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..models.api_definition import APIDefinition, APIEndpoint
from ..utils.validators import validate_parameters
from ..utils.json_path import extract_json_path
from .security import check_security
from .config import settings

class APIRouter:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.apis: Dict[str, APIDefinition] = {}
        self.tool_map: Dict[str, tuple] = {}  # tool_name -> (service_name, endpoint_id)
        self.session: Optional[aiohttp.ClientSession] = None

    async def load_api_definitions(self) -> None:
        """data/apis/*.json 파일 로딩"""
        for json_file in self.data_dir.glob("*.json"):
            with open(json_file) as f:
                data = json.load(f)
                api_def = APIDefinition(**data)
                self.apis[api_def.service_name] = api_def

                # Tool 매핑 생성
                for endpoint in api_def.endpoints:
                    self.tool_map[endpoint.name] = (api_def.service_name, endpoint.id)

    async def create_session(self) -> None:
        """aiohttp 세션 생성"""
        self.session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        """세션 종료"""
        if self.session:
            await self.session.close()

    async def route_request(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """MCP Tool 호출을 API로 라우팅"""
        if tool_name not in self.tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        service_name, endpoint_id = self.tool_map[tool_name]
        api_def = self.apis[service_name]

        # 엔드포인트 찾기
        endpoint = next((ep for ep in api_def.endpoints if ep.id == endpoint_id), None)
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
        """실제 API 호출"""
        # URL 생성
        url = api_def.base_url + endpoint.path

        # 보안 검사
        check_security(url)

        # 파라미터 검증
        validate_parameters(arguments, endpoint.parameters)

        # API 키 자동 주입 (NewsAPI)
        if api_def.service_name == "news":
            if settings.NEWSAPI_KEY:
                arguments["apiKey"] = settings.NEWSAPI_KEY

        # HTTP 요청
        method = endpoint.http_method.upper()
        params = arguments if method == "GET" else {}
        json_data = arguments if method == "POST" else None

        async with self.session.request(
            method,
            url,
            params=params,
            json=json_data,
            timeout=aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
        ) as response:
            response.raise_for_status()
            result = await response.json()

            # Response Mapping
            if endpoint.response_mapping and endpoint.response_mapping.path:
                result = extract_json_path(result, endpoint.response_mapping.path)

            return result
```

### 브랜치
- **이름**: `feature/005_api_router`
- **베이스**: `develop` (Issue #4 머지 후)

### 커밋 메시지
```
feat: API Router 핵심 로직 구현

- JSONPath 유틸리티 추가
- Parameter Validator 추가
- API Router 구현 (API 로딩, 라우팅, 호출)
- aiohttp 기반 HTTP 클라이언트 구현

Closes #5
```

### PR 제목
```
feat: API Router 핵심 로직 구현 (#5)
```

### 파일 목록
```
backend/src/utils/json_path.py
backend/src/utils/validators.py
backend/src/core/api_router.py
```

---

## Issue #6: MCP stdio 서버 구현

### 목표
MCP SDK를 사용하여 stdio 방식의 MCP 서버를 구현합니다.

### 작업 내용

#### 6.1 MCP 서버 메인 구현
**파일**: `backend/src/mcp_server/server.py`

```python
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

from ..core.api_router import APIRouter
from ..core.config import settings
from ..utils.logger import setup_logger
from .handlers import MCPHandlers

logger = setup_logger(__name__)

class UniversalMCPServer:
    """Universal API Gateway MCP Server"""

    def __init__(self):
        self.server = Server("universal-api-gateway")
        self.api_router = APIRouter(data_dir=settings.DATA_DIR)
        self.handlers = None

    async def initialize(self):
        """서버 초기화"""
        logger.info("Initializing MCP server...")
        await self.api_router.load_api_definitions()
        await self.api_router.create_session()

        self.handlers = MCPHandlers(self.api_router)
        self._register_handlers()

        logger.info(f"Loaded {len(self.api_router.apis)} APIs")

    def _register_handlers(self):
        """핸들러 등록"""
        @self.server.list_tools()
        async def handle_list_tools():
            return await self.handlers.handle_list_tools()

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            return await self.handlers.handle_call_tool(name, arguments)

    async def run_stdio(self):
        """stdio 모드로 실행"""
        async with stdio_server() as (read_stream, write_stream):
            await self.initialize()
            logger.info("MCP stdio server ready")

            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

    async def cleanup(self):
        """리소스 정리"""
        logger.info("Cleaning up...")
        await self.api_router.close_session()
```

#### 6.2 CLI 엔트리 포인트
**파일**: `backend/src/mcp_server/__main__.py`

```python
import asyncio
from .server import UniversalMCPServer

def main():
    server = UniversalMCPServer()
    asyncio.run(server.run_stdio())

if __name__ == "__main__":
    main()
```

#### 6.3 __init__.py 파일
**파일**: `backend/src/mcp_server/__init__.py`

```python
from .server import UniversalMCPServer

__all__ = ["UniversalMCPServer"]
```

### 브랜치
- **이름**: `feature/006_mcp_stdio_server`
- **베이스**: `develop` (Issue #5 머지 후)

### 커밋 메시지
```
feat: MCP stdio 서버 구현

- UniversalMCPServer 클래스 구현
- stdio_server 컨텍스트 매니저 사용
- CLI 엔트리 포인트 추가 (__main__.py)
- 서버 초기화 및 정리 로직 구현

Closes #6
```

### PR 제목
```
feat: MCP stdio 서버 구현 (#6)
```

### 파일 목록
```
backend/src/mcp_server/__init__.py
backend/src/mcp_server/__main__.py
backend/src/mcp_server/server.py
```

---

## Issue #7: MCP Tool 생성 및 핸들러 구현

### 목표
API 정의로부터 MCP Tool을 생성하고, Tool 호출을 처리하는 핸들러를 구현합니다.

### 작업 내용

#### 7.1 Tool 생성 로직
**파일**: `backend/src/mcp_server/tools.py`

```python
from mcp.types import Tool
from typing import List

from ..models.api_definition import APIDefinition

def create_tools_from_apis(apis: List[APIDefinition]) -> List[Tool]:
    """API 정의로부터 MCP Tool 객체 생성"""
    tools = []

    for api in apis:
        for endpoint in api.endpoints:
            # JSON Schema 생성
            input_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }

            for param_name, param_def in endpoint.parameters.items():
                prop = {
                    "type": param_def.type,
                    "description": param_def.description
                }

                # 제약 조건 추가
                if param_def.min is not None:
                    prop["minimum"] = param_def.min
                if param_def.max is not None:
                    prop["maximum"] = param_def.max
                if param_def.enum is not None:
                    prop["enum"] = param_def.enum
                if param_def.default is not None:
                    prop["default"] = param_def.default

                input_schema["properties"][param_name] = prop

                if param_def.required:
                    input_schema["required"].append(param_name)

            # Tool 객체 생성
            tool = Tool(
                name=endpoint.name,
                description=f"[{api.display_name}] {endpoint.description}",
                inputSchema=input_schema
            )
            tools.append(tool)

    return tools
```

#### 7.2 MCP 핸들러 구현
**파일**: `backend/src/mcp_server/handlers.py`

```python
import json
from mcp.types import TextContent, Tool
from typing import List

from ..core.api_router import APIRouter
from .tools import create_tools_from_apis
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class MCPHandlers:
    """MCP 요청 핸들러"""

    def __init__(self, api_router: APIRouter):
        self.api_router = api_router

    async def handle_list_tools(self) -> List[Tool]:
        """사용 가능한 Tool 목록 반환"""
        logger.info("Listing tools...")

        apis = list(self.api_router.apis.values())
        tools = create_tools_from_apis(apis)

        logger.info(f"Returning {len(tools)} tools")
        return tools

    async def handle_call_tool(self, name: str, arguments: dict) -> List[TextContent]:
        """Tool 호출 처리"""
        logger.info(f"Calling tool: {name} with arguments: {arguments}")

        try:
            result = await self.api_router.route_request(
                tool_name=name,
                arguments=arguments
            )

            logger.info(f"Tool {name} succeeded")
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        except Exception as e:
            logger.error(f"Tool {name} failed: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, ensure_ascii=False)
            )]
```

### 브랜치
- **이름**: `feature/007_mcp_handlers`
- **베이스**: `develop` (Issue #6 머지 후)

### 커밋 메시지
```
feat: MCP Tool 생성 및 핸들러 구현

- create_tools_from_apis 함수 구현 (API -> Tool 변환)
- MCPHandlers 클래스 구현 (list_tools, call_tool)
- JSON Schema 기반 Tool 정의 생성
- 에러 핸들링 및 로깅 추가

Closes #7
```

### PR 제목
```
feat: MCP Tool 생성 및 핸들러 구현 (#7)
```

### 파일 목록
```
backend/src/mcp_server/tools.py
backend/src/mcp_server/handlers.py
```

---

## Part 2 요약

### 완료 항목
- ✅ Issue #4: Pydantic 모델 정의
- ✅ Issue #5: API Router 핵심 로직 구현
- ✅ Issue #6: MCP stdio 서버 구현
- ✅ Issue #7: MCP Tool 생성 및 핸들러 구현

### 총 PR 수
4개

### 다음 단계
Part 3로 이동하여 외부 API 통합 및 REST API를 구현합니다.

---

**작성일**: 2025-10-28
**파트**: Part 2 - Backend stdio 핵심 MCP 기능

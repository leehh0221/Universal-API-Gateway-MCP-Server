# Part 3: Backend (stdio) - API 통합 및 REST API

## 개요

외부 API 통합 (Steam, Weather, News)과 FastAPI 기반 REST API 엔드포인트를 구현하는 단계입니다.

---

## Issue #8: Steam API 통합

### 목표
Steam Web API를 통합하고 API 정의 JSON 파일을 작성합니다.

### 작업 내용

#### 8.1 Steam API 정의 파일 작성
**파일**: `backend/data/apis/steam.json`

```json
{
  "service_name": "steam",
  "display_name": "Steam Web API",
  "base_url": "https://api.steampowered.com",
  "description": "Steam 게임 정보 및 플레이어 통계를 조회합니다",
  "auth_required": false,
  "endpoints": [
    {
      "id": "get_popular_games",
      "name": "steam_get_popular_games",
      "display_name": "Get Popular Games",
      "description": "Get a list of the most played Steam games currently",
      "http_method": "GET",
      "path": "/ISteamChartsService/GetMostPlayedGames/v1/",
      "parameters": {
        "count": {
          "type": "integer",
          "description": "반환할 게임 개수 (1-100)",
          "required": false,
          "default": 10,
          "min": 1,
          "max": 100
        }
      },
      "response_mapping": {
        "path": "$.response.ranks",
        "format": "json"
      },
      "timeout_seconds": 10
    }
  ]
}
```

#### 8.2 테스트 (수동)
```bash
# MCP 서버 실행
cd backend/src
python -m mcp_server

# Claude Desktop에서 확인
# Tool: steam_get_popular_games
# Argument: {"count": 5}
```

### 브랜치
- **이름**: `feature/008_steam_api_integration`
- **베이스**: `develop` (Issue #7 머지 후)

### 커밋 메시지
```
feat: Steam API 통합

- Steam Web API 정의 파일 추가 (steam.json)
- get_popular_games 엔드포인트 추가
- 파라미터: count (1-100, default 10)
- Response mapping: $.response.ranks

Closes #8
```

### PR 제목
```
feat: Steam API 통합 (#8)
```

### PR 설명
```markdown
## 요약
Steam Web API를 통합하여 인기 게임 목록을 조회할 수 있습니다.

## 변경 사항
- [x] steam.json 추가
- [x] steam_get_popular_games Tool 정의

## API 상세
- **Endpoint**: GET /ISteamChartsService/GetMostPlayedGames/v1/
- **Parameters**:
  - count (optional): 반환할 게임 개수 (1-100, default: 10)
- **Response**: 인기 게임 순위 배열

## 테스트 방법
```bash
python -m src.mcp_server
```

Claude Desktop에서 `steam_get_popular_games` Tool 사용

Closes #8
```

### 파일 목록
```
backend/data/apis/steam.json
```

---

## Issue #9: Weather API 통합

### 목표
Open-Meteo Weather API를 통합하고 2개의 엔드포인트를 추가합니다.

### 작업 내용

#### 9.1 Weather API 정의 파일 작성
**파일**: `backend/data/apis/weather.json`

```json
{
  "service_name": "weather",
  "display_name": "Open-Meteo Weather API",
  "base_url": "https://api.open-meteo.com",
  "description": "전 세계 날씨 정보를 조회합니다 (인증 불필요)",
  "auth_required": false,
  "endpoints": [
    {
      "id": "get_current_weather",
      "name": "weather_get_current",
      "display_name": "Get Current Weather",
      "description": "Get current weather information for a specific location",
      "http_method": "GET",
      "path": "/v1/forecast",
      "parameters": {
        "latitude": {
          "type": "number",
          "description": "위도 (-90 ~ 90)",
          "required": true,
          "min": -90,
          "max": 90
        },
        "longitude": {
          "type": "number",
          "description": "경도 (-180 ~ 180)",
          "required": true,
          "min": -180,
          "max": 180
        },
        "current_weather": {
          "type": "boolean",
          "description": "현재 날씨 포함 여부",
          "required": false,
          "default": true
        },
        "temperature_unit": {
          "type": "string",
          "description": "온도 단위 (celsius 또는 fahrenheit)",
          "required": false,
          "default": "celsius",
          "enum": ["celsius", "fahrenheit"]
        }
      },
      "response_mapping": {
        "path": "$.current_weather",
        "format": "json"
      },
      "timeout_seconds": 5
    },
    {
      "id": "get_forecast",
      "name": "weather_get_forecast",
      "display_name": "Get Weather Forecast",
      "description": "Get weather forecast for a specific location (7 days)",
      "http_method": "GET",
      "path": "/v1/forecast",
      "parameters": {
        "latitude": {
          "type": "number",
          "description": "위도",
          "required": true,
          "min": -90,
          "max": 90
        },
        "longitude": {
          "type": "number",
          "description": "경도",
          "required": true,
          "min": -180,
          "max": 180
        },
        "daily": {
          "type": "string",
          "description": "일별 데이터 항목",
          "required": false,
          "default": "temperature_2m_max,temperature_2m_min,precipitation_sum"
        },
        "forecast_days": {
          "type": "integer",
          "description": "예보 일수",
          "required": false,
          "default": 7,
          "min": 1,
          "max": 16
        }
      },
      "response_mapping": {
        "path": "$.daily",
        "format": "json"
      },
      "timeout_seconds": 5
    }
  ]
}
```

### 브랜치
- **이름**: `feature/009_weather_api_integration`
- **베이스**: `develop` (Issue #8 머지 후)

### 커밋 메시지
```
feat: Weather API 통합

- Open-Meteo Weather API 정의 파일 추가 (weather.json)
- weather_get_current 엔드포인트 추가 (현재 날씨)
- weather_get_forecast 엔드포인트 추가 (7일 예보)
- 위도/경도 기반 날씨 조회

Closes #9
```

### PR 제목
```
feat: Weather API 통합 (#9)
```

### 파일 목록
```
backend/data/apis/weather.json
```

---

## Issue #10: NewsAPI 통합 및 서버 측 API 키 관리

### 목표
NewsAPI.org를 통합하고 서버 측에서 API 키를 자동 주입하는 로직을 추가합니다.

### 작업 내용

#### 10.1 NewsAPI 정의 파일 작성
**파일**: `backend/data/apis/news.json`

```json
{
  "service_name": "news",
  "display_name": "NewsAPI.org",
  "base_url": "https://newsapi.org",
  "description": "전 세계 뉴스 기사를 검색하고 조회합니다",
  "auth_required": true,
  "endpoints": [
    {
      "id": "get_top_headlines",
      "name": "news_get_top_headlines",
      "display_name": "Get Top Headlines",
      "description": "Get the latest top headlines. Filter by country code.",
      "http_method": "GET",
      "path": "/v2/top-headlines",
      "parameters": {
        "country": {
          "type": "string",
          "description": "2글자 ISO 3166-1 국가 코드",
          "required": false,
          "default": "us",
          "enum": ["us", "kr", "jp", "gb", "de", "fr", "cn", "in"]
        },
        "category": {
          "type": "string",
          "description": "뉴스 카테고리",
          "required": false,
          "enum": ["business", "entertainment", "general", "health", "science", "sports", "technology"]
        },
        "pageSize": {
          "type": "integer",
          "description": "페이지당 결과 수",
          "required": false,
          "default": 10,
          "min": 1,
          "max": 100
        },
        "page": {
          "type": "integer",
          "description": "페이지 번호",
          "required": false,
          "default": 1,
          "min": 1
        }
      },
      "response_mapping": {
        "path": "$.articles",
        "format": "json"
      },
      "timeout_seconds": 10
    },
    {
      "id": "search_everything",
      "name": "news_search_everything",
      "display_name": "Search Everything",
      "description": "Search all news articles by keyword",
      "http_method": "GET",
      "path": "/v2/everything",
      "parameters": {
        "q": {
          "type": "string",
          "description": "검색 키워드 또는 구문",
          "required": true
        },
        "searchIn": {
          "type": "string",
          "description": "검색 대상 (title, description, content)",
          "required": false,
          "default": "title,description"
        },
        "language": {
          "type": "string",
          "description": "언어 코드",
          "required": false,
          "default": "en",
          "enum": ["ar", "de", "en", "es", "fr", "he", "it", "nl", "no", "pt", "ru", "sv", "ud", "zh"]
        },
        "sortBy": {
          "type": "string",
          "description": "정렬 기준",
          "required": false,
          "default": "publishedAt",
          "enum": ["relevancy", "popularity", "publishedAt"]
        },
        "pageSize": {
          "type": "integer",
          "description": "페이지당 결과 수",
          "required": false,
          "default": 10,
          "min": 1,
          "max": 100
        }
      },
      "response_mapping": {
        "path": "$.articles",
        "format": "json"
      },
      "timeout_seconds": 10
    }
  ]
}
```

#### 10.2 API 키 자동 주입 로직 (이미 api_router.py에 구현됨)
**파일**: `backend/src/core/api_router.py` (수정 필요 없음, 확인만)

```python
# _call_api 메서드 내
if api_def.service_name == "news":
    if settings.NEWSAPI_KEY:
        arguments["apiKey"] = settings.NEWSAPI_KEY
```

#### 10.3 .env 파일 업데이트 (예시)
**파일**: `backend/.env` (gitignore 대상)

```bash
NEWSAPI_KEY=363a8439829948a78a7b76ff87898300
```

### 브랜치
- **이름**: `feature/010_news_api_integration`
- **베이스**: `develop` (Issue #9 머지 후)

### 커밋 메시지
```
feat: NewsAPI 통합 및 서버 측 API 키 관리

- NewsAPI 정의 파일 추가 (news.json)
- news_get_top_headlines 엔드포인트 추가
- news_search_everything 엔드포인트 추가
- 서버 측 API 키 자동 주입 로직 구현

Closes #10
```

### PR 제목
```
feat: NewsAPI 통합 및 서버 측 API 키 관리 (#10)
```

### 파일 목록
```
backend/data/apis/news.json
```

---

## Issue #11: FastAPI REST API 엔드포인트 구현

### 목표
Dashboard용 REST API 엔드포인트를 구현합니다.

### 작업 내용

#### 11.1 Service Layer 구현
**파일**: `backend/src/services/api_service.py`

```python
from typing import List
from ..core.api_router import APIRouter
from ..models.api_definition import APIDefinition, APIEndpoint

class APIService:
    def __init__(self, api_router: APIRouter):
        self.api_router = api_router

    async def get_all_apis(self) -> List[APIDefinition]:
        """모든 API 목록 반환"""
        return list(self.api_router.apis.values())

    async def get_api(self, service_name: str) -> APIDefinition:
        """특정 API 상세 정보"""
        if service_name not in self.api_router.apis:
            raise ValueError(f"API not found: {service_name}")
        return self.api_router.apis[service_name]

    async def get_endpoints(self, service_name: str) -> List[APIEndpoint]:
        """특정 API의 엔드포인트 목록"""
        api = await self.get_api(service_name)
        return api.endpoints
```

**파일**: `backend/src/services/proxy_service.py`

```python
from typing import Any
from ..core.api_router import APIRouter
from ..models.requests import ProxyRequest

class ProxyService:
    def __init__(self, api_router: APIRouter):
        self.api_router = api_router

    async def call_endpoint(self, request: ProxyRequest) -> Any:
        """API 엔드포인트 호출"""
        api_def = self.api_router.apis.get(request.service_name)
        if not api_def:
            raise ValueError(f"API not found: {request.service_name}")

        endpoint = next((ep for ep in api_def.endpoints if ep.id == request.endpoint_id), None)
        if not endpoint:
            raise ValueError(f"Endpoint not found: {request.endpoint_id}")

        return await self.api_router._call_api(api_def, endpoint, request.arguments)
```

#### 11.2 Dependency Injection
**파일**: `backend/src/api/dependencies.py`

```python
from typing import Annotated
from fastapi import Depends

from ..core.api_router import APIRouter
from ..services.api_service import APIService
from ..services.proxy_service import ProxyService

_api_router_instance: APIRouter = None

def set_api_router(api_router: APIRouter) -> None:
    global _api_router_instance
    _api_router_instance = api_router

def get_api_router() -> APIRouter:
    return _api_router_instance

def get_api_service(
    api_router: Annotated[APIRouter, Depends(get_api_router)]
) -> APIService:
    return APIService(api_router)

def get_proxy_service(
    api_router: Annotated[APIRouter, Depends(get_api_router)]
) -> ProxyService:
    return ProxyService(api_router)
```

#### 11.3 REST API 엔드포인트 구현
**파일**: `backend/src/api/endpoints/health.py`

```python
from fastapi import APIRouter, Depends
from typing import Annotated

from ...models.responses import HealthResponse
from ...core.config import settings
from ..dependencies import get_api_router
from ...core.api_router import APIRouter as CoreAPIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthResponse)
async def health_check(
    api_router: Annotated[CoreAPIRouter, Depends(get_api_router)]
):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        loaded_apis=len(api_router.apis)
    )
```

**파일**: `backend/src/api/endpoints/apis.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from ...models.responses import APIListResponse, APIDetailResponse
from ...services.api_service import APIService
from ..dependencies import get_api_service

router = APIRouter(prefix="/apis", tags=["apis"])

@router.get("", response_model=APIListResponse)
async def list_apis(
    service: Annotated[APIService, Depends(get_api_service)]
):
    """List all available APIs"""
    apis = await service.get_all_apis()
    return APIListResponse(total=len(apis), apis=apis)

@router.get("/{service_name}", response_model=APIDetailResponse)
async def get_api(
    service_name: str,
    service: Annotated[APIService, Depends(get_api_service)]
):
    """Get API details"""
    try:
        api = await service.get_api(service_name)
        return APIDetailResponse(api=api)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{service_name}/endpoints")
async def get_endpoints(
    service_name: str,
    service: Annotated[APIService, Depends(get_api_service)]
):
    """Get API endpoints"""
    try:
        endpoints = await service.get_endpoints(service_name)
        return endpoints
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**파일**: `backend/src/api/endpoints/proxy.py`

```python
from fastapi import APIRouter, Depends
from typing import Annotated

from ...models.requests import ProxyRequest
from ...models.responses import ProxyResponse
from ...services.proxy_service import ProxyService
from ..dependencies import get_proxy_service

router = APIRouter(prefix="/proxy", tags=["proxy"])

@router.post("/test", response_model=ProxyResponse)
async def test_endpoint(
    request: ProxyRequest,
    service: Annotated[ProxyService, Depends(get_proxy_service)]
):
    """Test API endpoint"""
    try:
        data = await service.call_endpoint(request)
        return ProxyResponse(success=True, data=data)
    except Exception as e:
        return ProxyResponse(success=False, error=str(e))
```

#### 11.4 Router 구성
**파일**: `backend/src/api/router.py`

```python
from fastapi import APIRouter

from .endpoints import health, apis, proxy

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(apis.router)
api_router.include_router(proxy.router)
```

#### 11.5 __init__.py 파일
**파일**: `backend/src/api/__init__.py`
**파일**: `backend/src/services/__init__.py`

### 브랜치
- **이름**: `feature/011_fastapi_rest_api`
- **베이스**: `develop` (Issue #10 머지 후)

### 커밋 메시지
```
feat: FastAPI REST API 엔드포인트 구현

- Service Layer 추가 (APIService, ProxyService)
- Dependency Injection 시스템 구현
- REST API 엔드포인트 추가:
  - GET /api/v1/health
  - GET /api/v1/apis
  - GET /api/v1/apis/{service_name}
  - GET /api/v1/apis/{service_name}/endpoints
  - POST /api/v1/proxy/test

Closes #11
```

### PR 제목
```
feat: FastAPI REST API 엔드포인트 구현 (#11)
```

### 파일 목록
```
backend/src/services/__init__.py
backend/src/services/api_service.py
backend/src/services/proxy_service.py
backend/src/api/__init__.py
backend/src/api/dependencies.py
backend/src/api/router.py
backend/src/api/endpoints/health.py
backend/src/api/endpoints/apis.py
backend/src/api/endpoints/proxy.py
```

---

## Issue #12: MCP SSE 전송 계층 및 FastAPI 메인 앱 구현

### 목표
MCP SSE 전송 계층을 구현하고 FastAPI 메인 애플리케이션을 완성합니다.

### 작업 내용

#### 12.1 SSE Transport 구현
**파일**: `backend/src/mcp_server/sse_transport.py`

```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response

from .server import UniversalMCPServer
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

sse_transport = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> Response:
    """SSE 연결 핸들러"""
    logger.info("New SSE connection")

    mcp_server = UniversalMCPServer()
    await mcp_server.initialize()

    try:
        async with sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send
        ) as streams:
            await mcp_server.server.run(
                streams[0],
                streams[1],
                mcp_server.server.create_initialization_options()
            )
    finally:
        await mcp_server.cleanup()
        logger.info("SSE connection closed")

    return Response()

mcp_sse_app = Starlette(routes=[
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Mount("/messages/", app=sse_transport.handle_post_message),
])
```

#### 12.2 FastAPI 메인 앱 구현
**파일**: `backend/src/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.api_router import APIRouter
from .api.router import api_router
from .api.dependencies import set_api_router
from .mcp_server.sse_transport import mcp_sse_app
from .utils.logger import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    logger.info("Starting Universal API Gateway...")

    # APIRouter 초기화
    api_router_instance = APIRouter(data_dir=settings.DATA_DIR)
    await api_router_instance.load_api_definitions()
    await api_router_instance.create_session()

    set_api_router(api_router_instance)

    logger.info(f"Loaded {len(api_router_instance.apis)} APIs")
    logger.info(f"Server ready on {settings.HOST}:{settings.PORT}")

    yield

    # 정리
    logger.info("Shutting down...")
    await api_router_instance.close_session()

app = FastAPI(
    title=settings.APP_NAME,
    description="Universal API Gateway with MCP support",
    version=settings.VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+"
)

# REST API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# MCP SSE 앱 마운트
app.mount("/mcp", mcp_sse_app)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Universal API Gateway",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "mcp_sse": "/mcp/sse"
    }
```

#### 12.3 README 업데이트
**파일**: `backend/README.md`

```markdown
# Universal API Gateway - Backend

MCP (Model Context Protocol) 기반 API 게이트웨이 백엔드

## 기능

- **MCP stdio 서버**: Claude Desktop 로컬 연동
- **MCP SSE 서버**: HTTP/SSE 기반 원격 연동
- **REST API**: 대시보드용 API

## 시작하기

### 설치

```bash
pip install -r requirements.txt
```

### 환경 변수 설정

`.env` 파일 생성:
```bash
NEWSAPI_KEY=your_api_key_here
```

### 실행

#### FastAPI 서버 (REST API + MCP SSE)
```bash
cd src
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### MCP stdio 서버 (Claude Desktop용)
```bash
cd src
python -m mcp_server
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## MCP SSE 엔드포인트

- http://localhost:8000/mcp/sse
```

### 브랜치
- **이름**: `feature/012_mcp_sse_and_main_app`
- **베이스**: `develop` (Issue #11 머지 후)

### 커밋 메시지
```
feat: MCP SSE 전송 계층 및 FastAPI 메인 앱 구현

- SSE Transport 구현 (sse_transport.py)
- FastAPI 메인 앱 구현 (main.py)
- Lifespan 이벤트 핸들러 추가
- CORS 미들웨어 설정
- MCP SSE 앱 마운트
- README 업데이트

Closes #12
```

### PR 제목
```
feat: MCP SSE 전송 계층 및 FastAPI 메인 앱 구현 (#12)
```

### 파일 목록
```
backend/src/main.py
backend/src/mcp_server/sse_transport.py
backend/README.md
```

---

## Part 3 요약

### 완료 항목
- ✅ Issue #8: Steam API 통합
- ✅ Issue #9: Weather API 통합
- ✅ Issue #10: NewsAPI 통합 및 서버 측 API 키 관리
- ✅ Issue #11: FastAPI REST API 엔드포인트 구현
- ✅ Issue #12: MCP SSE 전송 계층 및 FastAPI 메인 앱 구현

### 총 PR 수
5개

### 다음 단계
Part 4로 이동하여 Backend-MCP-SSE 구현을 진행합니다.

---

**작성일**: 2025-10-28
**파트**: Part 3 - Backend API 통합 및 REST API

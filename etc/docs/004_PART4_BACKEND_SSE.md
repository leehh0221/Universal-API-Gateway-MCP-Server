# Part 4: Backend-MCP-SSE - HTTP/SSE 서버

## 개요

Backend-MCP-SSE는 HTTP/SSE 방식의 MCP 서버로, Backend stdio의 코드를 재사용하되 아키텍처를 개선한 버전입니다.

---

## Issue #13: Backend-MCP-SSE 프로젝트 설정

### 목표
Backend-MCP-SSE 프로젝트의 기본 구조와 의존성을 설정합니다.

### 작업 내용

#### 13.1 requirements.txt 작성
**파일**: `backend-mcp-sse/requirements.txt`

```txt
# MCP Protocol
mcp==1.1.2

# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.32.1

# HTTP Client
aiohttp==3.10.0

# Data Validation
pydantic==2.9.0
pydantic-settings==2.5.2

# JSONPath (installed but not used yet)
jsonpath-ng==1.6.1

# Utilities
python-dotenv==1.0.1
```

#### 13.2 .env.example 작성
**파일**: `backend-mcp-sse/.env.example`

```bash
# Server
HOST=0.0.0.0
PORT=8080
DEBUG=true
LOG_LEVEL=info

# API Keys
NEWSAPI_KEY=your_api_key_here

# Data
DATA_DIR=./data/apis

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

#### 13.3 디렉토리 구조 생성
```
backend-mcp-sse/
├── src/
│   ├── api/
│   ├── core/
│   ├── mcp_module/
│   ├── models/
│   ├── services/
│   └── utils/
└── data/
    └── apis/
```

#### 13.4 Backend에서 공통 파일 복사
다음 파일들을 backend에서 backend-mcp-sse로 복사:
- `src/core/config.py` (PORT를 8080으로 수정)
- `src/core/security.py`
- `src/utils/logger.py`
- `src/utils/validators.py`
- `src/utils/json_path.py`
- `src/models/api_definition.py`
- `src/models/requests.py`
- `src/models/responses.py`
- `data/apis/steam.json`
- `data/apis/weather.json`
- `data/apis/news.json`

**수정 사항**:
- `config.py`의 `PORT: int = 8080` (backend는 8000)

### 브랜치
- **이름**: `feature/013_backend_sse_setup`
- **베이스**: `develop` (Issue #12 머지 후)

### 커밋 메시지
```
feat: Backend-MCP-SSE 프로젝트 설정

- requirements.txt 추가
- .env.example 추가
- 디렉토리 구조 생성
- Backend에서 공통 파일 복사 (core, utils, models, data)
- PORT를 8080으로 변경

Closes #13
```

### PR 제목
```
feat: Backend-MCP-SSE 프로젝트 설정 (#13)
```

### 파일 목록
```
backend-mcp-sse/requirements.txt
backend-mcp-sse/.env.example
backend-mcp-sse/src/core/config.py
backend-mcp-sse/src/core/security.py
backend-mcp-sse/src/utils/logger.py
backend-mcp-sse/src/utils/validators.py
backend-mcp-sse/src/utils/json_path.py
backend-mcp-sse/src/models/api_definition.py
backend-mcp-sse/src/models/requests.py
backend-mcp-sse/src/models/responses.py
backend-mcp-sse/data/apis/steam.json
backend-mcp-sse/data/apis/weather.json
backend-mcp-sse/data/apis/news.json
```

---

## Issue #14: Backend-MCP-SSE MCP 서버 구현

### 목표
Backend-MCP-SSE의 MCP 서버를 구현합니다. Backend stdio와 달리 APIRouter를 생성자에서 받아 재사용합니다.

### 작업 내용

#### 14.1 API Router 복사
**파일**: `backend-mcp-sse/src/core/api_router.py`

Backend의 `src/core/api_router.py`를 그대로 복사합니다.

#### 14.2 MCP Handlers 및 Tools 복사
**파일**: `backend-mcp-sse/src/mcp_module/handlers.py`
**파일**: `backend-mcp-sse/src/mcp_module/tools.py`

Backend의 `src/mcp_server/handlers.py`와 `tools.py`를 복사합니다.

#### 14.3 MCP 서버 구현 (개선된 버전)
**파일**: `backend-mcp-sse/src/mcp_module/mcp_server.py`

```python
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response

from ..core.api_router import APIRouter
from .handlers import MCPHandlers
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class UniversalMCPServer:
    """Universal MCP Server (SSE)"""

    def __init__(self, api_router: APIRouter):
        self.server = Server("universal-api-gateway")
        self.api_router = api_router
        self.handlers = MCPHandlers(self.api_router)
        self._register_handlers()

    def _register_handlers(self):
        """핸들러 등록"""
        @self.server.list_tools()
        async def handle_list_tools():
            return await self.handlers.handle_list_tools()

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            return await self.handlers.handle_call_tool(name, arguments)

def create_mcp_sse_app(api_router: APIRouter):
    """MCP SSE 앱 생성"""
    sse_transport = SseServerTransport("/mcp/messages/")

    async def handle_sse(request: Request) -> Response:
        """SSE 연결 핸들러"""
        logger.info("New MCP SSE connection")

        mcp_server = UniversalMCPServer(api_router)

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
            logger.info("MCP SSE connection closed")

        return Response()

    return Starlette(routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ])
```

**주요 차이점**:
- `UniversalMCPServer`가 `api_router`를 생성자에서 받음 (재사용)
- `create_mcp_sse_app()` 함수로 Starlette 앱 생성
- Backend stdio에서는 매 연결마다 api_router를 새로 생성했지만, 여기서는 전역 인스턴스 재사용

### 브랜치
- **이름**: `feature/014_backend_sse_mcp_server`
- **베이스**: `develop` (Issue #13 머지 후)

### 커밋 메시지
```
feat: Backend-MCP-SSE MCP 서버 구현

- API Router 복사
- MCP Handlers 및 Tools 복사
- 개선된 MCP 서버 구현 (api_router 재사용 방식)
- create_mcp_sse_app 함수 추가

Closes #14
```

### PR 제목
```
feat: Backend-MCP-SSE MCP 서버 구현 (#14)
```

### 파일 목록
```
backend-mcp-sse/src/core/api_router.py
backend-mcp-sse/src/mcp_module/handlers.py
backend-mcp-sse/src/mcp_module/tools.py
backend-mcp-sse/src/mcp_module/mcp_server.py
```

---

## Issue #15: Backend-MCP-SSE REST API 및 통합

### 목표
REST API와 MCP SSE를 통합한 FastAPI 메인 앱을 완성합니다.

### 작업 내용

#### 15.1 Services 복사
**파일**: `backend-mcp-sse/src/services/api_service.py`
**파일**: `backend-mcp-sse/src/services/proxy_service.py`

Backend의 서비스 레이어를 그대로 복사합니다.

#### 15.2 API 엔드포인트 복사
**파일**: `backend-mcp-sse/src/api/dependencies.py`
**파일**: `backend-mcp-sse/src/api/router.py`
**파일**: `backend-mcp-sse/src/api/endpoints/health.py`
**파일**: `backend-mcp-sse/src/api/endpoints/apis.py`
**파일**: `backend-mcp-sse/src/api/endpoints/proxy.py`

Backend의 API 엔드포인트를 그대로 복사합니다.

#### 15.3 메인 앱 구현
**파일**: `backend-mcp-sse/src/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.api_router import APIRouter
from .api.router import api_router
from .api.dependencies import set_api_router
from .mcp_module.mcp_server import create_mcp_sse_app
from .utils.logger import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클"""
    logger.info("Starting Backend-MCP-SSE...")

    # APIRouter 초기화
    api_router_instance = APIRouter(data_dir=settings.DATA_DIR)
    await api_router_instance.load_api_definitions()
    await api_router_instance.create_session()

    set_api_router(api_router_instance)

    # MCP SSE 앱 생성 (APIRouter 전달)
    mcp_sse_app = create_mcp_sse_app(api_router_instance)
    app.mount("/mcp", mcp_sse_app)

    logger.info(f"Loaded {len(api_router_instance.apis)} APIs")
    logger.info(f"Server ready on {settings.HOST}:{settings.PORT}")
    logger.info(f"MCP SSE endpoint: http://{settings.HOST}:{settings.PORT}/mcp/sse")

    yield

    # 정리
    logger.info("Shutting down...")
    await api_router_instance.close_session()

app = FastAPI(
    title=settings.APP_NAME,
    description="Universal API Gateway with HTTP/SSE MCP Server",
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

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Universal API Gateway - HTTP/SSE MCP Server",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "mcp_sse": "/mcp/sse"
    }
```

**주요 차이점**:
- `lifespan`에서 `create_mcp_sse_app(api_router_instance)` 호출
- MCP 앱을 동적으로 마운트
- PORT가 8080

### 브랜치
- **이름**: `feature/015_backend_sse_rest_api`
- **베이스**: `develop` (Issue #14 머지 후)

### 커밋 메시지
```
feat: Backend-MCP-SSE REST API 및 통합

- Services 복사
- API 엔드포인트 복사
- FastAPI 메인 앱 구현 (HTTP/SSE 통합)
- PORT 8080으로 실행

Closes #15
```

### PR 제목
```
feat: Backend-MCP-SSE REST API 및 통합 (#15)
```

### 파일 목록
```
backend-mcp-sse/src/services/api_service.py
backend-mcp-sse/src/services/proxy_service.py
backend-mcp-sse/src/api/dependencies.py
backend-mcp-sse/src/api/router.py
backend-mcp-sse/src/api/endpoints/health.py
backend-mcp-sse/src/api/endpoints/apis.py
backend-mcp-sse/src/api/endpoints/proxy.py
backend-mcp-sse/src/main.py
```

---

## Part 4 요약

### 완료 항목
- ✅ Issue #13: Backend-MCP-SSE 프로젝트 설정
- ✅ Issue #14: Backend-MCP-SSE MCP 서버 구현
- ✅ Issue #15: Backend-MCP-SSE REST API 및 통합

### 총 PR 수
3개

### Backend vs Backend-MCP-SSE 차이점 요약

| 항목 | Backend (stdio) | Backend-MCP-SSE (HTTP/SSE) |
|------|-----------------|----------------------------|
| **포트** | 8000 | 8080 |
| **MCP 전송** | stdio + SSE (모듈 레벨) | SSE (통합) |
| **APIRouter** | 매 연결마다 생성 | 전역 인스턴스 재사용 |
| **아키텍처** | stdio 우선, SSE 추가 | HTTP/SSE 우선, 통합 설계 |

### 다음 단계
Part 5로 이동하여 Frontend를 구현합니다.

---

**작성일**: 2025-10-28
**파트**: Part 4 - Backend-MCP-SSE 구현

# MCP SSE 네이티브 구현 계획서

## 문서 정보
- **작성일**: 2025-10-27
- **목적**: MCP 서버를 stdio 방식에서 HTTP/SSE 네이티브 방식으로 전환하여 외부 배포 지원
- **구현 방식**: MCP 공식 표준 (SSE Transport)

---

## 1. 개요

### 1.1 현재 상태
- **MCP 서버**: stdio 방식으로만 구현 (로컬 전용)
- **FastAPI 서버**: REST API만 제공
- **문제점**: 원격에서 MCP 서버 사용 불가

### 1.2 목표
- MCP 서버를 HTTP/SSE 네이티브 방식으로 전환
- FastAPI와 MCP 서버를 하나의 통합 서버로 구성
- 로컬 및 원격 환경 모두에서 사용 가능

### 1.3 아키텍처 변경

#### 현재 구조
```
┌─────────────────┐         ┌──────────────────┐
│ Claude Desktop  │ stdio   │  MCP Server      │
│  (로컬 PC)      │◄────── ──┤  (server.py)     │
└─────────────────┘         └──────────────────┘

별도 존재:
┌─────────────────┐  HTTP   ┌──────────────────┐
│   React 앱      │◄────────┤  FastAPI         │
└─────────────────┘         └──────────────────┘
```

#### 변경 후 구조
```
┌─────────────────┐         ┌────────────────────────────────┐
│ Claude Desktop  │  HTTP   │  통합 서버 (Uvicorn)           │
│  (어디서나)     │◄────────┤  - FastAPI (REST API)          │
│                 │   SSE   │  - MCP Server (SSE)            │
│                 │         │  - 공통 APIRouter              │
└─────────────────┘         └────────────────────────────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │  외부 API들      │
                                │ Steam/Weather/   │
                                │ News             │
                                └──────────────────┘

┌─────────────────┐  HTTP
│   React 앱      │◄────────┐
└─────────────────┘         │
                            (동일 서버)
```

---

## 2. 구현 계획

### 2.1 필요한 패키지 추가

**requirements.txt 업데이트**:
```txt
# 기존 패키지들...
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
pydantic-settings==2.6.0
aiohttp==3.10.0
mcp==1.1.2

# 추가 패키지
starlette==0.41.0  # SSE 지원 (FastAPI에 포함되어 있지만 명시)
```

### 2.2 파일 수정 목록

#### 수정할 파일
1. `backend/src/mcp_server/server.py` - MCP 서버 핵심 로직 수정
2. `backend/src/main.py` - FastAPI 앱에 MCP SSE 통합
3. `backend/requirements.txt` - 필요시 패키지 추가

#### 새로 생성할 파일
1. `backend/src/mcp_server/sse_transport.py` - SSE 전송 계층 구현

---

## 3. 상세 구현 내용

### 3.1 MCP SSE 전송 계층 구현

**파일**: `backend/src/mcp_server/sse_transport.py`

```python
"""
MCP SSE 전송 계층
"""
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.sse import SseServerTransport

from mcp_server.server import UniversalMCPServer
from utils.logger import setup_logger

logger = setup_logger(__name__)


# SSE 전송 생성
sse_transport = SseServerTransport("/messages/")


async def handle_sse(request: Request) -> Response:
    """SSE 연결 핸들러"""
    logger.info("SSE connection established")

    # MCP 서버 인스턴스 생성
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

    return Response()


async def handle_post_message(request: Request) -> Response:
    """POST 메시지 핸들러"""
    return await sse_transport.handle_post_message(request)


# Starlette 라우트 정의
sse_routes = [
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/messages/{message_id}", endpoint=handle_post_message, methods=["POST"]),
]


# MCP SSE 앱 생성
mcp_sse_app = Starlette(routes=sse_routes)
```

**주요 기능**:
- `SseServerTransport`: MCP 공식 SSE 전송 계층
- `/sse`: Claude Desktop이 연결하는 엔드포인트
- `/messages/{message_id}`: 양방향 메시지 전송용

---

### 3.2 MCP 서버 수정

**파일**: `backend/src/mcp_server/server.py`

**수정 내용**:
```python
# 기존 코드 유지, 다음 메서드만 수정

class UniversalMCPServer:
    """Universal API Gateway MCP Server"""

    def __init__(self):
        self.server = Server("universal-api-gateway")
        self.api_router = APIRouter(data_dir=settings.DATA_DIR)
        self.handlers = None

    async def initialize(self):
        """서버 초기화 (기존과 동일)"""
        logger.info("Initializing MCP server...")
        await self.api_router.load_api_definitions()
        await self.api_router.create_session()
        logger.info(f"Loaded {len(self.api_router.apis)} APIs")

        self.handlers = MCPHandlers(self.api_router)
        self._register_handlers()
        logger.info("MCP server initialized")

    def _register_handlers(self):
        """MCP 요청 핸들러 등록 (기존과 동일)"""
        @self.server.list_tools()
        async def list_tools():
            return await self.handlers.handle_list_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            return await self.handlers.handle_call_tool(name, arguments)

    async def cleanup(self):
        """리소스 정리 (기존과 동일)"""
        logger.info("Cleaning up...")
        await self.api_router.close_session()

    # run() 메서드는 SSE 방식에서는 사용하지 않음
    # stdio 방식 지원이 필요하면 유지, 아니면 제거 가능


# main() 함수는 제거 (더 이상 독립 실행하지 않음)
```

**변경 사항**:
- `run()` 메서드: SSE에서는 사용 안 함 (선택적으로 제거)
- `main()` 함수: 제거 (FastAPI와 통합되므로)
- 나머지 핵심 로직은 모두 유지

---

### 3.3 FastAPI 통합

**파일**: `backend/src/main.py`

**수정 내용**:
```python
"""
FastAPI 애플리케이션 진입점
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import set_api_router
from api.router import api_router
from core.api_router import APIRouter
from core.config import settings
from utils.logger import setup_logger

# MCP SSE 앱 임포트 추가
from mcp_server.sse_transport import mcp_sse_app

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("Starting Universal API Gateway...")

    # APIRouter 인스턴스 생성 및 초기화
    api_router_instance = APIRouter(data_dir=settings.DATA_DIR)
    await api_router_instance.load_api_definitions()
    await api_router_instance.create_session()

    set_api_router(api_router_instance)

    logger.info(f"Loaded {len(api_router_instance.apis)} APIs")
    logger.info(f"Server ready on {settings.HOST}:{settings.PORT}")
    logger.info(f"MCP SSE endpoint: http://{settings.HOST}:{settings.PORT}/mcp/sse")

    yield

    logger.info("Shutting down...")
    await api_router_instance.close_session()


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="단일 MCP 서버로 여러 외부 API를 사용하는 Universal API Gateway",
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

# MCP SSE 앱 마운트 (추가)
app.mount("/mcp", mcp_sse_app)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "mcp_sse": "/mcp/sse"  # 추가
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

**변경 사항**:
- `from mcp_server.sse_transport import mcp_sse_app` 추가
- `app.mount("/mcp", mcp_sse_app)` 추가
- 루트 엔드포인트에 MCP SSE 정보 추가

---

## 4. 배포 및 사용 방법

### 4.1 로컬 테스트

```bash
# 1. 백엔드 디렉토리로 이동
cd backend

# 2. 가상환경 활성화
venv\Scripts\activate

# 3. 의존성 설치 (필요시)
pip install -r requirements.txt

# 4. 서버 실행
cd src
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**접근 URL**:
- REST API: http://localhost:8000/api/v1/
- MCP SSE: http://localhost:8000/mcp/sse
- API 문서: http://localhost:8000/docs

### 4.2 Claude Desktop 설정 (로컬)

**위치**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "universal-api-gateway": {
      "url": "http://localhost:8000/mcp/sse"
    }
  }
}
```

### 4.3 외부 배포 (예: AWS, Azure, Railway 등)

#### 배포 단계

1. **환경 변수 설정**:
   ```bash
   NEWSAPI_KEY=your_api_key_here
   HOST=0.0.0.0
   PORT=8000
   ```

2. **서버 실행 명령**:
   ```bash
   cd backend/src
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Claude Desktop 설정** (원격):
   ```json
   {
     "mcpServers": {
       "universal-api-gateway": {
         "url": "https://your-domain.com/mcp/sse",
         "headers": {
           "Authorization": "Bearer your-api-key"
         }
       }
     }
   }
   ```

#### 보안 고려사항

1. **API 키 인증 추가** (추후 구현):
   - FastAPI Dependency로 헤더 검증
   - MCP SSE 엔드포인트에 미들웨어 추가

2. **HTTPS 필수**:
   - 프로덕션 환경에서는 반드시 HTTPS 사용
   - 리버스 프록시 (Nginx, Caddy) 또는 클라우드 로드밸런서 사용

3. **CORS 설정 검토**:
   - 프로덕션에서는 특정 도메인만 허용

---

## 5. 테스트 계획

### 5.1 기능 테스트

1. **MCP SSE 연결 테스트**:
   ```bash
   curl -N http://localhost:8000/mcp/sse
   ```
   - SSE 스트림이 열리는지 확인

2. **도구 목록 조회**:
   - Claude Desktop에서 연결 후
   - 5개 도구가 표시되는지 확인 (Steam, Weather x2, News x2)

3. **도구 호출 테스트**:
   - "서울 날씨 알려줘" → weather__get_current_weather 호출
   - "한국 뉴스 알려줘" → news__get_top_headlines 호출

### 5.2 성능 테스트

1. 동시 연결 수 테스트
2. 응답 시간 측정
3. 메모리 사용량 모니터링

### 5.3 호환성 테스트

1. Claude Desktop (Windows, macOS)
2. 다른 MCP 클라이언트들

---

## 6. 롤백 계획

### 6.1 기존 stdio 방식 유지 옵션

필요시 `server.py`에 다음 코드 유지:

```python
async def run_stdio(self):
    """stdio 방식 실행 (로컬 전용)"""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await self.initialize()
            logger.info("MCP server running (stdio)...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"MCP server error: {e}", exc_info=True)
        raise
    finally:
        await self.cleanup()
```

별도 스크립트로 실행:
```bash
python src/mcp_server/server.py
```

### 6.2 Git 브랜치 전략

1. 현재 브랜치: `develop`
2. 작업 브랜치: `feature/mcp-sse-implementation`
3. 테스트 완료 후: `develop`에 머지
4. 문제 발생 시: 브랜치 롤백

---

## 7. 구현 일정

### Phase 1: 기본 구현 (1일)
- [ ] SSE 전송 계층 구현
- [ ] MCP 서버 수정
- [ ] FastAPI 통합

### Phase 2: 테스트 (0.5일)
- [ ] 로컬 테스트
- [ ] Claude Desktop 연결 테스트
- [ ] 기능 테스트

### Phase 3: 문서화 (0.5일)
- [ ] README 업데이트
- [ ] 배포 가이드 작성
- [ ] API 문서 업데이트

---

## 8. 참고 자료

### MCP 공식 문서
- MCP Specification: https://modelcontextprotocol.io/docs/concepts/transports
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- SSE Transport: https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/sse.py

### 관련 예제
- FastAPI + MCP SSE: https://www.ragie.ai/blog/building-a-server-sent-events-sse-mcp-server-with-fastapi
- Cloudflare Workers: https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/

---

## 9. 예상 문제 및 해결 방안

### 문제 1: SSE 연결이 끊어짐
**해결**:
- Keep-alive 설정
- 타임아웃 조정
- 재연결 로직 구현

### 문제 2: APIRouter 인스턴스 공유 문제
**해결**:
- FastAPI의 dependency injection 활용
- 싱글톤 패턴 적용

### 문제 3: 동시 요청 처리
**해결**:
- 비동기 처리 최적화
- aiohttp 세션 풀링
- 연결 제한 설정

---

## 10. 결론

이 계획서에 따라 MCP 서버를 SSE 네이티브 방식으로 전환하면:

✅ **장점**:
- 로컬 및 원격 환경 모두 지원
- MCP 표준 준수
- FastAPI와 통합된 단일 서버
- 확장성 및 유지보수성 향상

✅ **최소 변경**:
- 기존 핵심 로직 대부분 재사용
- 약 150줄의 새 코드 추가
- 기존 REST API 영향 없음

✅ **배포 용이성**:
- 모든 클라우드 플랫폼 지원
- Docker 컨테이너화 가능
- 수평 확장 가능

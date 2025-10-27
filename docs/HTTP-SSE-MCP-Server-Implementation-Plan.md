# HTTP/SSE MCP 서버 + REST API 구현 계획서

## 1. 개요

### 목적
- 기존 stdio 방식의 MCP 서버를 HTTP/SSE 방식으로 재구현
- 로컬 및 원격 환경 모두에서 사용 가능한 독립 실행형 MCP 서버 구축
- **프론트엔드 대시보드 연동을 위한 REST API 제공**
- stdio 방식의 제약(로컬 전용, 프로세스 관리 복잡도)을 해결

### 주요 차이점
| 항목 | stdio 방식 (기존) | HTTP/SSE 방식 (신규) |
|------|------------------|---------------------|
| **통신 방식** | stdin/stdout | HTTP + Server-Sent Events |
| **배포 범위** | 로컬 전용 | 로컬 + 원격 가능 |
| **실행 방식** | Claude Desktop이 프로세스 실행 | 독립 서버로 실행 |
| **로그** | stderr 사용 | 파일 또는 stdout 자유롭게 사용 |
| **확장성** | 제한적 | 높음 (스케일링 가능) |
| **디버깅** | 어려움 | 쉬움 (HTTP 요청 추적) |

## 2. 프로젝트 구조

### 디렉토리 구조
```
backend-mcp-sse/
├── src/
│   ├── main.py                    # 애플리케이션 엔트리포인트 (FastAPI)
│   ├── config.py                  # 설정 관리
│   │
│   ├── mcp/                       # MCP 서버 모듈
│   │   ├── server.py              # MCP SSE 서버 핵심 로직
│   │   ├── handlers.py            # MCP 요청 핸들러
│   │   └── tools.py               # MCP Tool 변환 로직
│   │
│   ├── api/                       # REST API 모듈 (프론트엔드용)
│   │   ├── router.py              # 메인 API 라우터
│   │   ├── dependencies.py        # 의존성 주입
│   │   └── endpoints/             # API 엔드포인트
│   │       ├── health.py          # 헬스 체크
│   │       ├── apis.py            # API 목록/상세 조회
│   │       └── proxy.py           # API 호출 프록시
│   │
│   ├── core/                      # 핵심 비즈니스 로직
│   │   ├── api_router.py          # 외부 API 호출 관리
│   │   └── security.py            # 보안 (URL 검증 등)
│   │
│   ├── services/                  # 비즈니스 서비스
│   │   └── api_service.py         # API 서비스 로직
│   │
│   ├── models/                    # 데이터 모델
│   │   ├── api_definition.py     # API 정의 모델
│   │   ├── requests.py            # 요청 모델
│   │   └── responses.py           # 응답 모델
│   │
│   └── utils/                     # 유틸리티
│       └── logger.py              # 로깅 설정
│
├── data/
│   └── apis/                      # API 정의 JSON 파일 (기존 재사용)
│       ├── news.json
│       ├── steam.json
│       └── weather.json
│
├── requirements.txt               # Python 의존성
├── .env.example                   # 환경 변수 예제
└── README.md                      # 프로젝트 문서
```

### 기존 backend 프로젝트와의 관계
- **API 정의 파일 공유**: `../backend/data/apis/` 디렉토리를 심볼릭 링크 또는 복사
- **코드 재사용** (기존 backend 코드를 거의 그대로 복사):
  - `core/` - API 라우터 및 보안 로직 **복사**
  - `models/` - 모든 데이터 모델 **복사**
  - `services/` - API 서비스 로직 **복사**
  - `api/` - FastAPI 엔드포인트 **복사** (프론트엔드 연동용)
  - `utils/` - 로깅 유틸리티 **복사**
  - `mcp/` - MCP 서버 로직만 **재작성** (stdio 제거, SSE만 유지)

## 3. 기술 스택

### 핵심 라이브러리
```python
# MCP 프로토콜
mcp==1.1.2                    # MCP SDK

# 웹 프레임워크
fastapi==0.115.0              # FastAPI (REST API + MCP SSE 호스팅)
starlette==0.41.3             # ASGI 프레임워크 (FastAPI 내장)
uvicorn[standard]==0.32.1     # ASGI 서버

# HTTP 클라이언트
aiohttp==3.10.0               # 비동기 HTTP 클라이언트

# 데이터 검증
pydantic==2.9.0               # 데이터 모델
pydantic-settings==2.5.2      # 설정 관리

# JSONPath
jsonpath-ng==1.6.1            # JSONPath 쿼리

# 유틸리티
python-dotenv==1.0.1          # 환경 변수 관리
```

### 포함되는 기능
- ✅ **FastAPI REST API** (프론트엔드 대시보드용)
  - API 목록 조회 (`GET /api/v1/apis`)
  - API 상세 정보 (`GET /api/v1/apis/{service_name}`)
  - API 호출 프록시 (`POST /api/v1/proxy/{service_name}/{endpoint_name}`)
  - 헬스 체크 (`GET /api/v1/health`)
- ✅ **MCP SSE 서버** (Claude Desktop용)
  - SSE 엔드포인트 (`GET /mcp/sse`)
  - 메시지 엔드포인트 (`POST /mcp/messages`)
- ✅ **CORS 설정** (프론트엔드 연동)
- ✅ **API 문서** (Swagger UI: `/docs`)

## 4. 핵심 구현 사항

### 4.1 MCP SSE 서버 (mcp/server.py)

**기존 backend/src/mcp_server/sse_transport.py를 기반으로 작성**

```python
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount

from mcp.handlers import MCPHandlers
from core.api_router import APIRouter

class UniversalMCPServer:
    """HTTP/SSE MCP 서버"""

    def __init__(self, api_router: APIRouter):
        self.server = Server("universal-api-gateway")
        self.api_router = api_router
        self.handlers = MCPHandlers(api_router)
        self._register_handlers()

    def _register_handlers(self):
        """MCP 핸들러 등록"""
        @self.server.list_tools()
        async def list_tools():
            return await self.handlers.handle_list_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            return await self.handlers.handle_call_tool(name, arguments)

# Starlette SSE 앱 생성 함수
def create_mcp_sse_app(api_router: APIRouter) -> Starlette:
    """MCP SSE 애플리케이션 생성"""
    sse_transport = SseServerTransport("/messages/")
    mcp_server = UniversalMCPServer(api_router)

    async def handle_sse(request):
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server.server.run(
                streams[0], streams[1],
                mcp_server.server.create_initialization_options()
            )

    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse_transport.handle_post_message),
        ]
    )
```

### 4.2 메인 애플리케이션 (main.py)

**기존 backend/src/main.py를 기반으로 작성 (FastAPI 유지)**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from core.api_router import APIRouter
from api.dependencies import set_api_router
from api.router import api_router
from mcp.server import create_mcp_sse_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시: API 정의 로드 및 세션 생성
    api_router_instance = APIRouter(data_dir=settings.DATA_DIR)
    await api_router_instance.load_api_definitions()
    await api_router_instance.create_session()
    set_api_router(api_router_instance)

    # MCP SSE 앱 생성 및 마운트
    mcp_sse_app = create_mcp_sse_app(api_router_instance)
    app.mount("/mcp", mcp_sse_app)

    yield

    # 종료 시: 세션 종료
    await api_router_instance.close_session()

# FastAPI 앱 생성
app = FastAPI(
    title="Universal API Gateway",
    description="HTTP/SSE MCP Server + REST API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 설정 (프론트엔드 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+"
)

# REST API 라우터 등록 (프론트엔드용)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Universal API Gateway (HTTP/SSE)",
        "version": "2.0.0",
        "docs": "/docs",
        "mcp_sse": "/mcp/sse"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
```

### 4.3 복사할 파일 목록

**기존 backend/src에서 거의 그대로 복사:**

1. **core/** (전체 복사)
   - `api_router.py` - API 호출 관리
   - `config.py` - 설정
   - `security.py` - 보안

2. **models/** (전체 복사)
   - `api_definition.py`
   - `requests.py`
   - `responses.py`

3. **services/** (전체 복사)
   - `api_service.py`

4. **api/** (전체 복사)
   - `router.py`
   - `dependencies.py`
   - `endpoints/health.py`
   - `endpoints/apis.py`
   - `endpoints/proxy.py`

5. **utils/** (전체 복사)
   - `logger.py`

6. **mcp/** (재작성)
   - `server.py` - SSE 전용 (stdio 제거)
   - `handlers.py` - MCP 핸들러 (기존과 동일)
   - `tools.py` - Tool 변환 (기존과 동일)

## 5. 환경 설정

### .env.example
```bash
# 서버 설정
HOST=0.0.0.0
PORT=8080
LOG_LEVEL=info

# API 키 (필요시)
NEWSAPI_KEY=your_api_key_here

# 데이터 디렉토리
API_DATA_DIR=../backend/data/apis
```

### config.py (pydantic-settings 사용)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    LOG_LEVEL: str = "info"
    NEWSAPI_KEY: str = ""
    API_DATA_DIR: str = "../backend/data/apis"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 6. Claude Desktop 연결 설정

### 로컬 환경
```json
{
  "mcpServers": {
    "universal-api-gateway-sse": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

### 원격 환경 (배포 후)
```json
{
  "mcpServers": {
    "universal-api-gateway-sse": {
      "url": "https://your-domain.com/sse"
    }
  }
}
```

## 7. 실행 방법

### 개발 모드
```bash
cd backend-mcp-sse

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 서버 실행
python src/main.py
```

### 프로덕션 모드
```bash
# Uvicorn으로 직접 실행
uvicorn src.main:app --host 0.0.0.0 --port 8080 --workers 4
```

## 8. 테스트 방법

### MCP Inspector로 테스트
```bash
npx -y @modelcontextprotocol/inspector http://localhost:8080/sse
```

### curl로 SSE 연결 테스트
```bash
# SSE 엔드포인트 확인
curl -N http://localhost:8080/sse

# 응답: text/event-stream
```

## 9. 구현 단계

### Phase 1: 프로젝트 기본 구조 생성
- [ ] `backend-mcp-sse/` 디렉토리 생성
- [ ] 하위 디렉토리 생성 (`src/`, `src/mcp/`, `src/api/`, `src/core/`, 등)
- [ ] `requirements.txt` 작성
- [ ] `.env.example` 작성

### Phase 2: 기존 코드 복사
- [ ] `backend/src/core/` → `backend-mcp-sse/src/core/` 복사
- [ ] `backend/src/models/` → `backend-mcp-sse/src/models/` 복사
- [ ] `backend/src/services/` → `backend-mcp-sse/src/services/` 복사
- [ ] `backend/src/api/` → `backend-mcp-sse/src/api/` 복사
- [ ] `backend/src/utils/` → `backend-mcp-sse/src/utils/` 복사
- [ ] `backend/data/apis/` → `backend-mcp-sse/data/apis/` 복사

### Phase 3: MCP 모듈 재작성
- [ ] `src/mcp/server.py` - SSE 전용으로 재작성
- [ ] `src/mcp/handlers.py` - 기존 복사 후 import 경로 수정
- [ ] `src/mcp/tools.py` - 기존 복사 후 import 경로 수정
- [ ] `src/mcp/__init__.py` - 생성

### Phase 4: main.py 수정
- [ ] `src/main.py` - FastAPI + MCP SSE 통합
- [ ] MCP SSE 앱 마운트 로직 추가
- [ ] 기존 REST API 라우터 유지
- [ ] CORS 설정 유지

### Phase 5: config.py 수정
- [ ] 포트 변경 (8000 → 8080)
- [ ] MCP SSE 엔드포인트 설정

### Phase 6: 테스트 및 검증
- [ ] 로컬 환경에서 서버 실행 (`python src/main.py`)
- [ ] FastAPI 문서 확인 (`http://localhost:8080/docs`)
- [ ] MCP Inspector로 SSE 연결 테스트 (`http://localhost:8080/mcp/sse`)
- [ ] Claude Desktop 연결 테스트
- [ ] 프론트엔드 연결 테스트 (`http://localhost:5173`)
- [ ] 5개 API 도구 동작 검증

### Phase 7: 문서화
- [ ] README.md 작성
- [ ] 실행 방법 문서화
- [ ] Claude Desktop 설정 가이드
- [ ] 프론트엔드 연동 가이드

## 10. 기존 코드 재사용 전략

### 복사할 파일
1. `backend/data/apis/*.json` → `backend-mcp-sse/data/apis/`
2. `backend/.env.example` → `backend-mcp-sse/.env.example` (수정)

### 참고할 파일 (직접 재작성)
1. `backend/src/core/api_router.py` → API 호출 로직 참고
2. `backend/src/models/api_definition.py` → 모델 정의 참고
3. `backend/src/mcp_server/handlers.py` → 핸들러 구조 참고
4. `backend/src/mcp_server/tools.py` → Tool 변환 로직 참고
5. `backend/src/utils/logger.py` → 로깅 설정 참고 (stdout 사용 가능)

### 제외할 부분
- FastAPI 관련 코드 전체
- REST API 엔드포인트 (`api/endpoints/`)
- stdio 관련 코드 (`mcp_server/server.py`의 stdio 부분)

## 11. 장점 및 기대 효과

### 장점
1. **배포 유연성**: 로컬 및 원격 모두 지원
2. **확장성**: 수평 확장 가능 (로드 밸런서 + 여러 인스턴스)
3. **디버깅 용이**: HTTP 요청 추적 가능
4. **독립성**: Claude Desktop의 프로세스 관리에 의존하지 않음
5. **로깅 자유도**: stdout 사용 가능, 제약 없음

### stdio 방식 대비 개선점
- ✅ 원격 배포 가능
- ✅ 로그 관리 간편
- ✅ 상태 모니터링 가능
- ✅ HTTPS 지원 (보안)
- ✅ 다중 클라이언트 연결 가능

## 12. 주의사항

### SSE 구현 시 주의점
1. **CORS 설정**: 원격 접속 시 필요
2. **타임아웃 관리**: 긴 SSE 연결 유지
3. **에러 핸들링**: 연결 끊김 시 재연결 로직
4. **보안**: HTTPS 사용 권장 (프로덕션)

### MCP 프로토콜 준수
1. **초기화**: `initialize` 요청 처리
2. **도구 목록**: `tools/list` 요청 처리
3. **도구 호출**: `tools/call` 요청 처리
4. **에러 응답**: JSON-RPC 표준 준수

## 13. 참고 자료

- [MCP SSE Transport Specification](https://spec.modelcontextprotocol.io/specification/basic/transports/#http-with-sse)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Starlette Documentation](https://www.starlette.io/)

---

**작성일**: 2025-10-27
**작성자**: Generated with Claude Code

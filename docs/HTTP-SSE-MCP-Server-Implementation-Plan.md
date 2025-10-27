# HTTP/SSE 전용 MCP 서버 구현 계획서

## 1. 개요

### 목적
- 기존 stdio 방식의 MCP 서버를 HTTP/SSE 방식으로 재구현
- 로컬 및 원격 환경 모두에서 사용 가능한 독립 실행형 MCP 서버 구축
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
│   ├── main.py                    # 애플리케이션 엔트리포인트
│   ├── config.py                  # 설정 관리
│   ├── server.py                  # MCP SSE 서버 핵심 로직
│   ├── handlers.py                # MCP 요청 핸들러
│   ├── tools.py                   # MCP Tool 변환 로직
│   ├── api_client.py              # 외부 API 호출 클라이언트
│   └── models.py                  # 데이터 모델 (Pydantic)
├── data/
│   └── apis/                      # API 정의 JSON 파일 (기존 재사용)
│       ├── news.json
│       ├── steam.json
│       └── weather.json
├── requirements.txt               # Python 의존성
├── .env.example                   # 환경 변수 예제
└── README.md                      # 프로젝트 문서

```

### 기존 backend 프로젝트와의 관계
- **API 정의 파일 공유**: `../backend/data/apis/` 디렉토리를 심볼릭 링크 또는 복사
- **코드 재사용**:
  - `core/api_router.py` → `api_client.py`로 재구성
  - `models/api_definition.py` → `models.py`에 포함
  - MCP 관련 로직은 기존 `mcp_server/` 참고하여 재작성

## 3. 기술 스택

### 핵심 라이브러리
```python
# MCP 프로토콜
mcp==1.1.2                    # MCP SDK

# 웹 프레임워크
starlette==0.41.3             # 경량 ASGI 프레임워크
uvicorn[standard]==0.32.1     # ASGI 서버

# HTTP 클라이언트
aiohttp==3.10.0               # 비동기 HTTP 클라이언트
httpx==0.27.0                 # 대안 HTTP 클라이언트

# 데이터 검증
pydantic==2.9.0               # 데이터 모델
pydantic-settings==2.5.2      # 설정 관리

# 유틸리티
python-dotenv==1.0.1          # 환경 변수 관리
```

### 제외되는 요소
- FastAPI (불필요 - Starlette만으로 충분)
- REST API 엔드포인트 (MCP SSE만 제공)
- 데이터베이스 (상태 비저장)

## 4. 핵심 구현 사항

### 4.1 MCP SSE 서버 (server.py)

```python
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response

class UniversalMCPServer:
    """HTTP/SSE 전용 MCP 서버"""

    def __init__(self):
        self.mcp_server = Server("universal-api-gateway")
        self.sse_transport = SseServerTransport("/messages")

    async def handle_sse(self, request: Request) -> Response:
        """SSE 연결 핸들러"""
        async with self.sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send
        ) as streams:
            await self.mcp_server.run(
                streams[0],
                streams[1],
                self.mcp_server.create_initialization_options()
            )
        return Response()

    def create_app(self) -> Starlette:
        """Starlette 애플리케이션 생성"""
        return Starlette(
            routes=[
                Route("/sse", endpoint=self.handle_sse, methods=["GET"]),
                Mount("/messages", app=self.sse_transport.handle_post_message),
            ],
            debug=True
        )
```

### 4.2 API 클라이언트 (api_client.py)

기존 `core/api_router.py`를 단순화:
```python
import aiohttp
from typing import Dict, Any, List
from models import APIDefinition

class APIClient:
    """외부 API 호출 클라이언트"""

    def __init__(self):
        self.session: aiohttp.ClientSession = None
        self.apis: Dict[str, APIDefinition] = {}

    async def load_apis(self, data_dir: str):
        """API 정의 로드"""
        # JSON 파일 읽기 및 파싱

    async def call_api(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """API 호출 및 응답 반환"""
        # HTTP 요청 실행
        # JSONPath 매핑 적용
        # 결과 반환
```

### 4.3 MCP 핸들러 (handlers.py)

기존 `mcp_server/handlers.py`와 유사하지만 독립적:
```python
from mcp.types import Tool, TextContent
from typing import List, Dict, Any
from api_client import APIClient

class MCPHandlers:
    """MCP 요청 핸들러"""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def list_tools(self) -> List[Tool]:
        """도구 목록 반환"""

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """도구 호출"""
```

### 4.4 메인 애플리케이션 (main.py)

```python
import uvicorn
from server import UniversalMCPServer
from config import settings

async def startup():
    """서버 시작 시 초기화"""
    # API 정의 로드
    # 세션 생성

async def shutdown():
    """서버 종료 시 정리"""
    # 세션 종료

def main():
    server = UniversalMCPServer()
    app = server.create_app()

    # 이벤트 핸들러 등록
    app.add_event_handler("startup", startup)
    app.add_event_handler("shutdown", shutdown)

    # Uvicorn 서버 실행
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL
    )

if __name__ == "__main__":
    main()
```

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

### Phase 1: 프로젝트 기본 구조 생성 ✅
- [ ] `backend-mcp-sse/` 디렉토리 생성
- [ ] 기본 파일 구조 생성
- [ ] `requirements.txt` 작성
- [ ] `.env.example` 작성

### Phase 2: 핵심 모듈 구현 ✅
- [ ] `models.py` - 데이터 모델 정의
- [ ] `config.py` - 설정 관리
- [ ] `api_client.py` - API 클라이언트 구현
- [ ] `handlers.py` - MCP 핸들러 구현
- [ ] `tools.py` - Tool 변환 로직

### Phase 3: MCP SSE 서버 구현 ✅
- [ ] `server.py` - SSE 서버 핵심 로직
- [ ] `main.py` - 애플리케이션 엔트리포인트
- [ ] 로깅 설정

### Phase 4: 테스트 및 검증 ✅
- [ ] 로컬 환경에서 서버 실행 테스트
- [ ] MCP Inspector로 연결 테스트
- [ ] Claude Desktop 연결 테스트
- [ ] 5개 API 도구 동작 검증

### Phase 5: 문서화 및 배포 준비 ✅
- [ ] README.md 작성
- [ ] Docker 지원 (선택사항)
- [ ] 배포 가이드 작성

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

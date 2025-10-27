# 기획서_251027_수정본 (MVP 중심)

## 📋 변경 사항 요약

### ✂️ MVP에서 제외된 기능

1. ❌ **API 문서 자동 변환 (LLM 기반)** → Phase 2로 이동
2. ❌ **사용자별 인증 정보 관리** → Phase 2로 이동
3. ✅ **수동 API 등록 및 하드코딩 방식** → MVP에서 구현

### 📌 MVP 핵심 목표

> "수동으로 등록된 3-5개의 Public API를 단일 MCP 서버를 통해 Claude에서 사용할 수 있다"
>

---

## 🎯 프로젝트 개요

### 핵심 아이디어

사용자가 Claude(또는 다른 LLM)를 사용할 때, **하나의 MCP 서버만 설치**하면 여러 외부 API를 손쉽게 사용할 수 있도록 하는 **Universal API Gateway**

### 사용자 시나리오

```
1. 사용자: Claude Desktop에 우리 MCP 서버 설치 (1회)
2. 사용자: "최근 인기있는 스팀 게임 5개 알려줘"
3. Claude: 우리 MCP 서버의 steam_popular_games 도구 사용
4. MCP 서버: Steam API 호출 → 결과 반환
5. Claude: 자연어로 응답 생성

```

### 차별점

- **기존**: Steam MCP, Weather MCP, News MCP... 각각 설치 필요
- **우리**: 하나의 MCP 서버에서 모든 API 접근 가능

---

## 🏗️ MVP 아키텍처

### 전체 구조도

```
┌─────────────┐
│   사용자    │
└──────┬──────┘
       │ "최근 스팀 게임 알려줘"
       ↓
┌─────────────────────┐
│  Claude (Desktop)   │
│  + MCP Client       │
└──────┬──────────────┘
       │ MCP Protocol (stdio)
       ↓
┌──────────────────────────┐
│  Universal API Gateway   │
│  MCP Server (Python)     │
│  ┌────────────────────┐  │
│  │  tools/list        │  │
│  │  tools/call        │  │
│  │  API Router        │  │
│  └────────────────────┘  │
└──────┬───────────────────┘
       │ HTTP Request
       ↓
┌──────────────────────┐
│  External APIs       │
│  - Steam API         │
│  - Weather API       │
│  - News API          │
└──────────────────────┘

```

### 핵심 컴포넌트

### 1. MCP Server (Python)

- **역할**: MCP 프로토콜 구현, API 라우팅
- **기술**: Python 3.11+, mcp SDK
- **배포**: Docker 컨테이너 또는 PyPI 패키지

### 2. API Definitions (JSON Config)

- **역할**: API 정보를 코드로 관리
- **형식**: JSON 파일 (수동 작성)
- **위치**: `/config/apis/*.json`

### 3. Request Handler

- **역할**: 외부 API 호출 및 응답 변환
- **기능**: 에러 핸들링, 타임아웃, 재시도

---

## 📁 프로젝트 구조

```
universal-api-mcp/
├── src/
│   ├── server.py              # MCP 서버 메인
│   ├── api_router.py          # API 라우팅 로직
│   ├── handlers/
│   │   ├── steam_handler.py   # Steam API 핸들러
│   │   ├── weather_handler.py # Weather API 핸들러
│   │   └── news_handler.py    # News API 핸들러
│   └── utils/
│       ├── http_client.py     # HTTP 클라이언트
│       └── logger.py          # 로깅
├── config/
│   └── apis/
│       ├── steam.json         # Steam API 정의
│       ├── weather.json       # Weather API 정의
│       └── news.json          # News API 정의
├── tests/
│   ├── test_server.py
│   └── test_handlers.py
├── pyproject.toml
├── README.md
└── Dockerfile

```

---

## 📄 API 정의 형식 (JSON)

### 예시: Steam API 정의

```json
{
  "service_name": "steam",
  "display_name": "Steam Web API",
  "base_url": "https://api.steampowered.com",
  "description": "Steam 게임 정보를 조회합니다",
  "auth_required": false,
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
      "timeout_seconds": 10,
      "rate_limit": {
        "max_calls": 100,
        "per_seconds": 60
      }
    }
  ]
}

```

### 예시: Weather API 정의 (인증 불필요 버전)

```json
{
  "service_name": "weather",
  "display_name": "Open-Meteo Weather API",
  "base_url": "https://api.open-meteo.com",
  "description": "날씨 정보를 조회합니다 (인증 불필요)",
  "auth_required": false,
  "endpoints": [
    {
      "id": "get_current_weather",
      "name": "weather_get_current",
      "display_name": "Get Current Weather",
      "description": "현재 날씨 정보를 조회합니다",
      "http_method": "GET",
      "path": "/v1/forecast",
      "parameters": {
        "latitude": {
          "type": "number",
          "description": "위도",
          "required": true
        },
        "longitude": {
          "type": "number",
          "description": "경도",
          "required": true
        },
        "current_weather": {
          "type": "boolean",
          "description": "현재 날씨 포함 여부",
          "required": false,
          "default": true
        }
      },
      "response_mapping": {
        "path": "$.current_weather",
        "format": "json"
      },
      "timeout_seconds": 5
    }
  ]
}

```

---

## 💻 핵심 코드 구현

### 1. MCP Server (server.py)

```python
"""
Universal API Gateway MCP Server
MVP Version - 수동 등록된 API만 지원
"""
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent
import aiohttp

from api_router import APIRouter
from utils.logger import setup_logger

logger = setup_logger(__name__)

class UniversalAPIServer:
    def __init__(self, config_dir: str = "./config/apis"):
        self.server = Server("universal-api-gateway")
        self.router = APIRouter(config_dir)
        self.session: aiohttp.ClientSession | None = None

    async def initialize(self):
        """서버 초기화"""
        # API 정의 로드
        await self.router.load_api_definitions()
        logger.info(f"Loaded {len(self.router.apis)} APIs")

        # HTTP 세션 생성
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )

        # MCP 핸들러 등록
        self._register_handlers()

    def _register_handlers(self):
        """MCP 요청 핸들러 등록"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """사용 가능한 모든 도구 목록 반환"""
            return await self._list_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """도구 호출 및 결과 반환"""
            return await self._call_tool(name, arguments)

    async def _list_tools(self) -> List[Tool]:
        """
        등록된 모든 API 엔드포인트를 MCP Tool 형식으로 변환
        """
        tools = []

        for api in self.router.apis.values():
            for endpoint in api["endpoints"]:
                # MCP Tool 스키마 생성
                input_schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }

                # 파라미터를 JSON Schema로 변환
                for param_name, param_def in endpoint["parameters"].items():
                    input_schema["properties"][param_name] = {
                        "type": param_def["type"],
                        "description": param_def["description"]
                    }

                    if param_def.get("default"):
                        input_schema["properties"][param_name]["default"] = param_def["default"]

                    if param_def.get("required", False):
                        input_schema["required"].append(param_name)

                # Tool 객체 생성
                tool = Tool(
                    name=endpoint["name"],
                    description=endpoint["description"],
                    inputSchema=input_schema
                )
                tools.append(tool)

        logger.info(f"Listed {len(tools)} tools")
        return tools

    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        API 호출 및 결과 반환
        """
        try:
            logger.info(f"Calling tool: {name} with args: {arguments}")

            # API 라우팅
            result = await self.router.route_request(
                tool_name=name,
                arguments=arguments,
                session=self.session
            )

            # 결과 포맷팅
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            logger.error(f"Error calling tool {name}: {str(e)}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    async def cleanup(self):
        """리소스 정리"""
        if self.session:
            await self.session.close()

    def run(self):
        """서버 실행"""
        import asyncio
        from mcp.server.stdio import stdio_server

        async def main():
            async with stdio_server() as (read_stream, write_stream):
                await self.initialize()
                try:
                    await self.server.run(
                        read_stream,
                        write_stream,
                        self.server.create_initialization_options()
                    )
                finally:
                    await self.cleanup()

        asyncio.run(main())

if __name__ == "__main__":
    server = UniversalAPIServer()
    server.run()

```

### 2. API Router (api_router.py)

```python
"""
API 라우팅 및 호출 로직
"""
import json
from pathlib import Path
from typing import Any, Dict
import aiohttp

from utils.logger import setup_logger

logger = setup_logger(__name__)

class APIRouter:
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.apis: Dict[str, Dict] = {}
        self.tool_map: Dict[str, tuple] = {}  # tool_name -> (service, endpoint)

    async def load_api_definitions(self):
        """
        JSON 파일에서 API 정의 로드
        """
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")

        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    api_def = json.load(f)

                service_name = api_def["service_name"]
                self.apis[service_name] = api_def

                # Tool 이름 매핑 생성
                for endpoint in api_def["endpoints"]:
                    tool_name = endpoint["name"]
                    self.tool_map[tool_name] = (service_name, endpoint["id"])

                logger.info(f"Loaded API: {service_name} with {len(api_def['endpoints'])} endpoints")

            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")

    async def route_request(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        session: aiohttp.ClientSession
    ) -> Any:
        """
        Tool 이름으로 적절한 API 호출
        """
        # Tool 찾기
        if tool_name not in self.tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        service_name, endpoint_id = self.tool_map[tool_name]
        api_def = self.apis[service_name]

        # Endpoint 정의 찾기
        endpoint = None
        for ep in api_def["endpoints"]:
            if ep["id"] == endpoint_id:
                endpoint = ep
                break

        if not endpoint:
            raise ValueError(f"Endpoint not found: {endpoint_id}")

        # API 호출
        return await self._call_api(api_def, endpoint, arguments, session)

    async def _call_api(
        self,
        api_def: Dict,
        endpoint: Dict,
        arguments: Dict[str, Any],
        session: aiohttp.ClientSession
    ) -> Any:
        """
        실제 외부 API 호출
        """
        # URL 구성
        url = f"{api_def['base_url']}{endpoint['path']}"

        # 파라미터 검증 및 기본값 적용
        params = {}
        for param_name, param_def in endpoint["parameters"].items():
            if param_name in arguments:
                params[param_name] = arguments[param_name]
            elif param_def.get("required", False):
                raise ValueError(f"Required parameter missing: {param_name}")
            elif "default" in param_def:
                params[param_name] = param_def["default"]

        # 타임아웃 설정
        timeout = aiohttp.ClientTimeout(
            total=endpoint.get("timeout_seconds", 10)
        )

        # HTTP 요청
        method = endpoint["http_method"]

        try:
            async with session.request(
                method=method,
                url=url,
                params=params if method == "GET" else None,
                json=params if method == "POST" else None,
                timeout=timeout
            ) as response:
                response.raise_for_status()
                data = await response.json()

                # 응답 매핑 (JSONPath)
                if "response_mapping" in endpoint:
                    mapping = endpoint["response_mapping"]
                    if mapping.get("path"):
                        data = self._extract_json_path(data, mapping["path"])

                logger.info(f"API call successful: {endpoint['name']}")
                return data

        except aiohttp.ClientError as e:
            logger.error(f"API call failed: {endpoint['name']}: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"API call timeout: {endpoint['name']}")
            raise Exception(f"API request timeout after {endpoint.get('timeout_seconds', 10)}s")

    def _extract_json_path(self, data: Any, path: str) -> Any:
        """
        간단한 JSONPath 추출 (MVP용)
        $.response.data 형식만 지원
        """
        if not path.startswith("$."):
            return data

        keys = path[2:].split(".")
        result = data

        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            else:
                return result

        return result

```

### 3. Steam Handler 예시

```python
"""
Steam API 전용 핸들러 (선택적 - 복잡한 로직이 필요한 경우)
"""
from typing import Any, Dict

class SteamHandler:
    """
    Steam API의 복잡한 로직을 처리
    (MVP에서는 선택사항)
    """

    @staticmethod
    def format_game_list(raw_data: Dict) -> Dict[str, Any]:
        """
        Steam API 응답을 사용자 친화적 형식으로 변환
        """
        games = []

        for rank in raw_data.get("ranks", []):
            games.append({
                "rank": rank.get("rank"),
                "app_id": rank.get("appid"),
                "concurrent_players": rank.get("concurrent_in_game"),
                "peak_players": rank.get("peak_in_game")
            })

        return {
            "total_games": len(games),
            "games": games
        }

```

---

## 🗂️ 데이터베이스 스키마 (Phase 2용)

MVP에서는 **데이터베이스를 사용하지 않습니다**. 모든 정보는 JSON 파일로 관리합니다.

Phase 2에서 DB 도입 시 아래 스키마 사용:

```sql
-- API 서비스 정보
CREATE TABLE api_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    base_url TEXT NOT NULL,
    description TEXT,
    auth_required BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API 엔드포인트
CREATE TABLE api_endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID REFERENCES api_services(id) ON DELETE CASCADE,
    endpoint_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    http_method VARCHAR(10) NOT NULL,
    path TEXT NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}',
    response_mapping JSONB,
    timeout_seconds INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(service_id, endpoint_id)
);

-- API 호출 로그
CREATE TABLE api_call_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_id UUID REFERENCES api_endpoints(id),
    arguments JSONB,
    response_data JSONB,
    status_code INTEGER,
    success BOOLEAN,
    error_message TEXT,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_api_services_name ON api_services(name);
CREATE INDEX idx_api_endpoints_name ON api_endpoints(name);
CREATE INDEX idx_api_call_logs_created_at ON api_call_logs(created_at DESC);

```

---

## 🔒 보안 고려사항

### MVP에서 구현할 보안 기능

1. **URL 화이트리스트**

```python
ALLOWED_DOMAINS = [
    "api.steampowered.com",
    "api.open-meteo.com",
    "newsapi.org"
]

def validate_url(url: str) -> bool:
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain in ALLOWED_DOMAINS

```

1. **내부 IP 차단**

```python
BLOCKED_IP_RANGES = [
    "127.0.0.0/8",      # localhost
    "10.0.0.0/8",       # Private A
    "172.16.0.0/12",    # Private B
    "192.168.0.0/16",   # Private C
    "169.254.0.0/16",   # Link-local
]

def is_internal_ip(ip: str) -> bool:
    import ipaddress
    ip_obj = ipaddress.ip_address(ip)
    for cidr in BLOCKED_IP_RANGES:
        if ip_obj in ipaddress.ip_network(cidr):
            return True
    return False

```

1. **Rate Limiting (간단한 버전)**

```python
from collections import defaultdict
from datetime import datetime, timedelta

class SimpleRateLimiter:
    def __init__(self):
        self.calls = defaultdict(list)  # tool_name -> [timestamps]

    def check_limit(self, tool_name: str, max_calls: int, per_seconds: int) -> bool:
        now = datetime.now()
        cutoff = now - timedelta(seconds=per_seconds)

        # 오래된 호출 기록 제거
        self.calls[tool_name] = [
            ts for ts in self.calls[tool_name] if ts > cutoff
        ]

        # 제한 확인
        if len(self.calls[tool_name]) >= max_calls:
            return False

        # 호출 기록
        self.calls[tool_name].append(now)
        return True

```

1. **입력 검증**

```python
def validate_parameters(arguments: Dict, parameter_defs: Dict) -> None:
    """
    사용자 입력 검증
    """
    for param_name, value in arguments.items():
        if param_name not in parameter_defs:
            raise ValueError(f"Unknown parameter: {param_name}")

        param_def = parameter_defs[param_name]

        # 타입 검증
        expected_type = param_def["type"]
        if expected_type == "integer" and not isinstance(value, int):
            raise TypeError(f"{param_name} must be integer")
        elif expected_type == "number" and not isinstance(value, (int, float)):
            raise TypeError(f"{param_name} must be number")
        elif expected_type == "string" and not isinstance(value, str):
            raise TypeError(f"{param_name} must be string")

        # 범위 검증
        if "min" in param_def and value < param_def["min"]:
            raise ValueError(f"{param_name} must be >= {param_def['min']}")
        if "max" in param_def and value > param_def["max"]:
            raise ValueError(f"{param_name} must be <= {param_def['max']}")

```

### Phase 2에서 추가할 보안 기능

- API Key 암호화 저장
- OAuth 2.0 지원
- HTTPS 강제
- 요청/응답 로깅 및 모니터링

---

## 🧪 테스트 전략

### 단위 테스트

```python
import pytest
from api_router import APIRouter

@pytest.mark.asyncio
async def test_load_api_definitions():
    router = APIRouter("./tests/fixtures/apis")
    await router.load_api_definitions()

    assert "steam" in router.apis
    assert len(router.apis["steam"]["endpoints"]) > 0

@pytest.mark.asyncio
async def test_route_request():
    router = APIRouter("./config/apis")
    await router.load_api_definitions()

    # Mock session
    from unittest.mock import AsyncMock
    session = AsyncMock()

    result = await router.route_request(
        tool_name="steam_get_popular_games",
        arguments={"count": 5},
        session=session
    )

    assert result is not None

```

### 통합 테스트

```python
@pytest.mark.asyncio
async def test_steam_api_integration():
    """
    실제 Steam API 호출 테스트
    """
    router = APIRouter("./config/apis")
    await router.load_api_definitions()

    import aiohttp
    async with aiohttp.ClientSession() as session:
        result = await router.route_request(
            tool_name="steam_get_popular_games",
            arguments={"count": 3},
            session=session
        )

        assert "ranks" in result or "games" in result
        assert len(result.get("ranks", result.get("games", []))) <= 3

```

### 수동 테스트 (Claude Desktop)

1. MCP 서버 빌드 및 설치
2. Claude Desktop 설정 파일 수정
3. Claude에게 "최근 인기 스팀 게임 알려줘" 요청
4. 정상 응답 확인

---

## 📦 배포 방식

### Option 1: PyPI 패키지 (추천)

```bash
# 사용자 설치
pip install universal-api-mcp

# Claude Desktop 설정
{
  "mcpServers": {
    "universal-api": {
      "command": "universal-api-mcp",
      "args": []
    }
  }
}

```

### Option 2: npx (Node.js 래퍼)

```bash
# Python 서버를 Node.js로 래핑
npx universal-api-mcp

# Claude Desktop 설정
{
  "mcpServers": {
    "universal-api": {
      "command": "npx",
      "args": ["-y", "universal-api-mcp"]
    }
  }
}

```

### Option 3: Docker

```docker
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["universal-api-mcp"]

```

---

## 📊 MVP 범위 및 일정

### Week 1: 핵심 기능 (5일)

**Day 1-2**: 프로젝트 설정 및 구조

- ✅ Python 프로젝트 생성
- ✅ MCP SDK 설정
- ✅ 기본 프로젝트 구조
- ✅ JSON 설정 파일 형식 정의

**Day 3-4**: 1개 API 구현 (Steam)

- ✅ Steam API JSON 정의 작성
- ✅ API Router 구현
- ✅ HTTP 클라이언트 구현
- ✅ 로컬 테스트

**Day 5**: 통합 테스트

- ✅ Claude Desktop 연동
- ✅ 실제 Steam API 호출 테스트
- ✅ 에러 케이스 테스트

### Week 2: 확장 및 안정화 (5일)

**Day 1-2**: 2-3개 API 추가

- ✅ Weather API (Open-Meteo)
- ✅ News API (NewsAPI.org - Free tier)

**Day 3**: 공통 로직 개선

- ✅ 에러 핸들링 통합
- ✅ 로깅 시스템
- ✅ Rate Limiting

**Day 4**: 문서 작성

- ✅ README.md
- ✅ API 추가 가이드
- ✅ 사용자 가이드

**Day 5**: 배포 준비

- ✅ PyPI 패키지 빌드
- ✅ Docker 이미지
- ✅ 최종 테스트

---

## 🎯 MVP 성공 기준

### 필수 기능 (Must Have)

- [x]  3개 이상의 Public API 지원
- [x]  MCP tools/list 구현
- [x]  MCP tools/call 구현
- [x]  Claude Desktop에서 정상 작동
- [x]  기본 에러 핸들링
- [x]  설치 문서

### 선택 기능 (Nice to Have)

- [ ]  5개 이상 API 지원
- [ ]  Rate Limiting
- [ ]  상세한 로깅
- [ ]  Docker 배포

### 성능 목표

- API 응답 시간: < 3초 (95 percentile)
- MCP 서버 시작 시간: < 2초
- 메모리 사용량: < 100MB

---

## 🚀 Phase 2 계획 (MVP 이후)

### Phase 2.1: 자동화 (2-3주)

- LLM 기반 API 문서 분석
- OpenAPI 3.0 자동 변환
- API 자동 테스트

### Phase 2.2: 사용자 기능 (2-3주)

- 웹 대시보드
- 사용자 인증
- API Key 관리
- 사용량 추적

### Phase 2.3: 확장 (3-4주)

- 데이터베이스 도입 (PostgreSQL)
- OAuth 2.0 지원
- 커뮤니티 API 제출
- Premium 기능

---

## 📋 MVP 체크리스트

### 개발 환경 설정

- [ ]  Python 3.11+ 설치
- [ ]  Poetry 또는 pip-tools 설정
- [ ]  MCP SDK 설치
- [ ]  Claude Desktop 설치
- [ ]  Git 저장소 생성

### 코드 작성

- [ ]  server.py 구현
- [ ]  api_router.py 구현
- [ ]  Steam API JSON 정의
- [ ]  Weather API JSON 정의
- [ ]  News API JSON 정의
- [ ]  단위 테스트 작성

### 테스트

- [ ]  로컬 MCP 서버 실행
- [ ]  Claude Desktop 연동
- [ ]  각 API 호출 테스트
- [ ]  에러 케이스 테스트

### 문서

- [ ]  README.md (설치 방법)
- [ ]  API 추가 가이드
- [ ]  사용자 가이드
- [ ]  아키텍처 문서

### 배포

- [ ]  PyPI 패키지 빌드
- [ ]  PyPI 퍼블리싱
- [ ]  GitHub Release
- [ ]  사용자 피드백 수집

---

## 💡 주요 차이점 (원본 기획서 vs MVP)

| 항목 | 원본 기획서 | MVP (수정본) |
| --- | --- | --- |
| **API 등록 방식** | LLM 자동 변환 | 수동 JSON 작성 |
| **데이터베이스** | PostgreSQL | 없음 (JSON 파일) |
| **인증 관리** | 사용자별 암호화 저장 | 없음 (Public API만) |
| **API 개수** | 수백 개 목표 | 3-5개로 시작 |
| **웹 대시보드** | Phase 2 | 없음 |
| **개발 기간** | 2주 | 2주 (현실적) |
| **배포 복잡도** | 높음 | 낮음 |
| **실현 가능성** | 70% | 95% |

---

## ⚠️ 알려진 제약사항

### MVP의 한계

1. **인증이 필요한 API 사용 불가**
    - Steam API 일부 기능 제한
    - 유료 API 사용 불가
    - 해결: Phase 2에서 구현
2. **API 추가가 수동**
    - 개발자가 JSON 파일 작성 필요
    - 커뮤니티가 직접 추가 불가
    - 해결: Phase 2에서 자동화
3. **확장성 제한**
    - JSON 파일 관리의 한계
    - 버전 관리 어려움
    - 해결: DB 도입 시 해결
4. **모니터링 부족**
    - 로그만 있고 대시보드 없음
    - 사용량 추적 불가
    - 해결: Phase 2에서 구현

### 기술적 제약

- Python 3.11+ 필수
- MCP는 stdio만 지원 (로컬 실행만 가능)
- 외부 API의 Rate Limit 적용

---

## 🎓 학습 목표 (3개월 과정 고려)

이 프로젝트를 통해 학습할 수 있는 내용:

### 백엔드 개발

- ✅ Python 비동기 프로그래밍 (asyncio, aiohttp)
- ✅ RESTful API 호출 및 처리
- ✅ JSON 스키마 설계 및 검증
- ✅ 에러 핸들링 및 로깅

### AI/LLM 관련

- ✅ MCP (Model Context Protocol) 프로토콜
- ✅ LLM과 외부 도구 통합
- ✅ Prompt Engineering (API 문서 분석용)

### 소프트웨어 엔지니어링

- ✅ 모듈화 및 추상화
- ✅ 테스트 작성 (pytest)
- ✅ 문서화
- ✅ 배포 및 패키징

### 추가 학습 기회 (Phase 2)

- 데이터베이스 설계 (PostgreSQL)
- 웹 개발 (FastAPI)
- OAuth 2.0
- Docker 및 배포

---

## 📚 참고 자료

### MCP 관련

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop 설정](https://docs.anthropic.com/claude/docs/claude-desktop)

### API 문서

- [Steam Web API](https://steamcommunity.com/dev)
- [Open-Meteo API](https://open-meteo.com/en/docs)
- [NewsAPI](https://newsapi.org/docs)

### Python 라이브러리

- [aiohttp](https://docs.aiohttp.org/) - 비동기 HTTP 클라이언트
- [pydantic](https://docs.pydantic.dev/) - 데이터 검증
- [jsonpath-ng](https://github.com/h2non/jsonpath-ng) - JSON 파싱

---

## ✅ 다음 단계

1. **프로젝트 시작**

    ```bash
    mkdir universal-api-mcp
    cd universal-api-mcp
    poetry init
    poetry add mcp aiohttp pydantic

    ```

2. **첫 번째 API 구현**
    - `config/apis/steam.json` 작성
    - `src/server.py` 기본 구현
    - 로컬 테스트
3. **Claude Desktop 연동**
    - 설정 파일 수정
    - 실제 대화로 테스트
4. **반복 개선**
    - 추가 API 구현
    - 에러 케이스 처리
    - 문서 작성

---

**작성일**: 2025-10-27

**버전**: MVP 1.0

**상태**: 구현 준비 완료

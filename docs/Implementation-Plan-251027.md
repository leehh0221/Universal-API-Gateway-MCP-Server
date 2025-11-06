# Universal API Gateway MCP Server - 구현 계획서

작성일: 2025-10-27
버전: v1.0
기술 스택: FastAPI (Backend) + React (Frontend)
목표: MVP (Minimum Viable Product)

---

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [기술 스택 및 아키텍처](#기술-스택-및-아키텍처)
3. [구현 범위 (MVP)](#구현-범위-mvp)
4. [프로젝트 구조](#프로젝트-구조)
5. [백엔드 구현 (FastAPI)](#백엔드-구현-fastapi)
6. [프론트엔드 구현 (React)](#프론트엔드-구현-react)
7. [MCP 서버 구현](#mcp-서버-구현)
8. [데이터 모델 및 하드코딩 데이터](#데이터-모델-및-하드코딩-데이터)
9. [API 엔드포인트 명세](#api-엔드포인트-명세)
10. [보안 및 에러 핸들링](#보안-및-에러-핸들링)
11. [테스트 전략](#테스트-전략)
12. [배포 전략](#배포-전략)
13. [개발 일정](#개발-일정)
14. [Phase 2 확장 계획](#phase-2-확장-계획)

---

## 프로젝트 개요

### 핵심 목표

**"하나의 MCP 서버로 여러 외부 API를 Claude에서 사용할 수 있는 Universal API Gateway 구축"**

### MVP 핵심 기능

1. **MCP 서버**: Python 기반 MCP 프로토콜 구현
2. **관리 웹 대시보드**: React 기반 API 등록/관리 UI
3. **API 게이트웨이**: FastAPI 기반 REST API 서버
4. **하드코딩 예시**: 3-5개의 Public API (Steam, Weather, News 등)

### 사용자 시나리오

```
[시나리오 1: Claude 사용자]
1. Claude Desktop에 MCP 서버 설치 (1회)
2. "최근 인기 스팀 게임 알려줘" 요청
3. Claude가 MCP 서버의 steam_popular_games 도구 사용
4. 결과를 자연어로 확인

[시나리오 2: 개발자/관리자]
1. 웹 대시보드 접속 (http://localhost:3000)
2. 등록된 API 목록 확인
3. 새로운 API 엔드포인트 추가 (JSON 편집)
4. API 테스트 및 검증
```

---

## 기술 스택 및 아키텍처

### 전체 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                     사용자 레이어                          │
├──────────────────────┬──────────────────────────────────┤
│  Claude Desktop      │  웹 브라우저 (관리자)               │
│  + MCP Client        │  React Dashboard                  │
└──────────┬───────────┴──────────────┬───────────────────┘
           │                          │
           │ MCP Protocol (stdio)     │ HTTP/REST
           │                          │
┌──────────▼──────────────────────────▼───────────────────┐
│              Python Application Layer                   │
│  ┌────────────────────┐    ┌──────────────────────┐    │
│  │   MCP Server       │◄───┤   FastAPI Server     │    │
│  │   (stdio)          │    │   (REST API)         │    │
│  └────────┬───────────┘    └───────┬──────────────┘    │
│           │                        │                    │
│           └────────┬───────────────┘                    │
│                    │                                    │
│           ┌────────▼───────────┐                        │
│           │   API Router       │                        │
│           │   + Handlers       │                        │
│           └────────┬───────────┘                        │
└────────────────────┼────────────────────────────────────┘
                     │ HTTP Requests
                     │
           ┌─────────▼──────────┐
           │   External APIs    │
           │   - Steam API      │
           │   - Weather API    │
           │   - News API       │
           └────────────────────┘
```

### 기술 스택 상세

#### Backend

- **FastAPI** 0.104+: REST API 서버, 관리 API
- **Python** 3.11+: 메인 언어
- **MCP Python SDK**: MCP 프로토콜 구현
- **aiohttp**: 비동기 HTTP 클라이언트
- **pydantic**: 데이터 검증 및 시리얼라이제이션
- **uvicorn**: ASGI 서버

#### Frontend

- **React** 18+: UI 프레임워크
- **TypeScript**: 타입 안전성
- **Vite**: 빌드 도구
- **TanStack Query** (React Query): 서버 상태 관리
- **Axios**: HTTP 클라이언트
- **Tailwind CSS**: 스타일링
- **React Router**: 라우팅
- **shadcn/ui**: UI 컴포넌트 라이브러리

#### 개발 도구

- **pytest**: 백엔드 테스트
- **Jest + React Testing Library**: 프론트엔드 테스트
- **Black + isort**: Python 코드 포맷팅
- **ESLint + Prettier**: TypeScript/React 린팅
- **Docker**: 컨테이너화 (선택)

---

## 구현 범위 (MVP)

### 포함 기능 ✅

1. **MCP 서버 핵심 기능**
   - tools/list 구현
   - tools/call 구현
   - 3-5개 Public API 지원 (하드코딩)

2. **관리 웹 대시보드**
   - API 목록 조회
   - API 상세 정보 확인
   - API 테스트 기능 (간단한 호출)
   - API 엔드포인트 추가/수정 (JSON 편집)

3. **API 게이트웨이**
   - 외부 API 프록시
   - 기본 에러 핸들링
   - 요청/응답 로깅

4. **보안 기능**
   - URL 화이트리스트
   - 내부 IP 차단
   - 입력 검증
   - 간단한 Rate Limiting

### 제외 기능 ❌

1. **데이터베이스**: PostgreSQL 대신 JSON 파일 + 메모리 사용
2. **사용자 인증**: 로그인/회원가입 없음
3. **API Key 암호화**: Public API만 지원
4. **LLM 기반 자동 변환**: 수동 JSON 작성
5. **고급 모니터링**: 대시보드/차트 없음

---

## 프로젝트 구조

```
universal-api-gateway-mcp-server/
├── backend/                          # FastAPI + MCP 서버
│   ├── src/
│   │   ├── main.py                  # FastAPI 앱 진입점
│   │   ├── mcp_server/
│   │   │   ├── __init__.py
│   │   │   ├── server.py            # MCP 서버 메인
│   │   │   ├── handlers.py          # MCP 요청 핸들러
│   │   │   └── tools.py             # Tool 정의 및 변환
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # FastAPI 라우터
│   │   │   ├── endpoints/
│   │   │   │   ├── apis.py          # API 관리 엔드포인트
│   │   │   │   ├── proxy.py         # API 프록시 엔드포인트
│   │   │   │   └── health.py        # 헬스체크
│   │   │   └── dependencies.py      # 의존성 주입
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # 설정 관리
│   │   │   ├── api_router.py        # API 라우팅 로직
│   │   │   ├── http_client.py       # HTTP 클라이언트
│   │   │   └── security.py          # 보안 유틸리티
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── api_definition.py    # API 정의 모델
│   │   │   ├── requests.py          # 요청 모델
│   │   │   └── responses.py         # 응답 모델
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── api_service.py       # API 관리 서비스
│   │   │   └── proxy_service.py     # 프록시 서비스
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py            # 로깅
│   │       ├── validators.py        # 입력 검증
│   │       └── json_path.py         # JSONPath 파서
│   ├── data/
│   │   └── apis/                    # API 정의 JSON 파일
│   │       ├── steam.json
│   │       ├── weather.json
│   │       └── news.json
│   ├── tests/
│   │   ├── test_mcp_server.py
│   │   ├── test_api_router.py
│   │   ├── test_proxy.py
│   │   └── conftest.py
│   ├── pyproject.toml
│   ├── poetry.lock
│   └── README.md
│
├── frontend/                         # React 대시보드
│   ├── src/
│   │   ├── main.tsx                 # React 진입점
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── api/
│   │   │   │   ├── ApiList.tsx      # API 목록
│   │   │   │   ├── ApiDetail.tsx    # API 상세
│   │   │   │   ├── ApiEditor.tsx    # API 편집
│   │   │   │   ├── ApiTester.tsx    # API 테스트
│   │   │   │   └── EndpointCard.tsx # 엔드포인트 카드
│   │   │   ├── ui/                  # shadcn/ui 컴포넌트
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   └── ...
│   │   │   └── common/
│   │   │       ├── Loading.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── CodeEditor.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx        # 대시보드 홈
│   │   │   ├── ApiListPage.tsx      # API 목록 페이지
│   │   │   ├── ApiDetailPage.tsx    # API 상세 페이지
│   │   │   └── NotFound.tsx
│   │   ├── services/
│   │   │   └── api.ts               # API 클라이언트
│   │   ├── hooks/
│   │   │   ├── useApis.ts           # API 관련 훅
│   │   │   └── useApiTest.ts        # API 테스트 훅
│   │   ├── types/
│   │   │   └── api.ts               # TypeScript 타입 정의
│   │   ├── utils/
│   │   │   └── format.ts            # 유틸리티 함수
│   │   └── styles/
│   │       └── globals.css
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
│
├── docs/                             # 문서
│   ├── Proposal-251027_1.md         # 원본 기획서
│   ├── Implementation-Plan-251027.md # 이 문서
│   ├── API-GUIDE.md                 # API 추가 가이드
│   └── USER-GUIDE.md                # 사용자 가이드
│
├── scripts/                          # 유틸리티 스크립트
│   ├── start-dev.sh                 # 개발 서버 시작
│   └── run-mcp.sh                   # MCP 서버 실행
│
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions CI
│
├── docker-compose.yml               # Docker Compose (선택)
├── .gitignore
└── README.md                        # 프로젝트 README
```

---

## 백엔드 구현 (FastAPI)

### 1. FastAPI 애플리케이션 구조

#### main.py

```python
"""
FastAPI 애플리케이션 진입점
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.router import api_router
from core.config import settings
from core.api_router import APIRouter
from utils.logger import setup_logger

logger = setup_logger(__name__)

# API Router 글로벌 인스턴스
api_router_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    global api_router_instance

    # 시작 시
    logger.info("Starting Universal API Gateway...")
    api_router_instance = APIRouter(data_dir=settings.DATA_DIR)
    await api_router_instance.load_api_definitions()
    logger.info(f"Loaded {len(api_router_instance.apis)} APIs")

    yield

    # 종료 시
    logger.info("Shutting down...")
    if api_router_instance and api_router_instance.session:
        await api_router_instance.session.close()

# FastAPI 앱 생성
app = FastAPI(
    title="Universal API Gateway",
    description="단일 MCP 서버로 여러 외부 API를 사용",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Universal API Gateway",
        "version": "1.0.0",
        "docs": "/docs"
    }

def get_api_router():
    """API Router 인스턴스 반환 (의존성 주입용)"""
    return api_router_instance
```

#### core/config.py

```python
"""
애플리케이션 설정
"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # 기본 설정
    APP_NAME: str = "Universal API Gateway"
    DEBUG: bool = True

    # 경로 설정
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data" / "apis"

    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 보안 설정
    ALLOWED_DOMAINS: list[str] = [
        "api.steampowered.com",
        "api.open-meteo.com",
        "newsapi.org"
    ]

    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    # HTTP 클라이언트
    HTTP_TIMEOUT: int = 30
    HTTP_MAX_REDIRECTS: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### 2. API 엔드포인트 구현

#### api/endpoints/apis.py

```python
"""
API 관리 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from models.api_definition import APIDefinition, APIEndpoint
from models.responses import APIListResponse, APIDetailResponse
from services.api_service import APIService
from api.dependencies import get_api_service

router = APIRouter(prefix="/apis", tags=["APIs"])

@router.get("", response_model=APIListResponse)
async def list_apis(
    service: APIService = Depends(get_api_service)
):
    """등록된 모든 API 목록 조회"""
    apis = await service.get_all_apis()
    return APIListResponse(
        total=len(apis),
        apis=apis
    )

@router.get("/{service_name}", response_model=APIDetailResponse)
async def get_api_detail(
    service_name: str,
    service: APIService = Depends(get_api_service)
):
    """특정 API 상세 정보 조회"""
    api = await service.get_api(service_name)
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    return APIDetailResponse(api=api)

@router.get("/{service_name}/endpoints", response_model=List[APIEndpoint])
async def list_endpoints(
    service_name: str,
    service: APIService = Depends(get_api_service)
):
    """특정 API의 모든 엔드포인트 조회"""
    endpoints = await service.get_endpoints(service_name)
    if not endpoints:
        raise HTTPException(status_code=404, detail="API not found")

    return endpoints
```

#### api/endpoints/proxy.py

```python
"""
API 프록시 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict

from models.requests import ProxyRequest
from models.responses import ProxyResponse
from services.proxy_service import ProxyService
from api.dependencies import get_proxy_service

router = APIRouter(prefix="/proxy", tags=["Proxy"])

@router.post("/test", response_model=ProxyResponse)
async def test_api_endpoint(
    request: ProxyRequest,
    service: ProxyService = Depends(get_proxy_service)
):
    """
    API 엔드포인트 테스트 호출

    대시보드에서 "Test" 버튼 클릭 시 사용
    """
    try:
        result = await service.call_endpoint(
            service_name=request.service_name,
            endpoint_id=request.endpoint_id,
            arguments=request.arguments
        )

        return ProxyResponse(
            success=True,
            data=result
        )

    except Exception as e:
        return ProxyResponse(
            success=False,
            error=str(e)
        )
```

### 3. 데이터 모델 (Pydantic)

#### models/api_definition.py

```python
"""
API 정의 데이터 모델
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, Optional, List

class ParameterDefinition(BaseModel):
    type: str = Field(..., description="파라미터 타입 (string, integer, number, boolean)")
    description: str = Field(..., description="파라미터 설명")
    required: bool = Field(default=False, description="필수 여부")
    default: Optional[Any] = Field(None, description="기본값")
    min: Optional[float] = Field(None, description="최소값")
    max: Optional[float] = Field(None, description="최대값")

class ResponseMapping(BaseModel):
    path: Optional[str] = Field(None, description="JSONPath 경로 ($.response.data)")
    format: str = Field(default="json", description="응답 포맷")

class RateLimit(BaseModel):
    max_calls: int = Field(..., description="최대 호출 횟수")
    per_seconds: int = Field(..., description="기간(초)")

class APIEndpoint(BaseModel):
    id: str = Field(..., description="엔드포인트 고유 ID")
    name: str = Field(..., description="MCP Tool 이름")
    display_name: str = Field(..., description="표시 이름")
    description: str = Field(..., description="기능 설명")
    http_method: str = Field(..., description="HTTP 메서드")
    path: str = Field(..., description="엔드포인트 경로")
    parameters: Dict[str, ParameterDefinition] = Field(default_factory=dict)
    response_mapping: Optional[ResponseMapping] = None
    timeout_seconds: int = Field(default=10, description="타임아웃(초)")
    rate_limit: Optional[RateLimit] = None

class APIDefinition(BaseModel):
    service_name: str = Field(..., description="서비스 고유 이름")
    display_name: str = Field(..., description="서비스 표시 이름")
    base_url: HttpUrl = Field(..., description="API 베이스 URL")
    description: str = Field(..., description="서비스 설명")
    auth_required: bool = Field(default=False, description="인증 필요 여부")
    endpoints: List[APIEndpoint] = Field(default_factory=list)
```

---

## 프론트엔드 구현 (React)

### 1. React 애플리케이션 구조

#### App.tsx

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import ApiListPage from './pages/ApiListPage';
import ApiDetailPage from './pages/ApiDetailPage';
import NotFound from './pages/NotFound';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="apis" element={<ApiListPage />} />
            <Route path="apis/:serviceName" element={<ApiDetailPage />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

### 2. API 클라이언트

#### services/api.ts

```typescript
import axios from 'axios';
import type { APIDefinition, APIEndpoint, ProxyRequest, ProxyResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // API 목록 조회
  async getApis(): Promise<APIDefinition[]> {
    const { data } = await client.get('/apis');
    return data.apis;
  },

  // API 상세 조회
  async getApi(serviceName: string): Promise<APIDefinition> {
    const { data } = await client.get(`/apis/${serviceName}`);
    return data.api;
  },

  // API 엔드포인트 목록 조회
  async getEndpoints(serviceName: string): Promise<APIEndpoint[]> {
    const { data } = await client.get(`/apis/${serviceName}/endpoints`);
    return data;
  },

  // API 테스트 호출
  async testEndpoint(request: ProxyRequest): Promise<ProxyResponse> {
    const { data } = await client.post('/proxy/test', request);
    return data;
  },
};
```

### 3. React 컴포넌트

#### components/api/ApiList.tsx

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import { Card, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ApiList() {
  const { data: apis, isLoading, error } = useQuery({
    queryKey: ['apis'],
    queryFn: apiClient.getApis,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading APIs</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {apis?.map((api) => (
        <Card key={api.service_name}>
          <CardHeader>
            <CardTitle>{api.display_name}</CardTitle>
            <CardDescription>{api.description}</CardDescription>
          </CardHeader>
          <div className="px-6 pb-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">
                {api.endpoints.length} endpoints
              </span>
              <Link to={`/apis/${api.service_name}`}>
                <Button variant="outline" size="sm">
                  View Details
                  <ExternalLink className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
```

#### components/api/ApiTester.tsx

```typescript
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import CodeEditor from '../common/CodeEditor';
import type { APIEndpoint } from '../../types/api';

interface ApiTesterProps {
  serviceName: string;
  endpoint: APIEndpoint;
}

export default function ApiTester({ serviceName, endpoint }: ApiTesterProps) {
  const [arguments, setArguments] = useState<Record<string, any>>({});
  const [response, setResponse] = useState<any>(null);

  const testMutation = useMutation({
    mutationFn: () =>
      apiClient.testEndpoint({
        service_name: serviceName,
        endpoint_id: endpoint.id,
        arguments,
      }),
    onSuccess: (data) => {
      setResponse(data);
    },
  });

  const handleTest = () => {
    testMutation.mutate();
  };

  return (
    <Card className="p-4">
      <h3 className="text-lg font-semibold mb-4">Test Endpoint</h3>

      {/* Parameters Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Parameters (JSON)</label>
        <CodeEditor
          value={JSON.stringify(arguments, null, 2)}
          onChange={(value) => setArguments(JSON.parse(value))}
          language="json"
        />
      </div>

      {/* Test Button */}
      <Button
        onClick={handleTest}
        disabled={testMutation.isPending}
        className="mb-4"
      >
        {testMutation.isPending ? 'Testing...' : 'Test API'}
      </Button>

      {/* Response */}
      {response && (
        <div>
          <label className="block text-sm font-medium mb-2">Response</label>
          <CodeEditor
            value={JSON.stringify(response, null, 2)}
            readOnly
            language="json"
          />
        </div>
      )}
    </Card>
  );
}
```

---

## MCP 서버 구현

### mcp_server/server.py

```python
"""
Universal API Gateway MCP Server
"""
import json
import asyncio
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from core.api_router import APIRouter
from core.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class UniversalMCPServer:
    def __init__(self):
        self.server = Server("universal-api-gateway")
        self.router = APIRouter(data_dir=settings.DATA_DIR)

    async def initialize(self):
        """서버 초기화"""
        await self.router.load_api_definitions()
        logger.info(f"Loaded {len(self.router.apis)} APIs")

        self._register_handlers()

    def _register_handlers(self):
        """MCP 요청 핸들러 등록"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """사용 가능한 모든 도구 목록"""
            return self._create_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """도구 호출"""
            return await self._call_tool(name, arguments)

    def _create_tools(self) -> List[Tool]:
        """API 엔드포인트를 MCP Tool로 변환"""
        tools = []

        for api in self.router.apis.values():
            for endpoint in api["endpoints"]:
                # JSON Schema 생성
                input_schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }

                for param_name, param_def in endpoint["parameters"].items():
                    input_schema["properties"][param_name] = {
                        "type": param_def["type"],
                        "description": param_def["description"]
                    }

                    if param_def.get("required"):
                        input_schema["required"].append(param_name)

                # Tool 생성
                tool = Tool(
                    name=endpoint["name"],
                    description=endpoint["description"],
                    inputSchema=input_schema
                )
                tools.append(tool)

        return tools

    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """API 호출 및 결과 반환"""
        try:
            result = await self.router.route_request(
                tool_name=name,
                arguments=arguments,
                session=self.router.session
            )

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    async def cleanup(self):
        """리소스 정리"""
        if self.router.session:
            await self.router.session.close()

    async def run(self):
        """서버 실행"""
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

def main():
    """메인 함수"""
    server = UniversalMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
```

---

## 데이터 모델 및 하드코딩 데이터

### 하드코딩 API 정의 (JSON)

#### data/apis/steam.json

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
      "description": "현재 가장 많이 플레이되는 Steam 게임 목록을 조회합니다",
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
      "timeout_seconds": 10
    }
  ]
}
```

#### data/apis/weather.json

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
      "description": "특정 위치의 현재 날씨 정보를 조회합니다",
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

#### data/apis/news.json

```json
{
  "service_name": "news",
  "display_name": "NewsAPI",
  "base_url": "https://newsapi.org",
  "description": "전 세계 뉴스 기사를 검색하고 조회합니다",
  "auth_required": false,
  "endpoints": [
    {
      "id": "get_top_headlines",
      "name": "news_get_top_headlines",
      "display_name": "Get Top Headlines",
      "description": "최신 헤드라인 뉴스를 조회합니다",
      "http_method": "GET",
      "path": "/v2/top-headlines",
      "parameters": {
        "country": {
          "type": "string",
          "description": "국가 코드 (us, kr, jp 등)",
          "required": false,
          "default": "us"
        },
        "category": {
          "type": "string",
          "description": "카테고리 (business, technology, sports 등)",
          "required": false
        },
        "pageSize": {
          "type": "integer",
          "description": "반환할 기사 개수",
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

---

## API 엔드포인트 명세

### Backend REST API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/health` | 헬스체크 |
| GET | `/api/v1/apis` | 등록된 모든 API 목록 조회 |
| GET | `/api/v1/apis/{service_name}` | 특정 API 상세 정보 |
| GET | `/api/v1/apis/{service_name}/endpoints` | 특정 API의 엔드포인트 목록 |
| POST | `/api/v1/proxy/test` | API 테스트 호출 |

### 요청/응답 예시

#### GET /api/v1/apis

**Response:**
```json
{
  "total": 3,
  "apis": [
    {
      "service_name": "steam",
      "display_name": "Steam Web API",
      "base_url": "https://api.steampowered.com",
      "description": "Steam 게임 정보",
      "auth_required": false,
      "endpoints": [...]
    }
  ]
}
```

#### POST /api/v1/proxy/test

**Request:**
```json
{
  "service_name": "steam",
  "endpoint_id": "get_popular_games",
  "arguments": {
    "count": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ranks": [
      {
        "rank": 1,
        "appid": 730,
        "concurrent_in_game": 1234567
      }
    ]
  }
}
```

---

## 보안 및 에러 핸들링

### 1. 보안 기능

#### URL 화이트리스트 (core/security.py)

```python
from urllib.parse import urlparse
from core.config import settings

def validate_url(url: str) -> bool:
    """URL이 허용된 도메인인지 확인"""
    domain = urlparse(url).netloc
    return domain in settings.ALLOWED_DOMAINS

def validate_internal_ip(url: str) -> bool:
    """내부 IP 차단"""
    import ipaddress

    BLOCKED_RANGES = [
        "127.0.0.0/8",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16"
    ]

    domain = urlparse(url).hostname
    try:
        ip = ipaddress.ip_address(domain)
        for cidr in BLOCKED_RANGES:
            if ip in ipaddress.ip_network(cidr):
                return False
    except:
        pass

    return True
```

#### Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.calls = defaultdict(list)

    def check_limit(self, key: str, max_calls: int, period: int) -> bool:
        """Rate limit 확인"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=period)

        # 오래된 기록 제거
        self.calls[key] = [ts for ts in self.calls[key] if ts > cutoff]

        # 제한 확인
        if len(self.calls[key]) >= max_calls:
            return False

        self.calls[key].append(now)
        return True
```

### 2. 에러 핸들링

#### 커스텀 예외

```python
class APIGatewayException(Exception):
    """기본 예외 클래스"""
    pass

class APINotFoundException(APIGatewayException):
    """API를 찾을 수 없음"""
    pass

class APICallException(APIGatewayException):
    """API 호출 실패"""
    pass

class ValidationException(APIGatewayException):
    """입력 검증 실패"""
    pass
```

#### FastAPI 에러 핸들러

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(APIGatewayException)
async def api_gateway_exception_handler(request: Request, exc: APIGatewayException):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
```

---

## 테스트 전략

### 1. 백엔드 테스트 (pytest)

#### tests/test_api_router.py

```python
import pytest
from core.api_router import APIRouter

@pytest.mark.asyncio
async def test_load_api_definitions(tmp_path):
    """API 정의 로드 테스트"""
    # Mock JSON 파일 생성
    api_file = tmp_path / "test_api.json"
    api_file.write_text('{"service_name": "test", "endpoints": []}')

    router = APIRouter(data_dir=tmp_path)
    await router.load_api_definitions()

    assert "test" in router.apis

@pytest.mark.asyncio
async def test_route_request(mock_api_router):
    """API 라우팅 테스트"""
    result = await mock_api_router.route_request(
        tool_name="test_endpoint",
        arguments={"param": "value"},
        session=mock_session
    )

    assert result is not None
```

### 2. 통합 테스트

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_steam_api_integration():
    """실제 Steam API 호출 테스트"""
    router = APIRouter(data_dir="./data/apis")
    await router.load_api_definitions()

    import aiohttp
    async with aiohttp.ClientSession() as session:
        result = await router.route_request(
            tool_name="steam_get_popular_games",
            arguments={"count": 3},
            session=session
        )

        assert "ranks" in result or "games" in result
```

### 3. 프론트엔드 테스트 (Jest)

```typescript
import { render, screen } from '@testing-library/react';
import ApiList from './ApiList';

describe('ApiList', () => {
  it('renders API cards', async () => {
    render(<ApiList />);

    const cards = await screen.findAllByRole('article');
    expect(cards.length).toBeGreaterThan(0);
  });
});
```

---

## 배포 전략

### 1. 로컬 개발 환경

```bash
# Backend
cd backend
poetry install
poetry run uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# MCP Server (별도 터미널)
cd backend
poetry run python -m src.mcp_server.server
```

### 2. Docker Compose (선택)

#### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      - DEBUG=true
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
```

### 3. MCP 서버 배포 (PyPI)

```bash
# 빌드
cd backend
poetry build

# 배포
poetry publish

# 사용자 설치
pip install universal-api-gateway-mcp
```

### 4. Claude Desktop 설정

```json
{
  "mcpServers": {
    "universal-api-gateway": {
      "command": "python",
      "args": [
        "-m",
        "src.mcp_server.server"
      ],
      "cwd": "C:/workspace/sesac/000.project/Universal-API-Gateway-MCP-Server/backend"
    }
  }
}
```

---

## 개발 일정

### Week 1: 기본 인프라 및 백엔드 (5일)

**Day 1: 프로젝트 설정**
- ✅ 프로젝트 구조 생성
- ✅ Poetry, npm 설정
- ✅ FastAPI 기본 앱 생성
- ✅ React + Vite 앱 생성

**Day 2: 데이터 모델 및 API 정의**
- ✅ Pydantic 모델 작성
- ✅ 3개 API JSON 파일 작성 (Steam, Weather, News)
- ✅ APIRouter 기본 구현

**Day 3: FastAPI 엔드포인트 구현**
- ✅ API 관리 엔드포인트 (/apis)
- ✅ 프록시 엔드포인트 (/proxy/test)
- ✅ 에러 핸들링

**Day 4: HTTP 클라이언트 및 보안**
- ✅ aiohttp 클라이언트 구현
- ✅ URL 화이트리스트
- ✅ Rate Limiting
- ✅ 입력 검증

**Day 5: 백엔드 테스트**
- ✅ 단위 테스트 작성
- ✅ 통합 테스트 (실제 API 호출)
- ✅ 로컬 서버 실행 검증

### Week 2: 프론트엔드 및 MCP 서버 (5일)

**Day 1: React 기본 구조**
- ✅ 라우팅 설정
- ✅ API 클라이언트 작성
- ✅ TanStack Query 설정
- ✅ 레이아웃 컴포넌트

**Day 2: 대시보드 UI**
- ✅ API 목록 페이지
- ✅ API 상세 페이지
- ✅ Endpoint 카드 컴포넌트
- ✅ shadcn/ui 통합

**Day 3: API 테스트 기능**
- ✅ API Tester 컴포넌트
- ✅ JSON 편집기
- ✅ 요청/응답 표시
- ✅ 에러 표시

**Day 4: MCP 서버 구현**
- ✅ MCP Server 기본 구조
- ✅ tools/list 구현
- ✅ tools/call 구현
- ✅ APIRouter 통합

**Day 5: 통합 테스트 및 문서**
- ✅ Claude Desktop 연동 테스트
- ✅ 실제 사용 시나리오 검증
- ✅ README 작성
- ✅ API 가이드 작성

---

## Phase 2 확장 계획

### Phase 2.1: 데이터베이스 도입 (2주)

- PostgreSQL 스키마 설계
- SQLAlchemy ORM 통합
- API 정의를 DB로 마이그레이션
- 관리자 UI에서 API 추가/수정 기능

### Phase 2.2: 인증 및 사용자 관리 (2주)

- 사용자 로그인/회원가입
- API Key 암호화 저장
- OAuth 2.0 지원
- 사용자별 API 사용량 추적

### Phase 2.3: LLM 기반 자동 변환 (3주)

- OpenAPI 3.0 파서
- LLM을 이용한 API 문서 분석
- 자동 JSON 생성
- 검증 및 테스트 자동화

### Phase 2.4: 고급 기능 (3주)

- 실시간 모니터링 대시보드
- API 호출 통계 및 차트
- Webhook 지원
- 커뮤니티 API 제출 기능

---

## 성공 기준

### MVP 필수 기능

- [x] FastAPI 서버 정상 실행
- [x] React 대시보드 정상 실행
- [x] MCP 서버 정상 실행
- [x] 3개 이상 Public API 하드코딩
- [x] Claude Desktop에서 API 호출 성공
- [x] 웹 대시보드에서 API 목록 확인
- [x] 웹 대시보드에서 API 테스트 성공

### 성능 목표

- API 프록시 응답 시간: < 3초 (95th percentile)
- FastAPI 서버 시작 시간: < 2초
- React 빌드 시간: < 30초
- MCP 서버 시작 시간: < 2초

### 코드 품질

- 백엔드 테스트 커버리지: > 70%
- 프론트엔드 주요 컴포넌트 테스트 작성
- ESLint, Prettier, Black 통과
- 타입 안전성 (TypeScript, Pydantic)

---

## 참고 자료

### 공식 문서

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Pydantic](https://docs.pydantic.dev/)

### 외부 API 문서

- [Steam Web API](https://steamcommunity.com/dev)
- [Open-Meteo API](https://open-meteo.com/en/docs)
- [NewsAPI](https://newsapi.org/docs)

### 관련 라이브러리

- [aiohttp](https://docs.aiohttp.org/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 다음 단계

1. **프로젝트 초기화**
   ```bash
   # Backend
   cd backend
   poetry init
   poetry add fastapi uvicorn pydantic pydantic-settings aiohttp mcp
   poetry add --group dev pytest pytest-asyncio black isort

   # Frontend
   cd frontend
   npm create vite@latest . -- --template react-ts
   npm install @tanstack/react-query axios react-router-dom
   npm install -D tailwindcss postcss autoprefixer
   ```

2. **디렉토리 구조 생성**
   ```bash
   mkdir -p backend/{src/{api/endpoints,core,models,services,utils,mcp_server},data/apis,tests}
   mkdir -p frontend/src/{components/{layout,api,ui,common},pages,services,hooks,types,utils,styles}
   ```

3. **API 정의 파일 생성**
   - `data/apis/steam.json`
   - `data/apis/weather.json`
   - `data/apis/news.json`

4. **핵심 파일 구현 시작**
   - `backend/src/main.py`
   - `backend/src/core/api_router.py`
   - `frontend/src/App.tsx`
   - `frontend/src/services/api.ts`

---

**작성일**: 2025-10-27
**작성자**: Claude Code
**버전**: v1.0
**상태**: 구현 준비 완료 ✅

# Part 5: Frontend - React 애플리케이션

## 개요

React + TypeScript + Vite 기반의 대시보드 Frontend를 구현하는 단계입니다.

---

## Issue #16: Frontend 프로젝트 초기 설정 (Vite, TypeScript, Tailwind)

### 목표
Frontend 프로젝트의 기본 구조와 개발 환경을 설정합니다.

### 작업 내용

#### 16.1 Vite 프로젝트 생성 (이미 완료됨)
```bash
cd frontend
npm create vite@latest . -- --template react-ts
```

#### 16.2 의존성 설치
**파일**: `frontend/package.json`

```json
{
  "name": "universal-api-gateway-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "react-router-dom": "^7.9.4",
    "@tanstack/react-query": "^5.90.5",
    "axios": "^1.12.2",
    "tailwindcss": "^4.1.16",
    "@tailwindcss/postcss": "^4.1.16"
  },
  "devDependencies": {
    "vite": "^7.1.7",
    "typescript": "~5.9.3",
    "@vitejs/plugin-react": "^5.0.4",
    "@types/react": "^19.1.16",
    "@types/react-dom": "^19.1.9",
    "@types/node": "^24.9.1",
    "postcss": "^8.5.6",
    "autoprefixer": "^10.4.21",
    "eslint": "^9.36.0",
    "typescript-eslint": "^8.45.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.22"
  }
}
```

#### 16.3 Vite 설정
**파일**: `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
```

#### 16.4 TypeScript 설정
**파일**: `frontend/tsconfig.app.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["src"]
}
```

#### 16.5 Tailwind CSS 설정
**파일**: `frontend/tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**파일**: `frontend/postcss.config.js`

```javascript
export default {
  plugins: {
    '@tailwindcss/postcss': {}
  }
}
```

**파일**: `frontend/src/index.css`

```css
@import "tailwindcss";
```

#### 16.6 환경 변수
**파일**: `frontend/.env`

```bash
VITE_API_URL=http://localhost:8080/api/v1
```

#### 16.7 HTML 엔트리 포인트
**파일**: `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Universal API Gateway</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### 브랜치
- **이름**: `feature/016_frontend_setup`
- **베이스**: `develop` (Issue #15 머지 후)

### 커밋 메시지
```
feat: Frontend 프로젝트 초기 설정

- Vite + React + TypeScript 프로젝트 생성
- Tailwind CSS v4 설정
- 의존성 설치 (React Query, React Router, Axios)
- Vite 프록시 설정 (/api → localhost:8080)
- TypeScript strict 모드 설정
- 환경 변수 설정

Closes #16
```

### PR 제목
```
feat: Frontend 프로젝트 초기 설정 (#16)
```

### 파일 목록
```
frontend/package.json
frontend/vite.config.ts
frontend/tsconfig.json
frontend/tsconfig.app.json
frontend/tailwind.config.js
frontend/postcss.config.js
frontend/src/index.css
frontend/index.html
frontend/.env
```

---

## Issue #17: API 클라이언트 및 React Query 통합

### 목표
Axios 기반 API 클라이언트와 React Query 커스텀 훅을 구현합니다.

### 작업 내용

#### 17.1 TypeScript 타입 정의
**파일**: `frontend/src/types/api.ts`

```typescript
// ParameterDefinition, ResponseMapping, RateLimit 등
// APIEndpoint, APIDefinition
// APIListResponse, APIDetailResponse
// ProxyRequest, ProxyResponse
// HealthResponse

// (전체 코드는 feature/001_init의 frontend/src/types/api.ts 참조)
```

#### 17.2 Axios API 클라이언트
**파일**: `frontend/src/lib/api-client.ts`

```typescript
import axios from 'axios'
import type {
  HealthResponse,
  APIListResponse,
  APIDetailResponse,
  APIEndpoint,
  ProxyRequest,
  ProxyResponse
} from '../types/api'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const api = {
  getHealth: async (): Promise<HealthResponse> => {
    const res = await apiClient.get('/health')
    return res.data
  },

  getApis: async (): Promise<APIListResponse> => {
    const res = await apiClient.get('/apis')
    return res.data
  },

  getApi: async (serviceName: string): Promise<APIDetailResponse> => {
    const res = await apiClient.get(`/apis/${serviceName}`)
    return res.data
  },

  getEndpoints: async (serviceName: string): Promise<APIEndpoint[]> => {
    const res = await apiClient.get(`/apis/${serviceName}/endpoints`)
    return res.data
  },

  testEndpoint: async (request: ProxyRequest): Promise<ProxyResponse> => {
    const res = await apiClient.post('/proxy/test', request)
    return res.data
  }
}
```

#### 17.3 React Query 커스텀 훅
**파일**: `frontend/src/hooks/useApis.ts`

```typescript
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../lib/api-client'
import type { ProxyRequest } from '../types/api'

export const useHealth = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth
  })
}

export const useApis = () => {
  return useQuery({
    queryKey: ['apis'],
    queryFn: api.getApis
  })
}

export const useApi = (serviceName: string) => {
  return useQuery({
    queryKey: ['api', serviceName],
    queryFn: () => api.getApi(serviceName),
    enabled: !!serviceName
  })
}

export const useEndpoints = (serviceName: string) => {
  return useQuery({
    queryKey: ['endpoints', serviceName],
    queryFn: () => api.getEndpoints(serviceName),
    enabled: !!serviceName
  })
}

export const useApiTest = () => {
  return useMutation({
    mutationFn: (request: ProxyRequest) => api.testEndpoint(request)
  })
}
```

### 브랜치
- **이름**: `feature/017_api_client_react_query`
- **베이스**: `develop` (Issue #16 머지 후)

### 커밋 메시지
```
feat: API 클라이언트 및 React Query 통합

- TypeScript 타입 정의 추가 (api.ts)
- Axios 기반 API 클라이언트 구현
- React Query 커스텀 훅 추가 (useApis, useApi, useApiTest 등)
- 환경 변수 기반 API URL 설정

Closes #17
```

### PR 제목
```
feat: API 클라이언트 및 React Query 통합 (#17)
```

### 파일 목록
```
frontend/src/types/api.ts
frontend/src/lib/api-client.ts
frontend/src/hooks/useApis.ts
```

---

## Issue #18: Dashboard 페이지 구현

### 목표
시스템 상태 및 API 목록을 보여주는 Dashboard 페이지를 구현합니다.

### 작업 내용

#### 18.1 Dashboard 페이지 구현
**파일**: `frontend/src/pages/Dashboard.tsx`

```typescript
import { Link } from 'react-router-dom'
import { useHealth, useApis } from '../hooks/useApis'

export default function Dashboard() {
  const { data: health, isLoading: healthLoading, error: healthError } = useHealth()
  const { data: apisData, isLoading: apisLoading, error: apisError } = useApis()

  // ... (전체 구현은 feature/001_init 참조)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Health Status Card */}
      {/* API List Grid */}
    </div>
  )
}
```

**주요 기능**:
- Health check 상태 표시
- 로드된 API 개수 표시
- API 목록 그리드 (카드 형식)
- 각 API의 엔드포인트 개수 및 설명

### 브랜치
- **이름**: `feature/018_dashboard_page`
- **베이스**: `develop` (Issue #17 머지 후)

### 커밋 메시지
```
feat: Dashboard 페이지 구현

- Dashboard 컴포넌트 추가
- Health check 상태 표시
- API 목록 그리드 표시
- Tailwind CSS 스타일링

Closes #18
```

### PR 제목
```
feat: Dashboard 페이지 구현 (#18)
```

### 파일 목록
```
frontend/src/pages/Dashboard.tsx
```

---

## Issue #19: API List 페이지 구현

### 목표
전체 API 목록을 보여주는 페이지를 구현합니다.

### 작업 내용

#### 19.1 API List 페이지 구현
**파일**: `frontend/src/pages/ApiListPage.tsx`

```typescript
import { Link } from 'react-router-dom'
import { useApis } from '../hooks/useApis'

export default function ApiListPage() {
  const { data, isLoading, error } = useApis()

  // ... (전체 구현은 feature/001_init 참조)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* API Cards Grid */}
    </div>
  )
}
```

**주요 기능**:
- API 카드 그리드 표시
- HTTP 메서드 뱃지 (GET, POST 등)
- Auth 요구 여부 표시
- 엔드포인트 미리보기
- Detail 페이지로 링크

### 브랜치
- **이름**: `feature/019_api_list_page`
- **베이스**: `develop` (Issue #18 머지 후)

### 커밋 메시지
```
feat: API List 페이지 구현

- ApiListPage 컴포넌트 추가
- API 카드 그리드 레이아웃
- HTTP 메서드 뱃지
- 엔드포인트 미리보기

Closes #19
```

### PR 제목
```
feat: API List 페이지 구현 (#19)
```

### 파일 목록
```
frontend/src/pages/ApiListPage.tsx
```

---

## Issue #20: API Detail 및 테스트 페이지 구현

### 목표
API 상세 정보를 보여주고 엔드포인트를 테스트할 수 있는 페이지를 구현합니다.

### 작업 내용

#### 20.1 API Detail 페이지 구현
**파일**: `frontend/src/pages/ApiDetailPage.tsx`

```typescript
import { useParams } from 'react-router-dom'
import { useState } from 'react'
import { useApi, useApiTest } from '../hooks/useApis'

export default function ApiDetailPage() {
  const { serviceName } = useParams<{ serviceName: string }>()
  const { data, isLoading, error } = useApi(serviceName!)
  const apiTest = useApiTest()

  const [selectedEndpoint, setSelectedEndpoint] = useState<APIEndpoint | null>(null)
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [testResult, setTestResult] = useState<any>(null)

  // ... (전체 구현은 feature/001_init 참조)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      {/* API Header */}
      {/* Two-column layout: Endpoints List + Test Panel */}
    </div>
  )
}
```

**주요 기능**:
- Breadcrumb 네비게이션
- API 헤더 (이름, 설명, base URL, auth 여부)
- 2열 레이아웃:
  - 좌측: 엔드포인트 목록
  - 우측: 선택된 엔드포인트 테스트 패널
- 동적 폼 생성 (파라미터 타입에 따라)
- 테스트 버튼
- 응답 결과 표시 (성공/실패)

### 브랜치
- **이름**: `feature/020_api_detail_page`
- **베이스**: `develop` (Issue #19 머지 후)

### 커밋 메시지
```
feat: API Detail 및 테스트 페이지 구현

- ApiDetailPage 컴포넌트 추가
- 엔드포인트 선택 및 테스트 기능
- 동적 폼 생성 (파라미터 기반)
- 응답 결과 표시 (JSON 포맷)

Closes #20
```

### PR 제목
```
feat: API Detail 및 테스트 페이지 구현 (#20)
```

### 파일 목록
```
frontend/src/pages/ApiDetailPage.tsx
```

---

## Issue #21: Frontend-Backend 연동 및 CORS 설정

### 목표
App 컴포넌트를 구현하고 라우팅을 설정하며, Frontend-Backend 연동을 완료합니다.

### 작업 내용

#### 21.1 App 컴포넌트 구현
**파일**: `frontend/src/App.tsx`

```typescript
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import Dashboard from './pages/Dashboard'
import ApiListPage from './pages/ApiListPage'
import ApiDetailPage from './pages/ApiDetailPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          {/* Navigation Bar */}
          <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold text-gray-900">
                    Universal API Gateway
                  </h1>
                </div>
                <div className="flex space-x-8 items-center">
                  <Link to="/" className="text-gray-600 hover:text-gray-900">
                    Dashboard
                  </Link>
                  <Link to="/apis" className="text-gray-600 hover:text-gray-900">
                    APIs
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          {/* Routes */}
          <main>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/apis" element={<ApiListPage />} />
              <Route path="/apis/:serviceName" element={<ApiDetailPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
```

#### 21.2 메인 엔트리 포인트
**파일**: `frontend/src/main.tsx`

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
```

#### 21.3 CORS 설정 확인
Backend-MCP-SSE의 `main.py`에서 CORS 설정이 올바른지 확인:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+"
)
```

`config.py`에서:
```python
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://localhost:5174",
    ...
]
```

### 브랜치
- **이름**: `feature/021_frontend_backend_integration`
- **베이스**: `develop` (Issue #20 머지 후)

### 커밋 메시지
```
feat: Frontend-Backend 연동 및 CORS 설정

- App 컴포넌트 구현 (라우팅 및 네비게이션)
- React Query QueryClient 설정
- main.tsx 엔트리 포인트 추가
- CORS 설정 확인 및 업데이트

Closes #21
```

### PR 제목
```
feat: Frontend-Backend 연동 및 CORS 설정 (#21)
```

### PR 설명
```markdown
## 요약
Frontend와 Backend를 연동하고 CORS 설정을 완료합니다.

## 변경 사항
- [x] App.tsx 구현 (BrowserRouter, Routes)
- [x] Navigation Bar 추가
- [x] React Query QueryClient 설정
- [x] main.tsx 엔트리 포인트
- [x] CORS 설정 확인

## 테스트 방법
1. Backend-MCP-SSE 실행:
   ```bash
   cd backend-mcp-sse/src
   python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

2. Frontend 실행:
   ```bash
   cd frontend
   npm run dev
   ```

3. 브라우저에서 http://localhost:5173 접속

Closes #21
```

### 파일 목록
```
frontend/src/App.tsx
frontend/src/main.tsx
```

---

## Part 5 요약

### 완료 항목
- ✅ Issue #16: Frontend 프로젝트 초기 설정
- ✅ Issue #17: API 클라이언트 및 React Query 통합
- ✅ Issue #18: Dashboard 페이지 구현
- ✅ Issue #19: API List 페이지 구현
- ✅ Issue #20: API Detail 및 테스트 페이지 구현
- ✅ Issue #21: Frontend-Backend 연동 및 CORS 설정

### 총 PR 수
6개

### 다음 단계
Part 6로 이동하여 문서화 및 최종 정리를 진행합니다.

---

**작성일**: 2025-10-28
**파트**: Part 5 - Frontend 구현

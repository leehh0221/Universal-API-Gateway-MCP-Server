# Backend 구현 단계별 계획서

작성일: 2025-10-27
목표: FastAPI + MCP 서버 구현

---

## 구현 순서 개요

```
Step 1: 프로젝트 초기 설정 (사용자 작업 필요)
  └─> Step 2: 핵심 모듈 구현 (config, models, utils)
      └─> Step 3: API 정의 JSON 파일 생성
          └─> Step 4: API Router 및 HTTP Client 구현
              └─> Step 5: FastAPI 엔드포인트 구현
                  └─> Step 6: MCP 서버 구현
                      └─> Step 7: 테스트 및 검증
```

---

## Step 1: 프로젝트 초기 설정 (사용자 작업 필요 ⚠️)

### 작업 내용

프로젝트 디렉토리 및 Python 환경을 설정합니다.

### 사용자가 해야 할 작업

1. **디렉토리 생성**
   ```bash
   cd C:\workspace\sesac\000.project\Universal-API-Gateway-MCP-Server
   mkdir backend
   cd backend
   ```

2. **Poetry 초기화 및 패키지 설치**
   ```bash
   # Poetry가 없다면 설치
   # pip install poetry

   # Poetry 초기화
   poetry init --no-interaction --name universal-api-gateway --python "^3.11"

   # 프로덕션 의존성 설치
   poetry add fastapi uvicorn pydantic pydantic-settings aiohttp mcp

   # 개발 의존성 설치
   poetry add --group dev pytest pytest-asyncio pytest-cov black isort ruff
   ```

3. **디렉토리 구조 생성**
   ```bash
   # Windows PowerShell
   mkdir src, src\api, src\api\endpoints, src\core, src\models, src\services, src\utils, src\mcp_server, data, data\apis, tests

   # 또는 Git Bash
   mkdir -p src/{api/endpoints,core,models,services,utils,mcp_server} data/apis tests
   ```

4. **__init__.py 파일 생성**
   ```bash
   # Windows PowerShell
   New-Item -ItemType File -Path src\__init__.py
   New-Item -ItemType File -Path src\api\__init__.py
   New-Item -ItemType File -Path src\api\endpoints\__init__.py
   New-Item -ItemType File -Path src\core\__init__.py
   New-Item -ItemType File -Path src\models\__init__.py
   New-Item -ItemType File -Path src\services\__init__.py
   New-Item -ItemType File -Path src\utils\__init__.py
   New-Item -ItemType File -Path src\mcp_server\__init__.py

   # 또는 Git Bash
   touch src/__init__.py
   touch src/api/__init__.py
   touch src/api/endpoints/__init__.py
   touch src/core/__init__.py
   touch src/models/__init__.py
   touch src/services/__init__.py
   touch src/utils/__init__.py
   touch src/mcp_server/__init__.py
   ```

### 예상 디렉토리 구조

```
backend/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   └── mcp_server/
│       └── __init__.py
├── data/
│   └── apis/
├── tests/
├── pyproject.toml
└── poetry.lock
```

### 완료 확인

- [ ] `backend` 디렉토리 생성됨
- [ ] `poetry install` 완료
- [ ] 디렉토리 구조 생성됨
- [ ] `__init__.py` 파일들 생성됨

---

## Step 2: 핵심 모듈 구현 (자동 구현)

### 구현할 파일

1. `src/utils/logger.py` - 로깅 설정
2. `src/core/config.py` - 애플리케이션 설정
3. `src/models/api_definition.py` - API 정의 모델
4. `src/models/requests.py` - 요청 모델
5. `src/models/responses.py` - 응답 모델

### 기능

- Pydantic 기반 데이터 모델
- 환경 변수 기반 설정
- 구조화된 로깅

---

## Step 3: API 정의 JSON 파일 생성 (자동 구현)

### 구현할 파일

1. `data/apis/steam.json` - Steam API 정의
2. `data/apis/weather.json` - Weather API 정의
3. `data/apis/news.json` - News API 정의

### 내용

- 3개 Public API의 엔드포인트 정의
- 파라미터, 응답 매핑 포함
- 하드코딩된 테스트 데이터

---

## Step 4: API Router 및 HTTP Client 구현 (자동 구현)

### 구현할 파일

1. `src/utils/json_path.py` - JSONPath 파서
2. `src/core/security.py` - 보안 유틸리티
3. `src/core/http_client.py` - HTTP 클라이언트
4. `src/core/api_router.py` - API 라우팅 로직

### 기능

- JSON 파일에서 API 정의 로드
- 외부 API 호출 및 응답 처리
- URL 검증 및 보안 기능
- Rate Limiting

---

## Step 5: FastAPI 엔드포인트 구현 (자동 구현)

### 구현할 파일

1. `src/services/api_service.py` - API 관리 서비스
2. `src/services/proxy_service.py` - 프록시 서비스
3. `src/api/dependencies.py` - 의존성 주입
4. `src/api/endpoints/health.py` - 헬스체크
5. `src/api/endpoints/apis.py` - API 관리 엔드포인트
6. `src/api/endpoints/proxy.py` - 프록시 엔드포인트
7. `src/api/router.py` - 메인 라우터
8. `src/main.py` - FastAPI 앱

### 기능

- REST API 엔드포인트
- API 목록 조회, 상세 조회
- API 테스트 호출
- CORS 설정

---

## Step 6: MCP 서버 구현 (자동 구현)

### 구현할 파일

1. `src/mcp_server/tools.py` - Tool 변환 로직
2. `src/mcp_server/handlers.py` - MCP 요청 핸들러
3. `src/mcp_server/server.py` - MCP 서버 메인
4. `src/mcp_server/__main__.py` - CLI 진입점

### 기능

- MCP Protocol 구현 (stdio)
- tools/list 핸들러
- tools/call 핸들러
- Claude Desktop 연동

---

## Step 7: 테스트 및 검증 (자동 구현)

### 구현할 파일

1. `tests/conftest.py` - pytest 설정
2. `tests/test_config.py` - 설정 테스트
3. `tests/test_api_router.py` - API Router 테스트
4. `tests/test_endpoints.py` - FastAPI 엔드포인트 테스트
5. `tests/test_mcp_server.py` - MCP 서버 테스트

### 기능

- 단위 테스트
- 통합 테스트
- Mock 데이터 사용

---

## Step 8: 실행 및 검증 (사용자 작업)

### FastAPI 서버 실행

```bash
cd backend
poetry run uvicorn src.main:app --reload --port 8000
```

브라우저에서 확인:
- http://localhost:8000 - 기본 페이지
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/api/v1/apis - API 목록

### MCP 서버 실행

```bash
cd backend
poetry run python -m src.mcp_server
```

### 테스트 실행

```bash
cd backend
poetry run pytest -v
```

---

## 구현 진행 방식

### 자동 구현 (Claude Code)

Step 2 ~ Step 7까지는 제가 자동으로 구현합니다.

**진행 순서:**
1. Step 2: 핵심 모듈 구현
2. Step 3: API 정의 JSON 생성
3. Step 4: API Router 구현
4. Step 5: FastAPI 엔드포인트 구현
5. Step 6: MCP 서버 구현
6. Step 7: 테스트 코드 작성

### 사용자 작업

**지금 당장 필요한 작업:**
- Step 1의 프로젝트 초기 설정 (디렉토리 생성, Poetry 설치)

**구현 완료 후 필요한 작업:**
- Step 8의 실행 및 검증

---

## 예상 소요 시간

- Step 1 (사용자): 5-10분
- Step 2-7 (자동): 15-20분
- Step 8 (사용자): 5분

**총 예상 시간: 30-40분**

---

## 다음 단계

1. **사용자**: Step 1의 명령어들을 실행해주세요
2. **완료 알림**: "Step 1 완료했습니다" 라고 알려주세요
3. **Claude Code**: Step 2부터 자동으로 구현 시작

---

## 문제 발생 시

- Poetry 설치 문제: `pip install poetry` 또는 공식 설치 스크립트 사용
- Python 버전 문제: Python 3.11 이상 필요
- 권한 문제: 관리자 권한으로 터미널 실행

준비되면 알려주세요!

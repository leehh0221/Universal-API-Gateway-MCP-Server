# Universal API Gateway MCP Server

단일 MCP 서버로 여러 외부 API를 사용할 수 있는 Universal API Gateway입니다.

## 프로젝트 구조

```
Universal-API-Gateway-MCP-Server/
├── backend/          # FastAPI 백엔드 + MCP 서버
│   ├── src/          # 소스 코드
│   ├── data/apis/    # API 정의 JSON 파일
│   └── venv/         # Python 가상환경
├── frontend/         # React 프론트엔드 대시보드
│   └── src/          # React 소스 코드
└── docs/             # 문서
```

## 지원 API

### 1. Steam Web API
- **설명**: Steam 게임 정보 및 플레이어 통계 조회
- **API 키**: 필요 없음 (Public API)
- **엔드포인트**:
  - Get Player Summaries: Steam 사용자 프로필 정보 조회

### 2. Open-Meteo Weather API
- **설명**: 전 세계 날씨 정보 조회
- **API 키**: 필요 없음 (무료 Public API)
- **엔드포인트**:
  - Get Current Weather: 현재 날씨 정보 조회
  - Get Weather Forecast: 날씨 예보 조회

### 3. NewsAPI.org
- **설명**: 전 세계 뉴스 기사 검색 및 조회
- **API 키**: **필수** (무료 등록)
- **API 키 발급**: https://newsapi.org/register
- **엔드포인트**:
  - Get Top Headlines: 최신 헤드라인 뉴스
  - Search Everything: 키워드로 뉴스 검색

#### NewsAPI 사용 방법:
1. https://newsapi.org/register 에서 무료 계정 등록
2. 이메일로 받은 API 키 복사
3. `backend/.env` 파일 생성 및 API 키 설정 (아래 참고)

## 빠른 시작

### 환경 변수 설정

NewsAPI를 사용하려면 API 키가 필요합니다:

```bash
# 1. backend 디렉토리로 이동
cd backend

# 2. .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env

# 3. .env 파일을 열어 NewsAPI 키 입력
# NEWSAPI_KEY=your_actual_api_key_here
```

### 백엔드 실행

```bash
# 1. 백엔드 디렉토리로 이동
cd backend

# 2. Python 가상환경 활성화 (Windows)
venv\Scripts\activate

# 3. 의존성 설치 (처음 한 번만)
pip install -r requirements.txt

# 4. 서버 실행
cd src
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

백엔드 서버: http://localhost:8000

### 프론트엔드 실행

```bash
# 1. 프론트엔드 디렉토리로 이동
cd frontend

# 2. 의존성 설치 (처음 한 번만)
npm install

# 3. 개발 서버 실행
npm run dev
```

프론트엔드 대시보드: http://localhost:5173

## API 테스트 방법

1. 브라우저에서 http://localhost:5173 접속
2. "APIs" 메뉴 클릭
3. 테스트하고 싶은 API 선택
4. 엔드포인트 선택
5. 필요한 파라미터 입력
6. "Test API" 버튼 클릭
7. 응답 결과 확인

**주의**: NewsAPI의 경우 `.env` 파일에 API 키를 미리 설정해야 합니다.

## MCP 서버로 사용

Claude Desktop에서 MCP 서버로 사용하려면:

```json
{
  "mcpServers": {
    "universal-api-gateway": {
      "command": "C:\\path\\to\\backend\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\backend\\src\\mcp_server\\server.py"
      ]
    }
  }
}
```

## 기술 스택

### 백엔드
- **FastAPI 0.115.0**: REST API 프레임워크
- **Python 3.12**: 프로그래밍 언어
- **Pydantic 2.9.0**: 데이터 검증
- **aiohttp 3.10.0**: 비동기 HTTP 클라이언트
- **MCP SDK 1.1.2**: Model Context Protocol 서버

### 프론트엔드
- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안전성
- **Vite 7.1.12**: 빌드 도구
- **TanStack React Query 5.64.2**: 서버 상태 관리
- **React Router 7.1.1**: 라우팅
- **Tailwind CSS 4.0**: 스타일링
- **Axios 1.7.9**: HTTP 클라이언트

## 주요 기능

- ✅ 3개 Public API 통합 (Steam, Weather, News)
- ✅ RESTful API 엔드포인트
- ✅ MCP (Model Context Protocol) 서버
- ✅ React 대시보드 UI
- ✅ 실시간 API 테스트 기능
- ✅ CORS 설정 (모든 localhost 포트 허용)
- ✅ 파라미터 검증 및 타입 체크
- ✅ JSONPath 기반 응답 매핑
- ✅ 보안 (URL 화이트리스트, 내부 IP 차단)

## 라이선스

MIT License

## 작성자

Generated with Claude Code

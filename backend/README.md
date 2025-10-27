# Universal API Gateway - Backend

FastAPI 기반 백엔드 서버 및 MCP 서버

## 구현 완료 사항 ✅

- ✅ FastAPI REST API 서버
- ✅ MCP (Model Context Protocol) 서버
- ✅ 3개 Public API 지원 (Steam, Weather, News)
- ✅ 5개 엔드포인트 구현
- ✅ API 라우팅 및 프록시
- ✅ 보안 기능 (URL 화이트리스트, 내부 IP 차단)
- ✅ 입력 검증 및 에러 핸들링

## 설치 및 실행

### 1. 가상환경 및 의존성 설치

```bash
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. FastAPI 서버 실행

```bash
cd src
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

서버 접속:
- 메인: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/api/v1/health
- API 목록: http://localhost:8000/api/v1/apis

### 3. MCP 서버 실행

```bash
cd src
python -m mcp_server
```

또는:
```bash
python -m src.mcp_server
```

## API 엔드포인트

### REST API

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 루트 페이지 |
| `/api/v1/health` | GET | 헬스체크 |
| `/api/v1/apis` | GET | 등록된 API 목록 |
| `/api/v1/apis/{service_name}` | GET | API 상세 정보 |
| `/api/v1/apis/{service_name}/endpoints` | GET | 엔드포인트 목록 |
| `/api/v1/proxy/test` | POST | API 테스트 호출 |

### 등록된 외부 API

1. **Steam Web API** (`steam`)
   - `steam_get_popular_games`: 인기 게임 목록 조회

2. **Open-Meteo Weather API** (`weather`)
   - `weather_get_current`: 현재 날씨 조회
   - `weather_get_forecast`: 일기 예보 조회

3. **NewsAPI.org** (`news`)
   - `news_get_top_headlines`: 최신 헤드라인 뉴스
   - `news_search_everything`: 뉴스 검색

## 사용 예시

### API 목록 조회

```bash
curl http://localhost:8000/api/v1/apis
```

### 날씨 API 테스트 (서울)

```bash
curl -X POST http://localhost:8000/api/v1/proxy/test \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "weather",
    "endpoint_id": "get_current_weather",
    "arguments": {
      "latitude": 37.5665,
      "longitude": 126.9780
    }
  }'
```

## 프로젝트 구조

```
backend/
├── src/
│   ├── main.py                    # FastAPI 앱
│   ├── api/
│   │   ├── router.py             # 메인 라우터
│   │   ├── dependencies.py       # 의존성 주입
│   │   └── endpoints/            # API 엔드포인트
│   ├── core/
│   │   ├── config.py             # 설정
│   │   ├── api_router.py         # API 라우팅 로직
│   │   └── security.py           # 보안 유틸리티
│   ├── models/
│   │   ├── api_definition.py    # 데이터 모델
│   │   ├── requests.py
│   │   └── responses.py
│   ├── services/
│   │   ├── api_service.py       # API 관리 서비스
│   │   └── proxy_service.py     # 프록시 서비스
│   ├── utils/
│   │   ├── logger.py            # 로깅
│   │   ├── validators.py        # 입력 검증
│   │   └── json_path.py         # JSONPath 파서
│   └── mcp_server/
│       ├── server.py            # MCP 서버
│       ├── handlers.py          # MCP 핸들러
│       └── tools.py             # Tool 변환
├── data/
│   └── apis/                    # API 정의 JSON 파일
│       ├── steam.json
│       ├── weather.json
│       └── news.json
├── requirements.txt             # Python 의존성
└── README.md                   # 이 파일
```

## 기술 스택

- **FastAPI** 0.115.0 - 웹 프레임워크
- **Uvicorn** 0.32.0 - ASGI 서버
- **Pydantic** 2.9.0 - 데이터 검증
- **aiohttp** 3.10.0 - 비동기 HTTP 클라이언트
- **MCP** 1.1.2 - Model Context Protocol SDK

## 환경 변수

`.env` 파일을 생성하여 설정을 오버라이드할 수 있습니다:

```bash
DEBUG=True
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

## 다음 단계

- [ ] 프론트엔드 React 대시보드 구현
- [ ] MCP 서버 Claude Desktop 연동 테스트
- [ ] 추가 API 등록 (GitHub, OpenWeatherMap 등)
- [ ] Rate Limiting 구현
- [ ] 단위 테스트 작성

## 문의

구현 관련 문의사항은 이슈를 등록해주세요.

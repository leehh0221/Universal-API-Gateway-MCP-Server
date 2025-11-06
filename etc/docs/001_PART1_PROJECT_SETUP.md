# Part 1: 프로젝트 초기 설정 및 인프라

## 개요

프로젝트의 기본 구조, 환경 설정, 그리고 핵심 인프라 코드를 구축하는 단계입니다.

---

## Issue #1: 프로젝트 구조 및 .gitignore 설정

### 목표
프로젝트 디렉토리 구조를 생성하고 버전 관리에서 제외할 파일들을 정의합니다.

### 작업 내용

#### 1.1 디렉토리 구조 생성
```
Universal-API-Gateway-MCP-Server/
├── backend/
│   ├── src/
│   ├── data/
│   ├── tests/
│   └── .gitignore
├── backend-mcp-sse/
│   ├── src/
│   ├── data/
│   └── .gitignore
├── frontend/
│   ├── src/
│   ├── public/
│   └── .gitignore
├── etc/
│   └── docs/
├── .gitignore
└── README.md
```

#### 1.2 .gitignore 파일 생성

**루트 .gitignore**:
- IDE 설정 파일 (.claude/, .idea/, .vscode/)
- OS 파일 (macOS, Windows, Linux)
- 환경 변수 (.env, .env.local 등)
- 로그 및 임시 파일
- 빌드 아티팩트 (dist/, build/)
- 패키지 매니저 (node_modules/)
- 데이터베이스 및 캐시

**backend/.gitignore**:
- Python 바이트코드 (__pycache__/, *.pyc)
- 가상환경 (venv/, ENV/)
- Python 패키징 (*.egg-info/, dist/)
- 테스트 및 커버리지 (.pytest_cache/, .coverage)
- 환경 변수 및 시크릿

**backend-mcp-sse/.gitignore**:
- backend와 동일 + MCP 특화 항목
- SSE 로그 (sse-logs/)
- MCP 캐시 (.mcp-cache/)

**frontend/.gitignore**:
- Node.js (node_modules/)
- Vite 빌드 (dist/, .vite/)
- 환경 변수 (.env*)
- TypeScript 빌드 정보
- 테스트 커버리지

#### 1.3 README.md 초안 작성
```markdown
# Universal API Gateway

Model Context Protocol (MCP) 기반 통합 API 게이트웨이

## 프로젝트 구조

- backend: MCP stdio 서버
- backend-mcp-sse: MCP HTTP/SSE 서버
- frontend: React 대시보드

## 시작하기

(각 폴더의 README 참조)
```

### 브랜치
- **이름**: `feature/001_project_structure`
- **베이스**: `develop`

### 커밋 메시지
```
feat: 프로젝트 구조 및 .gitignore 설정

- 프로젝트 디렉토리 구조 생성
- 루트, backend, backend-mcp-sse, frontend .gitignore 추가
- README.md 초안 작성

Closes #1
```

### PR 제목
```
feat: 프로젝트 구조 및 .gitignore 설정 (#1)
```

### PR 설명
```markdown
## 요약
프로젝트 기본 구조와 .gitignore 설정을 추가합니다.

## 변경 사항
- [x] 프로젝트 디렉토리 구조 생성 (backend, backend-mcp-sse, frontend, etc/docs)
- [x] 루트 .gitignore 추가 (IDE, OS, 환경변수, 빌드 아티팩트)
- [x] backend/.gitignore 추가 (Python 특화)
- [x] backend-mcp-sse/.gitignore 추가 (Python + MCP 특화)
- [x] frontend/.gitignore 추가 (Node.js, Vite 특화)
- [x] README.md 초안 작성

## 체크리스트
- [x] .gitignore 파일이 올바르게 설정되었는지 확인
- [x] 디렉토리 구조가 계획대로 생성되었는지 확인

Closes #1
```

### 파일 목록
```
.gitignore
backend/.gitignore
backend-mcp-sse/.gitignore
frontend/.gitignore
README.md
```

---

## Issue #2: Backend 의존성 및 환경 설정

### 목표
Backend (stdio) 프로젝트의 Python 의존성 및 환경 변수 설정을 구성합니다.

### 작업 내용

#### 2.1 requirements.txt 작성
**파일**: `backend/requirements.txt`

```txt
# MCP Protocol
mcp==1.1.2

# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0

# Data Validation
pydantic==2.9.0
pydantic-settings==2.6.0

# HTTP Client
aiohttp==3.10.0
```

#### 2.2 requirements-dev.txt 작성
**파일**: `backend/requirements-dev.txt`

```txt
pytest==8.2.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.0
black==24.4.2
isort==5.13.2
ruff==0.4.5
```

#### 2.3 .env.example 작성
**파일**: `backend/.env`

```bash
# NewsAPI.org API Key
NEWSAPI_KEY=your_api_key_here
```

**참고**: 실제 `.env` 파일은 .gitignore에 포함되므로 버전 관리에서 제외됩니다.

#### 2.4 data/apis 디렉토리 생성
```
backend/data/apis/
```

빈 디렉토리 생성 (API 정의 JSON 파일은 이후 이슈에서 추가)

### 브랜치
- **이름**: `feature/002_backend_dependencies`
- **베이스**: `develop` (Issue #1 머지 후)

### 커밋 메시지
```
feat: Backend 의존성 및 환경 설정

- requirements.txt 추가 (FastAPI, MCP, Pydantic 등)
- requirements-dev.txt 추가 (테스트 및 린팅 도구)
- .env.example 추가 (API 키 템플릿)
- data/apis 디렉토리 생성

Closes #2
```

### PR 제목
```
feat: Backend 의존성 및 환경 설정 (#2)
```

### PR 설명
```markdown
## 요약
Backend 프로젝트의 Python 의존성 및 환경 변수 설정을 추가합니다.

## 변경 사항
- [x] requirements.txt 추가 (프로덕션 의존성)
- [x] requirements-dev.txt 추가 (개발 의존성)
- [x] .env.example 추가 (환경 변수 템플릿)
- [x] data/apis 디렉토리 생성

## 의존성 목록
### 프로덕션
- mcp 1.1.2 (MCP 프로토콜)
- fastapi 0.115.0 (웹 프레임워크)
- uvicorn 0.32.0 (ASGI 서버)
- pydantic 2.9.0 (데이터 검증)
- aiohttp 3.10.0 (비동기 HTTP 클라이언트)

### 개발
- pytest, pytest-asyncio, pytest-cov (테스팅)
- black, isort, ruff (코드 포맷팅 및 린팅)
- httpx (HTTP 테스트 클라이언트)

Closes #2
```

### 파일 목록
```
backend/requirements.txt
backend/requirements-dev.txt
backend/.env.example
backend/data/apis/.gitkeep (옵션)
```

---

## Issue #3: Backend 코어 설정 (Config, Security, Logger)

### 목표
Backend의 핵심 유틸리티 및 설정 모듈을 구현합니다.

### 작업 내용

#### 3.1 Config 모듈 구현
**파일**: `backend/src/core/config.py`

**주요 내용**:
- Pydantic BaseSettings 사용
- 환경 변수 로딩 (.env 파일)
- 애플리케이션 설정 (APP_NAME, DEBUG, VERSION)
- 서버 설정 (HOST, PORT)
- CORS 설정
- 보안 설정 (ALLOWED_DOMAINS, BLOCKED_IP_RANGES)
- Rate Limiting 설정
- HTTP 클라이언트 설정
- 로깅 레벨
- API 키 (NEWSAPI_KEY)

**주요 코드**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Universal API Gateway"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data" / "apis"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    CORS_ORIGINS: List[str] = [...]
    ALLOWED_DOMAINS: List[str] = [...]
    BLOCKED_IP_RANGES: List[str] = [...]

    NEWSAPI_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        case_sensitive=True
    )

settings = Settings()
```

#### 3.2 Security 모듈 구현
**파일**: `backend/src/core/security.py`

**주요 기능**:
- `validate_url(url: str) -> bool`: 도메인 화이트리스트 검증
- `validate_not_internal_ip(url: str) -> bool`: 내부 IP 차단 (SSRF 방지)
- `check_security(url: str) -> None`: 통합 보안 검사
- `SecurityError` 예외 클래스

**주요 코드**:
```python
import ipaddress
from urllib.parse import urlparse
from typing import List

class SecurityError(Exception):
    pass

def validate_url(url: str) -> bool:
    """도메인 화이트리스트 검증"""
    parsed = urlparse(url)
    domain = parsed.netloc.split(':')[0]

    from .config import settings
    return domain in settings.ALLOWED_DOMAINS

def validate_not_internal_ip(url: str) -> bool:
    """SSRF 방지 - 내부 IP 차단"""
    # IP 범위 체크 로직
    ...

def check_security(url: str) -> None:
    """통합 보안 검사"""
    if not validate_url(url):
        raise SecurityError(f"URL domain not allowed: {url}")
    if not validate_not_internal_ip(url):
        raise SecurityError(f"Internal IP not allowed: {url}")
```

#### 3.3 Logger 모듈 구현
**파일**: `backend/src/utils/logger.py`

**주요 기능**:
- `setup_logger()`: 로거 설정 함수
- stderr로 출력 (stdio 모드와 호환)
- 포맷팅 설정

**주요 코드**:
```python
import logging
import sys

def setup_logger(
    name: str,
    level: int = logging.INFO
) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
```

#### 3.4 __init__.py 파일 생성
**파일 목록**:
- `backend/src/__init__.py`
- `backend/src/core/__init__.py`
- `backend/src/utils/__init__.py`

### 브랜치
- **이름**: `feature/003_backend_core_config`
- **베이스**: `develop` (Issue #2 머지 후)

### 커밋 메시지
```
feat: Backend 코어 설정 모듈 구현

- Pydantic Settings 기반 Config 모듈 추가
- 보안 검증 모듈 추가 (URL 화이트리스트, SSRF 방지)
- 로거 유틸리티 추가 (stderr 출력)
- 디렉토리 __init__.py 파일 생성

Closes #3
```

### PR 제목
```
feat: Backend 코어 설정 모듈 구현 (#3)
```

### PR 설명
```markdown
## 요약
Backend의 핵심 설정 및 유틸리티 모듈을 구현합니다.

## 변경 사항
- [x] Config 모듈 추가 (Pydantic Settings 기반)
  - 환경 변수 로딩
  - 애플리케이션, 서버, CORS, 보안 설정
  - API 키 관리
- [x] Security 모듈 추가
  - URL 도메인 화이트리스트 검증
  - 내부 IP 차단 (SSRF 방지)
  - SecurityError 예외 클래스
- [x] Logger 모듈 추가
  - stderr 기반 로깅 (stdio 모드 호환)
  - 포맷팅 설정
- [x] __init__.py 파일 생성

## 구현 세부사항
### Config 주요 설정
- APP_NAME, VERSION, DEBUG
- HOST, PORT (서버 설정)
- CORS_ORIGINS (허용 출처 목록)
- ALLOWED_DOMAINS (허용 도메인)
- BLOCKED_IP_RANGES (차단 IP 범위)
- NEWSAPI_KEY (API 키)

### Security 주요 기능
- `validate_url()`: 도메인 화이트리스트 검증
- `validate_not_internal_ip()`: 내부 IP 차단
- `check_security()`: 통합 보안 검사

### Logger 주요 기능
- `setup_logger()`: 로거 설정 함수
- stderr 출력 (stdio 모드 호환)

Closes #3
```

### 파일 목록
```
backend/src/__init__.py
backend/src/core/__init__.py
backend/src/core/config.py
backend/src/core/security.py
backend/src/utils/__init__.py
backend/src/utils/logger.py
```

---

## Part 1 요약

### 완료 항목
- ✅ Issue #1: 프로젝트 구조 및 .gitignore 설정
- ✅ Issue #2: Backend 의존성 및 환경 설정
- ✅ Issue #3: Backend 코어 설정 (Config, Security, Logger)

### 총 PR 수
3개

### 다음 단계
Part 2로 이동하여 Backend의 핵심 MCP 기능을 구현합니다.

---

**작성일**: 2025-10-28
**파트**: Part 1 - 프로젝트 초기 설정 및 인프라

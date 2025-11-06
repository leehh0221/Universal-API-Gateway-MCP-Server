# Universal API Gateway - Master Reorganization Plan

## Overview

이 문서는 `feature/001_init` 브랜치에 구현된 모든 내용을 분석하고, 각 기능별로 이슈를 생성하여 개별 브랜치로 분리하여 PR하는 전체 계획을 담고 있습니다.

## 현재 상황 분석

### 브랜치 상태
- **현재 브랜치**: `feature/001_init`
- **베이스 브랜치**: `develop`
- **커밋 수**: 23개의 커밋이 develop 브랜치보다 앞서 있음
- **작업 범위**: 전체 프로젝트 초기 구현 (Backend stdio, Backend HTTP/SSE, Frontend)

### 구현 완료된 항목

#### 1. Backend (stdio 방식) - MCP 로컬 서버
- **위치**: `/backend`
- **전송 방식**: stdio (표준 입출력)
- **용도**: Claude Desktop과 로컬 연동
- **구현 상태**: ✅ 완료
- **주요 기능**:
  - FastAPI REST API 서버
  - MCP stdio 서버 (로컬 연결용)
  - MCP SSE 서버 (HTTP 연결용)
  - 3개 외부 API 통합 (Steam, Weather, News)
  - 보안 기능 (URL 화이트리스트, SSRF 방지)
  - 파라미터 검증 및 에러 핸들링
  - JSONPath 기반 응답 매핑

#### 2. Backend-MCP-SSE (HTTP/SSE 방식) - MCP 원격 서버
- **위치**: `/backend-mcp-sse`
- **전송 방식**: HTTP/SSE (Server-Sent Events)
- **용도**: 원격 MCP 클라이언트 연동 (웹 기반)
- **구현 상태**: ✅ 대부분 완료, 일부 미완성
- **주요 기능**:
  - FastAPI + MCP SSE 통합 서버
  - REST API 및 MCP SSE 동시 제공
  - Backend와 동일한 API 라우팅 로직 공유
  - 개선된 APIRouter 재사용 아키텍처
- **미완성 항목**:
  - Rate Limiting (설정되어 있으나 미적용)
  - API Key Authentication (구조만 존재)
  - 에러 응답 표준화
  - 테스트 코드 부재

#### 3. Frontend (React + TypeScript)
- **위치**: `/frontend`
- **기술 스택**: React 19, TypeScript, Vite, Tailwind CSS, React Query
- **구현 상태**: ✅ 완료
- **주요 기능**:
  - Dashboard (시스템 상태 및 API 목록)
  - API List Page (전체 API 목록)
  - API Detail Page (API 상세 정보 및 엔드포인트 테스트)
  - React Query 기반 상태 관리
  - Axios 기반 API 클라이언트
  - 반응형 UI (Tailwind CSS)
- **미완성 항목**:
  - 컴포넌트 재사용성 개선
  - Form Validation 라이브러리
  - Authentication UI
  - Error Boundary
  - 테스트 코드

#### 4. 문서 및 설정
- README 파일들
- 환경 설정 파일 (.env.example)
- Git 설정 (.gitignore는 이번에 추가됨)
- 요구사항 파일 (requirements.txt)

## 재구성 전략

### 목표
1. 각 기능을 독립적인 이슈로 분리
2. 이슈 번호 기반 브랜치 생성
3. 작은 단위의 PR로 분할하여 리뷰 용이성 확보
4. 각 PR은 하나의 명확한 책임을 가짐

### 이슈 분류 기준
- **Part 1**: 프로젝트 초기 설정 및 인프라
- **Part 2**: Backend (stdio) 핵심 구현
- **Part 3**: Backend (stdio) API 통합
- **Part 4**: Backend-MCP-SSE 구현
- **Part 5**: Frontend 구현
- **Part 6**: 문서화 및 마무리

## 이슈 목록 (상세 계획은 별도 문서 참조)

### Part 1: 프로젝트 초기 설정 및 인프라
1. **Issue #1**: 프로젝트 구조 및 .gitignore 설정
2. **Issue #2**: Backend 의존성 및 환경 설정
3. **Issue #3**: Backend 코어 설정 (Config, Security, Logger)

### Part 2: Backend (stdio) - 핵심 MCP 기능
4. **Issue #4**: Pydantic 모델 정의 (API Definition, Request, Response)
5. **Issue #5**: API Router 핵심 로직 구현
6. **Issue #6**: MCP stdio 서버 구현
7. **Issue #7**: MCP Tool 생성 및 핸들러 구현

### Part 3: Backend (stdio) - API 통합 및 REST API
8. **Issue #8**: Steam API 통합
9. **Issue #9**: Weather API 통합
10. **Issue #10**: NewsAPI 통합 및 서버 측 API 키 관리
11. **Issue #11**: FastAPI REST API 엔드포인트 구현
12. **Issue #12**: MCP SSE 전송 계층 구현

### Part 4: Backend-MCP-SSE - HTTP/SSE 서버
13. **Issue #13**: Backend-MCP-SSE 프로젝트 설정
14. **Issue #14**: Backend-MCP-SSE MCP 서버 구현
15. **Issue #15**: Backend-MCP-SSE REST API 및 통합

### Part 5: Frontend - React 애플리케이션
16. **Issue #16**: Frontend 프로젝트 초기 설정 (Vite, TypeScript, Tailwind)
17. **Issue #17**: API 클라이언트 및 React Query 통합
18. **Issue #18**: Dashboard 페이지 구현
19. **Issue #19**: API List 페이지 구현
20. **Issue #20**: API Detail 및 테스트 페이지 구현
21. **Issue #21**: Frontend-Backend 연동 및 CORS 설정

### Part 6: 문서화 및 개선
22. **Issue #22**: README 및 사용 가이드 작성
23. **Issue #23**: MCP stdio 모드 에러 수정 및 영문 설명 추가
24. **Issue #24**: 미완성 기능 정리 및 TODO 문서화

## 작업 프로세스

각 이슈에 대해 다음 프로세스를 따릅니다:

```
1. GitHub Issue 생성
   ↓
2. 이슈 번호로 브랜치 생성 (feature/{issue_number}_{description})
   ↓
3. 해당 브랜치로 checkout
   ↓
4. feature/001_init에서 해당 기능 관련 코드만 cherry-pick 또는 복사
   ↓
5. 커밋 메시지 작성 (feat/fix/docs 등 Conventional Commits 형식)
   ↓
6. 푸시
   ↓
7. PR 생성 (base: develop)
   ↓
8. 리뷰 및 머지
```

## 세부 계획서

각 파트별 상세한 작업 내용은 다음 문서들을 참조하세요:

- **[001_PART1_PROJECT_SETUP.md](001_PART1_PROJECT_SETUP.md)**: 프로젝트 초기 설정
- **[002_PART2_BACKEND_CORE.md](002_PART2_BACKEND_CORE.md)**: Backend stdio 핵심 기능
- **[003_PART3_BACKEND_API.md](003_PART3_BACKEND_API.md)**: Backend API 통합
- **[004_PART4_BACKEND_SSE.md](004_PART4_BACKEND_SSE.md)**: Backend-MCP-SSE 구현
- **[005_PART5_FRONTEND.md](005_PART5_FRONTEND.md)**: Frontend 구현
- **[006_PART6_DOCS.md](006_PART6_DOCS.md)**: 문서화 및 마무리

## 주의사항

1. **의존성 관리**: 각 브랜치는 이전 이슈가 머지된 후에 생성해야 함
2. **커밋 메시지**: Conventional Commits 형식 준수
3. **PR 설명**: 각 PR은 관련 이슈 번호 및 변경 사항을 명확히 기술
4. **테스트**: 가능한 경우 각 PR에 테스트 추가
5. **리뷰**: 모든 PR은 리뷰 후 머지

## 타임라인 예상

- Part 1: 3개 이슈 (1일)
- Part 2: 4개 이슈 (2일)
- Part 3: 5개 이슈 (2일)
- Part 4: 3개 이슈 (1일)
- Part 5: 6개 이슈 (3일)
- Part 6: 4개 이슈 (1일)

**총 예상 기간**: 10일 (리뷰 시간 포함)

## 다음 단계

1. 이 마스터 플랜을 검토하고 승인받기
2. 각 파트별 세부 계획서 작성 완료 확인
3. Issue #1부터 순차적으로 생성 시작
4. 첫 번째 브랜치 생성 및 PR 진행

---

**작성일**: 2025-10-28
**작성자**: AI Assistant (Claude Code)
**최종 수정일**: 2025-10-28

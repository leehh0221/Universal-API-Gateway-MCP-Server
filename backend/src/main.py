"""
FastAPI 애플리케이션 진입점
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import set_api_router
from api.router import api_router
from core.api_router import APIRouter
from core.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""

    # 시작 시
    logger.info("Starting Universal API Gateway...")

    # APIRouter 인스턴스 생성 및 초기화
    api_router_instance = APIRouter(data_dir=settings.DATA_DIR)
    await api_router_instance.load_api_definitions()
    await api_router_instance.create_session()

    # 전역 인스턴스 설정
    set_api_router(api_router_instance)

    logger.info(f"Loaded {len(api_router_instance.apis)} APIs")
    logger.info(f"Server ready on {settings.HOST}:{settings.PORT}")

    yield

    # 종료 시
    logger.info("Shutting down...")
    await api_router_instance.close_session()


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="단일 MCP 서버로 여러 외부 API를 사용하는 Universal API Gateway",
    version=settings.VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+"  # 모든 localhost 포트 허용
)

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

"""
Universal API Gateway - HTTP/SSE MCP Server + REST API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.api_router import APIRouter
from api.dependencies import set_api_router
from api.router import api_router
from mcp_module.mcp_server import create_mcp_sse_app
from utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Universal API Gateway (HTTP/SSE)...")

    # Create and initialize API Router instance
    api_router_instance = APIRouter(data_dir=settings.DATA_DIR)
    await api_router_instance.load_api_definitions()
    await api_router_instance.create_session()

    # Set global instance
    set_api_router(api_router_instance)

    # Create MCP SSE app (Starlette app)
    mcp_app = create_mcp_sse_app(api_router_instance)

    # Mount MCP app at /mcp
    app.mount("/mcp", mcp_app)

    logger.info(f"Loaded {len(api_router_instance.apis)} APIs")
    logger.info(f"Server ready on {settings.HOST}:{settings.PORT}")
    logger.info(f"MCP SSE endpoint: http://{settings.HOST}:{settings.PORT}/mcp/sse")
    logger.info(f"REST API docs: http://{settings.HOST}:{settings.PORT}/docs")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await api_router_instance.close_session()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="HTTP/SSE MCP Server + REST API",
    version=settings.VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS middleware (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+"
)

# Register REST API router (for frontend)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "mcp_sse": "/mcp/sse"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

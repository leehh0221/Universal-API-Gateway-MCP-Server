"""
Universal API Gateway MCP Server
"""
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server

from core.api_router import APIRouter
from core.config import settings
from mcp_server.handlers import MCPHandlers
from utils.logger import setup_logger

logger = setup_logger(__name__)


class UniversalMCPServer:
    """Universal API Gateway MCP Server"""

    def __init__(self):
        self.server = Server("universal-api-gateway")
        self.api_router = APIRouter(data_dir=settings.DATA_DIR)
        self.handlers = None

    async def initialize(self):
        """서버 초기화"""
        logger.info("Initializing MCP server...")

        # API 정의 로드
        await self.api_router.load_api_definitions()
        await self.api_router.create_session()

        logger.info(f"Loaded {len(self.api_router.apis)} APIs")

        # 핸들러 생성
        self.handlers = MCPHandlers(self.api_router)

        # MCP 핸들러 등록
        self._register_handlers()

        logger.info("MCP server initialized")

    def _register_handlers(self):
        """MCP 요청 핸들러 등록"""

        @self.server.list_tools()
        async def list_tools():
            """사용 가능한 모든 도구 목록"""
            return await self.handlers.handle_list_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """도구 호출"""
            return await self.handlers.handle_call_tool(name, arguments)

    async def cleanup(self):
        """리소스 정리"""
        logger.info("Cleaning up...")
        await self.api_router.close_session()

    async def run_stdio(self):
        """stdio 방식으로 서버 실행 (로컬 전용, 레거시)"""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.initialize()

                logger.info("MCP server running (stdio mode)...")

                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )

        except Exception as e:
            logger.error(f"MCP server error: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()


def main():
    """메인 함수 (stdio 모드 - 레거시 지원)"""
    server = UniversalMCPServer()

    try:
        asyncio.run(server.run_stdio())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

"""
MCP SSE 전송 계층
"""
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.sse import SseServerTransport

from mcp_server.server import UniversalMCPServer
from utils.logger import setup_logger

logger = setup_logger(__name__)


# SSE 전송 생성
sse_transport = SseServerTransport("/messages/")


async def handle_sse(request: Request) -> Response:
    """SSE 연결 핸들러"""
    logger.info("SSE connection established")

    # MCP 서버 인스턴스 생성
    mcp_server = UniversalMCPServer()
    await mcp_server.initialize()

    try:
        async with sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send
        ) as streams:
            await mcp_server.server.run(
                streams[0],
                streams[1],
                mcp_server.server.create_initialization_options()
            )
    finally:
        await mcp_server.cleanup()

    return Response()


async def handle_post_message(request: Request) -> Response:
    """POST 메시지 핸들러"""
    return await sse_transport.handle_post_message(request)


# Starlette 라우트 정의
sse_routes = [
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/messages/{message_id}", endpoint=handle_post_message, methods=["POST"]),
]


# MCP SSE 앱 생성
mcp_sse_app = Starlette(routes=sse_routes)

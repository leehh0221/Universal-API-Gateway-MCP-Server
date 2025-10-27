"""
HTTP/SSE MCP Server Implementation
"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

from .handlers import MCPHandlers
from core.api_router import APIRouter


class UniversalMCPServer:
    """HTTP/SSE MCP Server"""

    def __init__(self, api_router: APIRouter):
        self.server = Server("universal-api-gateway")
        self.api_router = api_router
        self.handlers = MCPHandlers(api_router)
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP handlers"""
        @self.server.list_tools()
        async def list_tools():
            return await self.handlers.handle_list_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            return await self.handlers.handle_call_tool(name, arguments)


def create_mcp_sse_app(api_router: APIRouter):
    """Create MCP SSE application as Starlette app"""
    # Create transport with message path relative to mounted app
    # When mounted at /mcp, messages will be at /mcp/messages/
    sse_transport = SseServerTransport("/mcp/messages/")
    mcp_server = UniversalMCPServer(api_router)

    async def handle_sse(request):
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server.server.run(
                streams[0], streams[1],
                mcp_server.server.create_initialization_options()
            )

    async def handle_messages(request):
        return await sse_transport.handle_post_message(
            request.scope, request.receive, request._send
        )

    # Create Starlette app with routes
    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages/", endpoint=handle_messages, methods=["POST"]),
        ]
    )

    return app

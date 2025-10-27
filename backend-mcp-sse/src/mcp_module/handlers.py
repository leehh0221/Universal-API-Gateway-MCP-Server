"""
MCP 요청 핸들러
"""
import json
from typing import Any, Dict, List

from mcp.types import Tool, TextContent

from core.api_router import APIRouter
from .tools import create_tools_from_apis
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MCPHandlers:
    """MCP 요청 핸들러 클래스"""

    def __init__(self, api_router: APIRouter):
        """
        Args:
            api_router: APIRouter 인스턴스
        """
        self.api_router = api_router

    async def handle_list_tools(self) -> List[Tool]:
        """
        사용 가능한 모든 도구 목록 반환

        Returns:
            Tool 목록
        """
        apis = list(self.api_router.apis.values())
        tools = create_tools_from_apis(apis)

        logger.info(f"Listed {len(tools)} tools from {len(apis)} APIs")
        return tools

    async def handle_call_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """
        도구 호출 및 결과 반환

        Args:
            name: Tool 이름
            arguments: 호출 인자

        Returns:
            TextContent 목록
        """
        try:
            logger.info(f"Calling tool: {name} with args: {arguments}")

            # API 라우팅
            result = await self.api_router.route_request(
                tool_name=name,
                arguments=arguments
            )

            # 결과 포맷팅
            response_text = json.dumps(result, ensure_ascii=False, indent=2)

            return [TextContent(
                type="text",
                text=response_text
            )]

        except Exception as e:
            logger.error(f"Error calling tool {name}: {str(e)}", exc_info=True)

            error_response = {
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }

            return [TextContent(
                type="text",
                text=json.dumps(error_response, ensure_ascii=False, indent=2)
            )]

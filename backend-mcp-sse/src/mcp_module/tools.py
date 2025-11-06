"""
MCP Tool 변환 로직
"""
from typing import List

from mcp.types import Tool

from models.api_definition import APIDefinition


def create_tools_from_apis(apis: List[APIDefinition]) -> List[Tool]:
    """
    API 정의에서 MCP Tool 목록 생성

    Args:
        apis: API 정의 목록

    Returns:
        MCP Tool 목록
    """
    tools = []

    for api in apis:
        for endpoint in api.endpoints:
            # JSON Schema 생성
            input_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }

            # 파라미터를 JSON Schema로 변환
            for param_name, param_def in endpoint.parameters.items():
                prop = {
                    "type": param_def.type,
                    "description": param_def.description
                }

                # 기본값 추가
                if param_def.default is not None:
                    prop["default"] = param_def.default

                # 범위 제약 추가
                if param_def.min is not None:
                    prop["minimum"] = param_def.min
                if param_def.max is not None:
                    prop["maximum"] = param_def.max

                # Enum 추가
                if param_def.enum is not None:
                    prop["enum"] = param_def.enum

                input_schema["properties"][param_name] = prop

                # 필수 파라미터 추가
                if param_def.required:
                    input_schema["required"].append(param_name)

            # Tool 객체 생성
            tool = Tool(
                name=endpoint.name,
                description=f"[{api.display_name}] {endpoint.description}",
                inputSchema=input_schema
            )
            tools.append(tool)

    return tools

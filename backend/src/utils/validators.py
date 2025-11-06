"""
입력 검증 유틸리티
"""
from typing import Any, Dict

from models.api_definition import ParameterDefinition


class ValidationError(Exception):
    """검증 오류"""
    pass


def validate_parameters(
    arguments: Dict[str, Any],
    parameter_defs: Dict[str, ParameterDefinition]
) -> None:
    """
    사용자 입력 파라미터 검증

    Args:
        arguments: 사용자가 전달한 인자
        parameter_defs: 파라미터 정의

    Raises:
        ValidationError: 검증 실패 시
    """
    # 필수 파라미터 확인
    for param_name, param_def in parameter_defs.items():
        if param_def.required and param_name not in arguments:
            raise ValidationError(f"Required parameter missing: {param_name}")

    # 각 파라미터 검증
    for param_name, value in arguments.items():
        if param_name not in parameter_defs:
            raise ValidationError(f"Unknown parameter: {param_name}")

        param_def = parameter_defs[param_name]

        # 타입 검증
        if param_def.type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValidationError(f"{param_name} must be an integer")
        elif param_def.type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValidationError(f"{param_name} must be a number")
        elif param_def.type == "string":
            if not isinstance(value, str):
                raise ValidationError(f"{param_name} must be a string")
        elif param_def.type == "boolean":
            if not isinstance(value, bool):
                raise ValidationError(f"{param_name} must be a boolean")

        # 범위 검증 (숫자 타입만)
        if param_def.type in ("integer", "number"):
            if param_def.min is not None and value < param_def.min:
                raise ValidationError(
                    f"{param_name} must be >= {param_def.min}"
                )
            if param_def.max is not None and value > param_def.max:
                raise ValidationError(
                    f"{param_name} must be <= {param_def.max}"
                )

        # Enum 검증
        if param_def.enum is not None and value not in param_def.enum:
            raise ValidationError(
                f"{param_name} must be one of {param_def.enum}"
            )

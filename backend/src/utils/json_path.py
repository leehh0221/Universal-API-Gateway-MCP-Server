"""
간단한 JSONPath 파서 (MVP용)
"""
from typing import Any, Optional


def extract_json_path(data: Any, path: str) -> Any:
    """
    간단한 JSONPath 추출

    $.response.data 형식만 지원
    더 복잡한 JSONPath는 jsonpath-ng 라이브러리 사용 필요

    Args:
        data: JSON 데이터
        path: JSONPath 경로 (예: $.response.data)

    Returns:
        추출된 데이터
    """
    if not path or not path.startswith("$."):
        return data

    # $ 제거하고 . 으로 split
    keys = path[2:].split(".")

    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return None
        elif isinstance(result, list) and key.isdigit():
            index = int(key)
            if 0 <= index < len(result):
                result = result[index]
            else:
                return None
        else:
            return None

    return result

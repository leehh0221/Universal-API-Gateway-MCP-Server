"""
애플리케이션 설정
"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""

    # 기본 설정
    APP_NAME: str = "Universal API Gateway"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # 경로 설정
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data" / "apis"

    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # 보안 설정
    ALLOWED_DOMAINS: List[str] = [
        "api.steampowered.com",
        "api.open-meteo.com",
        "newsapi.org"
    ]

    BLOCKED_IP_RANGES: List[str] = [
        "127.0.0.0/8",      # localhost
        "10.0.0.0/8",       # Private A
        "172.16.0.0/12",    # Private B
        "192.168.0.0/16",   # Private C
        "169.254.0.0/16",   # Link-local
    ]

    # Rate Limiting
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # HTTP 클라이언트
    HTTP_TIMEOUT: int = 30  # seconds
    HTTP_MAX_REDIRECTS: int = 5

    # 로깅
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# 전역 설정 인스턴스
settings = Settings()

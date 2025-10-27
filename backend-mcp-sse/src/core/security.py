"""
보안 유틸리티
"""
import ipaddress
from urllib.parse import urlparse
from typing import List

from core.config import settings


class SecurityError(Exception):
    """보안 관련 오류"""
    pass


def validate_url(url: str) -> bool:
    """
    URL이 허용된 도메인인지 확인

    Args:
        url: 확인할 URL

    Returns:
        허용 여부
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc

        # 포트 번호 제거
        if ":" in domain:
            domain = domain.split(":")[0]

        return domain in settings.ALLOWED_DOMAINS
    except Exception:
        return False


def validate_not_internal_ip(url: str) -> bool:
    """
    URL이 내부 IP를 가리키지 않는지 확인
    SSRF 공격 방지

    Args:
        url: 확인할 URL

    Returns:
        안전 여부 (True = 안전, False = 내부 IP)
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False

        # IP 주소인 경우
        try:
            ip = ipaddress.ip_address(hostname)

            # 차단된 IP 범위 확인
            for cidr in settings.BLOCKED_IP_RANGES:
                network = ipaddress.ip_network(cidr)
                if ip in network:
                    return False

            return True

        except ValueError:
            # 도메인 이름인 경우는 일단 허용
            # (실제로는 DNS 조회 후 IP 확인 필요)
            return True

    except Exception:
        return False


def check_security(url: str) -> None:
    """
    URL 보안 검사

    Args:
        url: 확인할 URL

    Raises:
        SecurityError: 보안 검사 실패 시
    """
    if not validate_url(url):
        raise SecurityError(f"URL domain not allowed: {url}")

    if not validate_not_internal_ip(url):
        raise SecurityError(f"Internal IP address not allowed: {url}")

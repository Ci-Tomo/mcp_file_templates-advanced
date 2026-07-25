"""Google Maps API 用の共通 HTTP セッション。"""

import logging
import random
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .errors import (
    MapsAPIError,
    NETWORK_TIMEOUT_MESSAGE,
    RATE_LIMIT_MESSAGE,
    raise_maps_error,
)

logger = logging.getLogger(__name__)


def create_google_maps_session(
    api_key: str, timeout_connect_s: int = 5, timeout_read_s: int = 5
) -> requests.Session:
    """Google Maps API 用の共通セッションを作成する。"""
    session = requests.Session()
    session.headers.update({"X-Goog-Api-Key": api_key})

    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.timeout = (timeout_connect_s, timeout_read_s)
    return session


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    *,
    headers: Optional[dict] = None,
    json: Optional[dict] = None,
    params: Optional[dict] = None,
    max_retries: int = 3,
) -> dict:
    """リトライ付き HTTP リクエスト。成功時は JSON 辞書を返す。"""
    request_headers = dict(session.headers)
    if headers:
        request_headers.update(headers)
    timeout = getattr(session, "timeout", (5, 5))

    for attempt in range(max_retries):
        try:
            logger.info(
                "Request: %s %s (attempt %s/%s)",
                method,
                url,
                attempt + 1,
                max_retries,
            )
            start_time = time.time()
            response = session.request(
                method=method,
                url=url,
                headers=request_headers,
                json=json,
                params=params,
                timeout=timeout,
            )
            latency = time.time() - start_time
            logger.info(
                "Response: status=%s, latency=%.3fs",
                response.status_code,
                latency,
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code in [429, 500, 502, 503, 504]:
                if attempt < max_retries - 1:
                    wait_time = (2**attempt) + random.uniform(0, 1)
                    logger.warning(
                        "Retryable error %s, waiting %.2fs",
                        response.status_code,
                        wait_time,
                    )
                    time.sleep(wait_time)
                    continue

            try:
                response_body = response.json()
            except Exception:
                response_body = None
            raise_maps_error(response.status_code, response_body)

        except requests.Timeout:
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                logger.warning("Timeout, waiting %.2fs before retry", wait_time)
                time.sleep(wait_time)
                continue
            raise MapsAPIError(NETWORK_TIMEOUT_MESSAGE, category="NETWORK_TIMEOUT")

        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                logger.warning(
                    "Request exception: %s, waiting %.2fs", e, wait_time
                )
                time.sleep(wait_time)
                continue
            raise MapsAPIError(NETWORK_TIMEOUT_MESSAGE, category="NETWORK_TIMEOUT")

    raise MapsAPIError(RATE_LIMIT_MESSAGE, category="RATE_LIMIT")

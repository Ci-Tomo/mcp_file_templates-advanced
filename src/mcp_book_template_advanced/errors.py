"""Google Maps API エラーの日本語化。"""

from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

NETWORK_TIMEOUT_MESSAGE = (
    "ネットワークまたはタイムアウトの問題が発生しました（5 秒）。"
    "通信状況をご確認のうえ再実行してください。"
)
RATE_LIMIT_MESSAGE = (
    "リクエストが集中しています。しばらく時間をおいてから再実行してください。"
)


class MapsAPIError(Exception):
    """Google Maps API エラー。"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        category: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.category = category


def map_http_error_to_message(
    status_code: int, response_body: Optional[Any] = None
) -> str:
    """HTTP ステータスをエージェント向け日本語メッセージに変換する。"""
    if isinstance(response_body, dict):
        error_info = response_body.get("error", {}) or {}
        error_message = error_info.get("message", "")
        status = error_info.get("status", "")
        logger.warning(
            "Maps API error: status_code=%s, error_status=%s, error_message=%s",
            status_code,
            status or "N/A",
            (error_message[:100] if error_message else "N/A"),
        )

    if status_code == 400:
        return (
            "リクエスト内容に不備があります。"
            "地点名やパラメータを見直してから再実行してください。"
        )
    if status_code == 401:
        return (
            "認証に失敗しました。"
            "API キーの設定（環境変数 GOOGLE_MAPS_API_KEY）を確認してください。"
        )
    if status_code == 403:
        return (
            "権限エラーが発生しました。"
            "対象 API の有効化やキーの権限設定、リファラ/IP 制限をご確認ください。"
        )
    if status_code == 404:
        return "指定された地点を見つけられませんでした。入力内容をご確認ください。"
    if status_code == 429:
        return RATE_LIMIT_MESSAGE
    if 500 <= status_code < 600:
        return (
            "サービスが混雑または一時的に利用できません。"
            "時間をおいて再実行してください。"
        )
    return (
        f"API リクエストでエラーが発生しました（HTTP {status_code}）。"
        "時間をおいて再実行してください。"
    )


def raise_maps_error(status_code: int, response_body: Optional[Any] = None) -> None:
    """HTTP エラーを MapsAPIError として送出する。"""
    message = map_http_error_to_message(status_code, response_body)
    category = "UNKNOWN"
    if status_code == 400:
        category = "INVALID_ARGUMENT"
    elif status_code == 401:
        category = "AUTH"
    elif status_code == 403:
        category = "PERMISSION"
    elif status_code == 404:
        category = "NOT_FOUND"
    elif status_code == 429:
        category = "RATE_LIMIT"
    elif 500 <= status_code < 600:
        category = "SERVER"
    raise MapsAPIError(message, status_code=status_code, category=category)

"""MCP サーバー — Place Text Search 連携。"""

import logging
import os
import sys
from pathlib import Path

# パッケージ外から直接実行されたときの import 経路を確保
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastmcp import FastMCP
from pydantic import Field

from mcp_book_template_advanced.clients.places import search_text_candidates_for_display
from mcp_book_template_advanced.errors import MapsAPIError
from mcp_book_template_advanced.http_session import create_google_maps_session
from mcp_book_template_advanced.messages import (
    INVALID_QUERY_MESSAGE,
    MISSING_FIELDS_TEMPLATE,
    NO_CANDIDATES_MESSAGE,
    SUCCESS_ALL_FIELDS,
    UNEXPECTED_ERROR_MESSAGE,
)
from mcp_book_template_advanced.schemas import (
    CandidateItem,
    SearchPlaceError,
    SearchPlaceOk,
    SearchPlaceOutput,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP("mcp-book-template-advanced")

_session = None


def _get_session():
    """共通セッションを遅延初期化する。"""
    global _session
    if _session is None:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise ValueError(
                "環境変数 GOOGLE_MAPS_API_KEY が設定されていません。"
                "API キーを設定してから再実行してください。"
            )
        _session = create_google_maps_session(api_key)
        logger.info("Google Maps session initialized")
    return _session


@mcp.tool(description="曖昧なクエリから最大5件の候補を返します。")
def maps_search_place(
    query: str = Field(description="検索クエリ（例: '新宿のラーメン屋さん'）"),
) -> SearchPlaceOutput:
    """曖昧な地点検索クエリから最大5件の候補を検索する。

    Places API (New) の Text Search を使用し、各候補の表示名・評価・タイプ・住所を返す。
    """
    try:
        if not query or not isinstance(query, str) or not query.strip():
            return SearchPlaceOutput(
                status="error",
                payload=SearchPlaceError(error=INVALID_QUERY_MESSAGE),
            ).model_dump(exclude_none=True, exclude_unset=True)

        logger.info("maps_search_place: query=%s", query)
        session = _get_session()
        candidates = search_text_candidates_for_display(session, query, page_size=5)

        if not candidates:
            return SearchPlaceOutput(
                status="ok",
                payload=SearchPlaceOk(
                    candidates=[],
                    messages=[NO_CANDIDATES_MESSAGE],
                ),
            ).model_dump(exclude_none=True, exclude_unset=True)

        optional_fields = [
            "primaryTypeDisplayName",
            "rating",
            "userRatingCount",
            "shortFormattedAddress",
        ]
        missing_fields_set: set[str] = set()
        for candidate in candidates:
            for field_name in optional_fields:
                if candidate.get(field_name) is None:
                    missing_fields_set.add(field_name)

        response_candidates = [
            CandidateItem(
                displayName=c["displayName"],
                primaryTypeDisplayName=c.get("primaryTypeDisplayName"),
                rating=c.get("rating"),
                userRatingCount=c.get("userRatingCount"),
                shortFormattedAddress=c.get("shortFormattedAddress"),
            )
            for c in candidates
        ]

        if missing_fields_set:
            messages = [
                MISSING_FIELDS_TEMPLATE.format(
                    names=" または ".join(sorted(missing_fields_set))
                )
            ]
        else:
            messages = [SUCCESS_ALL_FIELDS]

        logger.info("maps_search_place result: %s candidates", len(response_candidates))
        return SearchPlaceOutput(
            status="ok",
            payload=SearchPlaceOk(candidates=response_candidates, messages=messages),
        ).model_dump(exclude_none=True, exclude_unset=True)

    except MapsAPIError as e:
        logger.error("MapsAPIError: %s", e.message)
        return SearchPlaceOutput(
            status="error",
            payload=SearchPlaceError(error=e.message),
        ).model_dump(exclude_none=True, exclude_unset=True)

    except ValueError as e:
        logger.error("Config error: %s", e)
        return SearchPlaceOutput(
            status="error",
            payload=SearchPlaceError(error=str(e)),
        ).model_dump(exclude_none=True, exclude_unset=True)

    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return SearchPlaceOutput(
            status="error",
            payload=SearchPlaceError(error=UNEXPECTED_ERROR_MESSAGE),
        ).model_dump(exclude_none=True, exclude_unset=True)


def main():
    mcp.run()


if __name__ == "__main__":
    main()

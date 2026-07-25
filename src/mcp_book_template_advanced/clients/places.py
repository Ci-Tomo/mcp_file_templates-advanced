"""Places API — Text Search クライアント。"""

import logging

import requests

from ..field_masks import build_search_place_candidates_field_mask
from ..http_session import request_with_retry

logger = logging.getLogger(__name__)

PLACES_BASE_URL = "https://places.googleapis.com/v1"


def search_text_candidates_for_display(
    session: requests.Session,
    text_query: str,
    page_size: int = 5,
) -> list[dict]:
    """Text Search を実行し、候補表示用の辞書リストを返す。

    maps_search_place 専用。place_id は含めない（キャッシュしないため）。
    """
    url = f"{PLACES_BASE_URL}/places:searchText"
    field_mask = build_search_place_candidates_field_mask()
    body = {
        "textQuery": text_query,
        "languageCode": "ja",
        "regionCode": "JP",
        "pageSize": page_size,
    }
    headers = {"Content-Type": "application/json", "X-Goog-FieldMask": field_mask}

    logger.info(
        "Text Search (candidates): query=%s, field_mask=%s", text_query, field_mask
    )
    response = request_with_retry(session, "POST", url, headers=headers, json=body)

    places = response.get("places", [])
    candidates: list[dict] = []

    for place in places:
        display_name_obj = place.get("displayName", {})
        display_name = (
            display_name_obj.get("text", "")
            if isinstance(display_name_obj, dict)
            else ""
        )
        if not display_name:
            continue

        candidate = {
            "displayName": display_name,
            "primaryTypeDisplayName": None,
            "rating": None,
            "userRatingCount": None,
            "shortFormattedAddress": None,
        }

        primary_type_obj = place.get("primaryTypeDisplayName")
        if primary_type_obj and isinstance(primary_type_obj, dict):
            candidate["primaryTypeDisplayName"] = primary_type_obj.get("text")

        if "rating" in place:
            candidate["rating"] = place["rating"]
        if "userRatingCount" in place:
            candidate["userRatingCount"] = place["userRatingCount"]
        if "shortFormattedAddress" in place:
            candidate["shortFormattedAddress"] = place["shortFormattedAddress"]

        candidates.append(candidate)

    logger.info("Text Search (candidates) result: %s candidates", len(candidates))
    return candidates

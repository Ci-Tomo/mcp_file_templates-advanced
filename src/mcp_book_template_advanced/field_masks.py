"""Places API FieldMask ビルダー。"""


def build_search_place_candidates_field_mask() -> str:
    """Text Search（候補表示用）の最小 FieldMask。

    maps_search_place 向け。id は含めない（キャッシュしないため）。
    """
    return (
        "places.displayName,"
        "places.primaryTypeDisplayName,"
        "places.rating,"
        "places.userRatingCount,"
        "places.shortFormattedAddress"
    )

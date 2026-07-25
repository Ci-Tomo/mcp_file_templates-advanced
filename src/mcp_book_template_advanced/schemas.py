"""maps_search_place の入出力スキーマ。"""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class CandidateItem(BaseModel):
    """候補地点の情報。"""

    displayName: str = Field(description="表示名")
    primaryTypeDisplayName: Optional[str] = Field(
        default=None, description="主要タイプ表示名"
    )
    rating: Optional[float] = Field(default=None, description="評価（0-5）")
    userRatingCount: Optional[int] = Field(default=None, description="評価件数")
    shortFormattedAddress: Optional[str] = Field(default=None, description="短い住所")


class SearchPlaceOk(BaseModel):
    """地点検索成功時のペイロード。"""

    candidates: List[CandidateItem] = Field(description="候補リスト（最大5件）")
    messages: List[str] = Field(description="補足メッセージ")


class SearchPlaceError(BaseModel):
    """地点検索時のエラーペイロード。"""

    error: str = Field(description="エラーメッセージ")


class SearchPlaceOutput(BaseModel):
    """maps_search_place の出力エンベロープ。"""

    status: Literal["ok", "error"] = Field(description="処理結果のステータス")
    payload: Union[SearchPlaceOk, SearchPlaceError] = Field(
        description="ステータスに応じたペイロード"
    )

# mcp-book-template-advanced

mcpbook-samples の advanced（`mcp_google_maps`）を参考にした、Google Places API (New) **Text Search** 連携 MCP サーバーです。

## 提供ツール

- **`maps_search_place`**: 曖昧な検索クエリから最大5件の候補を返す

## セットアップ

```bash
uv sync
```

1. [Google Cloud Console](https://console.cloud.google.com/) で **Places API (New)** を有効化
2. API キーを発行
3. `.env.sample` を参考に環境変数を設定

```bash
export GOOGLE_MAPS_API_KEY=YOUR_API_KEY
```

Cursor では `.cursor/mcp.json` の `env.GOOGLE_MAPS_API_KEY` を実キーに置き換えてください。

## 起動

```bash
uv run python src/mcp_book_template_advanced/server.py
```

## レスポンス契約

`{"status": "ok"|"error", "payload": {...}}` のエンベロープ形式です。

- **ok**: 候補リスト（0件含む）+ `messages`
- **error**: 入力不正・API/認証エラーなど

## 構成

```
src/mcp_book_template_advanced/
├── server.py           # MCP ツール定義
├── http_session.py     # API キー認証・リトライ
├── field_masks.py      # X-Goog-FieldMask
├── errors.py / messages.py / schemas.py
└── clients/
    └── places.py       # places:searchText
```

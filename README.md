# mcp-book-template-advanced

FastMCP 3.x ベースの MCP サーバーテンプレートです。

## セットアップ

```bash
uv sync
```

## 起動

```bash
# stdio（Cursor / Claude Desktop 向け）
uv run python server.py

# または CLI
uv run fastmcp run server.py:mcp

# HTTP（ブラウザやリモートクライアント向け）
uv run fastmcp run server.py:mcp --transport http --port 8000
```

## Cursor への接続

プロジェクト内の `.cursor/mcp.json` を用意済みです。Cursor を再起動するか MCP 設定をリロードすると、`mcp-book-template-advanced` サーバーが利用できます。

## ツールの追加

`server.py` に関数を書き、`@mcp.tool` を付けるだけです。

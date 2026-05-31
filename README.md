# Roborock MCP

ClaudeからRoborock掃除機を操作するMCPサーバーです。

## フォルダ構成

```
roborock/
├── README.md           # このファイル
└── roborock_mcp/       # MCPサーバー本体
    ├── auth.py         # 初回認証スクリプト
    ├── \erver.py       # MCPサーバー（FastMCP）
    ├── pyproject.toml  # 依存パッケージ定義
    ├── uv.lock
    └── utils/
        └── logger.py   # ロガー
```

## セットアップ手順

### 1. 初回認証

```bash
cd roborock_mcp
uv run auth.py
```

- メールアドレスを入力
- Roborockアカウントに届いたコードを入力
- `~/.roborock_creds.json` に認証情報が保存される

### 2. MCPサーバーを登録

```bash
claude mcp add roborock -- uv run \
  --project "$(pwd)/roborock_mcp" \
  "$(pwd)/roborock_mcp/server.py"
```

確認：

```bash
claude mcp list
```

`roborock` が表示されれば成功。

### 3. 動作確認

```bash
claude
```

起動後、「roborockのステータス確認して」と話しかけると動作する。

## 再認証

`~/.roborock_creds.json` を削除して `uv run auth.py` を再実行する。

## 実装済みツール

| ツール名 | 説明 |
|---|---|
| `get_roborock_status` | バッテリー残量・掃除状態などを取得 |

## 新しいツールの追加

`server.py` に `@mcp.tool()` デコレータで関数を追加するだけ。

```python
@mcp.tool()
async def start_cleaning(device_index: int = 0) -> str:
    """掃除を開始します。"""
    try:
        device_manager = await get_device_manager()
        # ... 実装
    except Exception as e:
        return f"❌ エラー: {type(e).__name__}: {e}"
```

コードスタイルの注意：
- 1行79文字以内（Flake8 E501）
- `print` は使わず `Log.info` / `Log.error` を使う
- `from utils.logger import Log` をインポートに追加する

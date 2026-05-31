---
name: roborock-add-tool
description: >
  Roborock MCPサーバー（./roborock_mcp/server.py）に
  新しいツールを追加するときに使うスキル。
  「掃除を開始する機能を追加して」「充電に戻す処理を追加したい」「部屋を指定して掃除したい」
  など、Roborock MCPに新しいコマンドや機能を実装したいときは必ずこのスキルを使うこと。
---

# Roborock MCP ツール追加スキル

このスキルは `server.py` に新しい `@mcp.tool()` を追加するための手順を定義する。

## プロジェクト情報

- **サーバーファイル**: `./roborock_mcp/server.py`
- **フレームワーク**: FastMCP（`from mcp.server.fastmcp import FastMCP`）
- **ロガー**: `from utils.logger import Log`（`print` は使わない）
- **ライン制限**: 79文字以内（Flake8 E501）
- **認証**: `get_device_manager()` で取得したデバイスマネージャーを使う

## 実装手順

### 1. server.py を読み込む

まず現在の `server.py` を Read して、既存のツール構造を把握する。

### 2. python-roborock のAPIを調べる

追加したい機能がどのAPIで実現できるか調べる。
`device.v1_properties` 以下にあるトレイトを確認する。

よく使うトレイト例：
- `device.v1_properties.status` — ステータス取得
- `device.v1_properties.clean` — 掃除開始/停止
- `device.v1_properties.charge` — 充電台に戻す

### 3. ツールを追加する

以下のテンプレートに従って `server.py` に追加する：

```python
@mcp.tool()
async def <ツール名>(device_index: int = 0) -> str:
    """
    <日本語での説明>。

    Args:
        device_index: デバイスのインデックス（複数台ある場合。デフォルト0）
    """
    try:
        device_manager = await get_device_manager()
        devices = await device_manager.get_devices()
        vacuum_devices = [d for d in devices if d.v1_properties]

        if not vacuum_devices:
            return "掃除機デバイスが見つかりませんでした。"

        if device_index >= len(vacuum_devices):
            return (
                f"デバイスインデックス {device_index} は範囲外です。"
                f"見つかったデバイス数: {len(vacuum_devices)}"
            )

        device = vacuum_devices[device_index]
        # ここに処理を書く

        return "✅ <成功メッセージ>"

    except FileNotFoundError as e:
        return f"❌ 認証エラー: {e}"
    except Exception as e:
        return f"❌ エラー: {type(e).__name__}: {e}"
```

### 4. コードスタイルチェック

追加後に以下を確認する：

- 1行が79文字を超えていないか（長い行は複数行に分割する）
- `print` を使っていないか（`Log.info` / `Log.error` を使う）
- `Log` をインポートしているか（`from utils.logger import Log`）
- 型ヒントが付いているか

### 5. 動作確認の案内

実装後、ユーザーに伝えること：

> Claude Desktop を再起動すると新しいツールが使えるようになります。
> 「<ツール名>して」と話しかけてみてください。

## コードスタイル詳細

### 長い行の折り返し方

```python
# NG（80文字超）
status_dict = {k: v for k, v in vars(obj).items() if not k.startswith("_")}

# OK（複数行に分割）
status_dict = {
    k: v for k, v in vars(obj).items()
    if not k.startswith("_")
}
```

```python
# NG（80文字超）
return f"デバイスインデックス {device_index} は範囲外です。見つかったデバイス数: {len(vacuum_devices)}"

# OK（括弧で複数行に分割）
return (
    f"デバイスインデックス {device_index} は範囲外です。"
    f"見つかったデバイス数: {len(vacuum_devices)}"
)
```

### Log の使い方

```python
from utils.logger import Log

Log.info("掃除を開始しました")
Log.error(f"エラーが発生しました: {e}")
Log.debug(f"デバイス数: {len(devices)}")
```

#!/usr/bin/env python3
"""
Roborock MCP Server (FastMCP)
Claudeからルンバ（Roborock）のステータスを確認できるMCPサーバー。

事前に auth.py を実行して ~/.roborock_creds.json を作成してください。
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from roborock import RoborockCommand
from roborock.devices.device_manager import create_device_manager, UserParams
from roborock.data.containers import UserData

CREDS_PATH = Path.home() / ".roborock_creds.json"

mcp = FastMCP("roborock")


def load_creds() -> dict:
    if not CREDS_PATH.exists():
        raise FileNotFoundError(
            f"Credentials not found at {CREDS_PATH}. "
            "Please run auth.py first."
        )
    return json.loads(CREDS_PATH.read_text())


async def get_device_manager():
    creds = load_creds()
    email = creds["email"]
    user_data = UserData.from_dict(creds["user_data"])
    user_params = UserParams(username=email, user_data=user_data)
    return await create_device_manager(user_params)


async def get_vacuum_device(device_index: int = 0):
    device_manager = await get_device_manager()
    devices = await device_manager.get_devices()
    vacuum_devices = [d for d in devices if d.v1_properties]

    if not vacuum_devices:
        raise ValueError("掃除機デバイスが見つかりませんでした。")

    if device_index >= len(vacuum_devices):
        raise ValueError(
            f"デバイスインデックス {device_index} は範囲外です。"
            f"見つかったデバイス数: {len(vacuum_devices)}"
        )

    return vacuum_devices[device_index]


@mcp.tool()
async def get_roborock_status(device_index: int = 0) -> str:
    """
    Roborock掃除機のステータスを取得します。
    バッテリー残量、掃除状態（掃除中/待機中/充電中など）、エラー情報などを返します。

    Args:
        device_index: デバイスのインデックス（複数台ある場合。デフォルト0）
    """
    try:
        device = await get_vacuum_device(device_index)
        status_trait = device.v1_properties.status
        await status_trait.refresh()

        device_name = getattr(device, "name", f"Device {device_index}")
        lines = [f"🤖 デバイス名: {device_name}"]

        if hasattr(status_trait, "model_dump"):
            status_dict = status_trait.model_dump()
        elif hasattr(status_trait, "__dict__"):
            status_dict = {
                k: v for k, v in vars(status_trait).items()
                if not k.startswith("_")
            }
        else:
            return str(status_trait)

        key_labels = {
            "state": "状態",
            "battery": "バッテリー",
            "battery_level": "バッテリー残量",
            "error_code": "エラーコード",
            "clean_time": "掃除時間（秒）",
            "clean_area": "掃除面積",
            "fan_power": "吸引力",
            "in_cleaning": "掃除中",
            "in_returning": "帰還中",
        }

        for key, label in key_labels.items():
            if status_dict.get(key) is not None:
                lines.append(f"  {label}: {status_dict[key]}")

        other = {
            k: v for k, v in status_dict.items()
            if k not in key_labels and v is not None
        }
        if other:
            lines.append("  --- その他 ---")
            for k, v in other.items():
                lines.append(f"  {k}: {v}")

        return "\n".join(lines)

    except FileNotFoundError as e:
        return f"❌ 認証エラー: {e}"
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        return f"❌ エラー: {type(e).__name__}: {e}"


@mcp.tool()
async def start_cleaning(device_index: int = 0) -> str:
    """
    Roborock掃除機の掃除を開始します。

    Args:
        device_index: デバイスのインデックス（複数台ある場合。デフォルト0）
    """
    try:
        device = await get_vacuum_device(device_index)
        await device.v1_properties.command.send(RoborockCommand.APP_START)
        device_name = getattr(device, "name", f"Device {device_index}")
        return f"✅ {device_name} の掃除を開始しました。"

    except FileNotFoundError as e:
        return f"❌ 認証エラー: {e}"
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        return f"❌ エラー: {type(e).__name__}: {e}"


@mcp.tool()
async def stop_cleaning(device_index: int = 0) -> str:
    """
    Roborock掃除機の掃除を終了します。

    Args:
        device_index: デバイスのインデックス（複数台ある場合。デフォルト0）
    """
    try:
        device = await get_vacuum_device(device_index)
        await device.v1_properties.command.send(RoborockCommand.APP_STOP)
        device_name = getattr(device, "name", f"Device {device_index}")
        return f"✅ {device_name} の掃除を終了しました。"

    except FileNotFoundError as e:
        return f"❌ 認証エラー: {e}"
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        return f"❌ エラー: {type(e).__name__}: {e}"


if __name__ == "__main__":
    mcp.run()

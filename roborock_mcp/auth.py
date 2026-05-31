#!/usr/bin/env python3
"""
初回認証スクリプト。
実行するとメールにコードが届くので入力すると ~/.roborock_creds.json に保存されます。
"""

import asyncio
import dataclasses
import json
from pathlib import Path

from roborock.web_api import RoborockApiClient

from utils.logger import Log

CREDS_PATH = Path.home() / ".roborock_creds.json"


class _RoborockEncoder(json.JSONEncoder):
    """Roborock オブジェクトを再帰的に dict/list に変換するエンコーダー。"""

    def default(self, obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return dataclasses.asdict(obj)
        if hasattr(obj, "__dict__"):
            return vars(obj)
        return super().default(obj)


async def main():
    email = input("Roborock account email: ").strip()
    web_api = RoborockApiClient(username=email)

    Log.info(f"Sending login code to {email}...")
    await web_api.request_code()

    code = input("Enter the code from your email: ").strip()
    user_data = await web_api.code_login(code)

    creds = {"email": email, "user_data": user_data}
    CREDS_PATH.write_text(
        json.dumps(creds, indent=2, ensure_ascii=False, cls=_RoborockEncoder)
    )
    Log.info(f"Credentials saved to {CREDS_PATH}")
    Log.info("Now you can start the MCP server.")


if __name__ == "__main__":
    asyncio.run(main())

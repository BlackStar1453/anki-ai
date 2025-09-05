#!/usr/bin/env python3
"""
演示脚本：列出 OpenAI 模型。
使用环境变量或 config.json 中的 openai_api_key。
"""
import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.openai_service import OpenAIService
from config import Config


def main():
    # 优先使用环境变量
    api_key = os.environ.get("OPENAI_API_KEY") or Config.get("openai_api_key", "")
    svc = OpenAIService()
    svc.api_key = api_key
    ok, models, msg = svc.list_models()
    if not ok:
        print("❌ 获取模型失败:", msg)
        return 1
    print("✅ 模型数量:", len(models))
    for m in models[:20]:
        print(" -", m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""
Anki LLM 环境诊断脚本（不依赖 anki 运行，也可在 Anki 的 Python 控制台运行）
- 检查 Python/平台信息
- 检查 vendor 路径与依赖可见性
- 尝试导入 pydantic_core、litellm、openai，并打印完整堆栈
- 可选：用 requests 直连 OpenAI 的最小连通性测试（需要 API Key）

注意：本脚本不安装、不修改任何环境，仅输出诊断信息。
"""

import sys
import os
import platform
import importlib
import traceback
import json


def header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def show_python_env():
    header("1) Python 与平台信息")
    print("Python:", sys.version)
    print("sys.platform:", sys.platform)
    print("machine:", platform.machine())
    print("processor:", platform.processor())
    print("architecture:", platform.architecture())
    print("maxsize(bits):", 64 if sys.maxsize > 2**32 else 32)


def show_paths_and_vendor():
    header("2) sys.path 与 vendor 可见性")
    print("sys.path 前 10 项:")
    for p in sys.path[:10]:
        print("  -", p)
    # 猜测运行目录的 vendor
    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(here, os.pardir))
    likely_vendor = os.path.join(project_root, 'vendor')
    print("推测的 vendor 路径:", likely_vendor, "存在:" , os.path.isdir(likely_vendor))

    # 尝试定位 pydantic_core 所在文件
    core_dir = os.path.join(likely_vendor, 'pydantic_core')
    print("pydantic_core 目录存在:", os.path.isdir(core_dir))
    if os.path.isdir(core_dir):
        files = [f for f in os.listdir(core_dir) if f.startswith('_pydantic_core.')]
        print("pydantic_core/_pydantic_core.*:", files)


def try_import(name: str):
    header(f"3) 尝试导入: {name}")
    try:
        mod = importlib.import_module(name)
        print(f"✅ 导入成功: {name}")
        f = getattr(mod, '__file__', None)
        if f:
            print("  __file__:", f)
        return True
    except Exception:
        print(f"❌ 导入失败: {name}")
        print(traceback.format_exc())
        return False


def test_openai_requests():
    header("4) OpenAI 直连（requests）最小连通性测试（可选）")
    try:
        import requests
    except Exception:
        print("❌ 无法导入 requests。请安装或确保其在 vendor 中。")
        print(traceback.format_exc())
        return

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ 未在环境变量中找到 OPENAI_API_KEY。跳过 HTTP 测试。")
        print("   如需测试，可先执行: export OPENAI_API_KEY=sk-... 再运行脚本。")
        return

    try:
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(url, headers=headers, timeout=15)
        print("HTTP 状态码:", resp.status_code)
        if resp.status_code >= 400:
            print("响应片段:", resp.text[:500])
        else:
            data = resp.json()
            print("返回字段: keys=", list(data.keys()))
    except Exception:
        print("❌ HTTP 测试异常：")
        print(traceback.format_exc())


def main():
    show_python_env()
    show_paths_and_vendor()

    # 依赖导入顺序: pydantic_core -> pydantic -> litellm/openai
    try_import('pydantic_core')
    try_import('pydantic')
    try_import('litellm')
    try_import('openai')

    # 可选连通性
    test_openai_requests()


if __name__ == '__main__':
    main()


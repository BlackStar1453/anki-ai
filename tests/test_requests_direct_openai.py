import os
import json
import unittest

# 优先从插件路径导入
import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.openai_service import OpenAIService

class TestRequestsDirectOpenAI(unittest.TestCase):
    def setUp(self):
        self.svc = OpenAIService()

    def test_missing_requests(self):
        # 如果 requests 存在则跳过该检查
        try:
            import requests  # noqa: F401
        except Exception:
            msg = self.svc.get_response([{"role": "user", "content": "hi"}])
            self.assertIn("requests", msg.lower())

    def test_invalid_key(self):
        self.svc.api_key = "sk-placeholder-key-here"
        ok, msg = self.svc.validate_api_key()
        self.assertFalse(ok)
        self.assertIn("invalid", msg.lower())

    def test_min_body(self):
        # 构造一个最小消息体，不实际发请求
        payload = {
            "model": self.svc.model,
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": self.svc.max_tokens,
            "temperature": self.svc.temperature,
        }
        body = json.dumps(payload)
        self.assertIn("model", body)
        self.assertIn("messages", body)

if __name__ == '__main__':
    unittest.main()


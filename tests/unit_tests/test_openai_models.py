import unittest
import sys
import pathlib
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.openai_service import OpenAIService


class TestOpenAIModels(unittest.TestCase):
    def setUp(self):
        self.svc = OpenAIService()
        self.svc.api_key = "sk-test"

    @mock.patch("services.openai_service.requests.get")
    def test_list_models_success(self, mget):
        mget.return_value = mock.Mock(status_code=200, json=lambda: {
            "data": [
                {"id": "gpt-3.5-turbo"},
                {"id": "gpt-4o-mini"},
                {"id": "text-embedding-3-small"}
            ]
        })
        ok, models, msg = self.svc.list_models()
        self.assertTrue(ok)
        self.assertIn("gpt-3.5-turbo", models)
        self.assertIn("gpt-4o-mini", models)
        self.assertNotIn("text-embedding-3-small", models)

    @mock.patch("services.openai_service.requests.get")
    def test_list_models_http_error(self, mget):
        mget.return_value = mock.Mock(status_code=401, text="Unauthorized")
        ok, models, msg = self.svc.list_models()
        self.assertFalse(ok)
        self.assertEqual(models, [])
        self.assertIn("HTTP 401", msg)


if __name__ == "__main__":
    unittest.main()


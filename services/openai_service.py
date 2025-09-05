# OpenAI API服务（requests 直连实现，避免二进制依赖）

import logging
import os
import json
from typing import List, Dict

# 尝试相对导入，如果失败则使用绝对导入
try:
    from ..config import Config
except ImportError:
    from config import Config

try:
    import requests
except Exception:
    requests = None

class OpenAIService:
    """OpenAI API服务类（不依赖 openai 官方包，避免 pydantic-core 依赖）"""

    def __init__(self):
        """初始化OpenAI服务"""
        openai_config = Config.get_openai_config()

        self.api_key = openai_config.get("api_key", "")
        self.model = openai_config.get("model", "")
        self.max_tokens = openai_config.get("max_tokens", 500)
        self.temperature = openai_config.get("temperature", 0.7)

        self.logger = logging.getLogger(__name__)
        self.endpoint = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")

    def get_response(self, conversation_history: List[Dict[str, str]]):
        """获取AI回复（一次性请求）"""
        if not conversation_history:
            return self._handle_api_error("Empty conversation history")
        if not requests:
            return self._handle_api_error("'requests' library not available")
        if not self.api_key:
            return self._handle_api_error("Invalid or missing API key")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": self.model,
                "messages": conversation_history,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            resp = requests.post(self.endpoint, headers=headers, data=json.dumps(body), timeout=30)
            if resp.status_code >= 400:
                return self._handle_api_error(f"HTTP {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return self._handle_api_error("No response choices from API")
            content = choices[0].get("message", {}).get("content")
            if not content:
                return self._handle_api_error("Empty response from API")
            return content.strip()
        except Exception as e:
            return self._handle_api_error(str(e))

    def stream_response(self, conversation_history: List[Dict[str, str]]):
        """流式响应生成器（使用 OpenAI Chat Completions 流式接口）"""
        if not requests:
            raise RuntimeError("'requests' library not available")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        body = {
            "model": self.model,
            "messages": conversation_history,
            "temperature": self.temperature,
            "stream": True
        }
        with requests.post(self.endpoint, headers=headers, data=json.dumps(body), stream=True, timeout=60) as r:
            r.raise_for_status()
            buffer = ""
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[len("data: "):].strip()
                    if data == "[DONE]":
                        break
                    # 有些网关可能一次传多条 JSON，用换行或空格相连，这里做一次拆分
                    chunks = [data]
                    if "}{" in data:
                        # 朴素拆分，尽量不中断
                        chunks = data.replace('}{', '}\n{').split('\n')
                    for chunk in chunks:
                        if not chunk or chunk == "[DONE]":
                            continue
                        try:
                            obj = json.loads(chunk)
                            choices = obj.get("choices", [])
                            if not choices:
                                continue
                            choice = choices[0]
                            delta = None
                            # 兼容 Azure/第三方的字段名
                            if "delta" in choice:
                                delta = choice["delta"].get("content")
                            elif "message" in choice and isinstance(choice["message"], dict):
                                delta = choice["message"].get("content")
                            if delta:
                                yield delta
                            # 处理结束原因
                            finish = choice.get("finish_reason")
                            if finish:
                                return
                        except Exception:
                            continue

    def _handle_api_error(self, error_message: str):
        """处理API错误"""
        error_text = f"AI服务暂时不可用: {error_message}"
        if hasattr(self, 'logger'):
            self.logger.error(f"OpenAI API Error: {error_message}")
        else:
            print(f"OpenAI API Error: {error_message}")
        return error_text

    def validate_api_key(self):
        """验证API密钥（最小化请求）"""
        if not requests:
            return False, "'requests' library not available"
        if not self.api_key:
            return False, "Invalid or missing API key"
        try:
            # 如果未指定模型，改用 models 列表接口做快速校验
            if not self.model:
                url = os.environ.get("OPENAI_MODELS_URL", "https://api.openai.com/v1/models")
                headers = {"Authorization": f"Bearer {self.api_key}"}
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code >= 400:
                    return False, f"HTTP {resp.status_code}: {resp.text[:300]}"
                return True, "API key is valid"
            # 有模型时，最小请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": self.model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1
            }
            resp = requests.post(self.endpoint, headers=headers, data=json.dumps(body), timeout=15)
            if resp.status_code >= 400:
                return False, f"HTTP {resp.status_code}: {resp.text[:300]}"
            return True, "API key is valid"
        except Exception as e:
            return False, f"API key validation failed: {str(e)}"

    def get_service_status(self):
        """获取服务状态"""
        status = {
            "openai_available": True,  # requests 直连，不依赖 openai 包
            "api_key_set": bool(self.api_key),
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        return status

    def update_config(self, new_config):
        """更新配置"""
        if "openai_api_key" in new_config:
            self.api_key = new_config["openai_api_key"]
        elif "api_key" in new_config:
            self.api_key = new_config["api_key"]

        if "openai_model" in new_config:
            self.model = new_config["openai_model"]
        elif "model" in new_config:
            self.model = new_config["model"]

        if "max_tokens" in new_config:
            self.max_tokens = new_config["max_tokens"]

        if "temperature" in new_config:
            self.temperature = new_config["temperature"]

    def list_models(self):
        """列出可用模型（OpenAI /v1/models），过滤常见聊天模型"""
        if not requests:
            return False, [], "'requests' library not available"
        if not self.api_key:
            return False, [], "Missing API key"
        try:
            url = os.environ.get("OPENAI_MODELS_URL", "https://api.openai.com/v1/models")
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code >= 400:
                return False, [], f"HTTP {resp.status_code}: {resp.text[:300]}"
            data = resp.json()
            items = data.get("data", [])
            ids = [m.get("id") for m in items if isinstance(m, dict) and m.get("id")]
            # 粗略过滤常用聊天模型关键词
            chat_ids = [i for i in ids if any(k in i for k in ["gpt-", "o-"])]
            return True, chat_ids, "OK"
        except Exception as e:
            return False, [], str(e)

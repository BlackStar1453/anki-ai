# 简化的AI服务 - 使用HTTP请求直接调用OpenAI API

import json
import logging
import requests
import time

# 尝试相对导入，如果失败则使用绝对导入
try:
    from ..config import Config
except ImportError:
    from config import Config

class AIService:
    """简化的AI服务类 - 直接使用HTTP请求"""
    
    def __init__(self):
        """初始化AI服务"""
        # 获取配置
        openai_config = Config.get_openai_config()
        
        self.api_key = openai_config.get("api_key", "sk-placeholder-key-here")
        self.model = openai_config.get("model", "gpt-3.5-turbo")
        self.max_tokens = openai_config.get("max_tokens", 500)
        self.temperature = openai_config.get("temperature", 0.7)
        self.base_url = "https://api.openai.com/v1"
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def get_response(self, conversation_history):
        """获取AI回复"""
        if not conversation_history:
            return self._handle_api_error("Empty conversation history")

        try:
            # 准备请求数据
            messages = self._prepare_messages(conversation_history)
            
            # 构建请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            # 检查响应
            if response.status_code == 200:
                result = response.json()
                if result.get("choices") and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "response": content.strip(),
                        "usage": result.get("usage", {})
                    }
                else:
                    return self._handle_api_error("No response from AI")
            else:
                error_msg = f"API request failed: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', response.text)}"
                    except:
                        error_msg += f" - {response.text}"
                return self._handle_api_error(error_msg)
                
        except requests.exceptions.Timeout:
            return self._handle_api_error("Request timeout")
        except requests.exceptions.ConnectionError:
            return self._handle_api_error("Connection error")
        except Exception as e:
            return self._handle_api_error(f"Unexpected error: {str(e)}")
    
    def _prepare_messages(self, conversation_history):
        """准备消息格式"""
        messages = []
        
        # 添加系统消息
        messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant for Anki flashcard learning. Help users understand and learn from their flashcard content."
        })
        
        # 处理对话历史
        for entry in conversation_history:
            if isinstance(entry, dict):
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if content.strip():
                    messages.append({
                        "role": role,
                        "content": content
                    })
            elif isinstance(entry, str):
                # 简单字符串作为用户消息
                messages.append({
                    "role": "user", 
                    "content": entry
                })
        
        return messages
    
    def test_connection(self):
        """测试API连接"""
        try:
            # 发送简单的测试请求
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": test_messages,
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Connection successful"
            elif response.status_code == 401:
                return False, "Invalid API key"
            elif response.status_code == 429:
                return False, "Rate limit exceeded"
            else:
                error_msg = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', '')}"
                except:
                    pass
                return False, error_msg
                
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to OpenAI API"
        except Exception as e:
            return False, f"Test failed: {str(e)}"
    
    def _handle_api_error(self, error_message):
        """处理API错误"""
        self.logger.error(f"AI Service Error: {error_message}")
        
        return {
            "success": False,
            "error": error_message,
            "response": f"AI服务暂时不可用: {error_message}"
        }
    
    def get_model_info(self):
        """获取模型信息"""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_available": self.api_key != "sk-placeholder-key-here"
        }

# 为了向后兼容，创建一个别名
OpenAIService = AIService

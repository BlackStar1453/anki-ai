# Anki AI Chat Tool - LiteLLM 迁移实现文档

## 实现策略
采用渐进式迁移策略，最小化代码修改，保持向后兼容性。

## 实现步骤

### 步骤 1：依赖管理和环境准备

#### 1.1 安装 LiteLLM
```bash
pip install litellm
```

#### 1.2 创建依赖文件
```python
# requirements.txt (新建)
litellm>=1.0.0
openai>=1.0.0  # 保持向后兼容
requests>=2.25.0
```

### 步骤 2：创建统一 AI 服务

#### 2.1 新建 `services/unified_ai_service.py`
```python
# 伪代码
import litellm
from typing import List, Dict, Any, Optional

class UnifiedAIService:
    def __init__(self):
        self.config = Config.get_ai_config()
        self.setup_litellm()
        self.setup_providers()
    
    def setup_litellm(self):
        # 配置 LiteLLM 全局设置
        litellm.set_verbose = self.config.get("debug_mode", False)
        litellm.drop_params = True  # 自动处理不支持的参数
        
        # 设置重试策略
        litellm.num_retries = self.config.get("retry_attempts", 3)
        litellm.request_timeout = self.config.get("timeout", 30)
    
    def setup_providers(self):
        # 设置环境变量
        import os
        if self.config.get("openai_api_key"):
            os.environ["OPENAI_API_KEY"] = self.config["openai_api_key"]
        if self.config.get("anthropic_api_key"):
            os.environ["ANTHROPIC_API_KEY"] = self.config["anthropic_api_key"]
    
    def get_response(self, conversation_history: List[Dict]) -> str:
        """获取 AI 回复 - 保持原有接口"""
        if not conversation_history:
            return self._handle_error("Empty conversation history")
        
        try:
            # 获取当前模型配置
            model = self._get_current_model()
            
            # 调用 LiteLLM
            response = litellm.completion(
                model=model,
                messages=conversation_history,
                max_tokens=self.config.get("max_tokens", 500),
                temperature=self.config.get("temperature", 0.7)
            )
            
            # 提取回复内容
            return self._extract_content(response)
            
        except Exception as e:
            return self._handle_error(str(e))
    
    def _get_current_model(self) -> str:
        """获取当前模型"""
        provider = self.config.get("ai_provider", "openai")
        model = self.config.get("openai_model", "gpt-3.5-turbo")
        
        if provider == "openai":
            return model
        elif provider == "anthropic":
            return "claude-3-sonnet-20240229"
        elif provider == "google":
            return "gemini-pro"
        else:
            return model  # 默认返回 OpenAI 模型
    
    def _extract_content(self, response) -> str:
        """提取响应内容"""
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and choice.message.content:
                return choice.message.content.strip()
        
        return self._handle_error("Empty response from API")
    
    def _handle_error(self, error_msg: str) -> str:
        """错误处理 - 保持原有格式"""
        return f"AI服务暂时不可用: {error_msg}"
    
    def validate_api_key(self) -> tuple[bool, str]:
        """验证 API 密钥"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            response = litellm.completion(
                model=self._get_current_model(),
                messages=test_messages,
                max_tokens=10
            )
            return True, "API key is valid"
        except Exception as e:
            return False, f"API key validation failed: {str(e)}"
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "ai_provider": self.config.get("ai_provider", "openai"),
            "model": self._get_current_model(),
            "api_key_set": bool(self._get_api_key()),
            "max_tokens": self.config.get("max_tokens", 500),
            "temperature": self.config.get("temperature", 0.7),
            "retry_attempts": self.config.get("retry_attempts", 3)
        }
    
    def _get_api_key(self) -> Optional[str]:
        """获取当前提供商的 API 密钥"""
        provider = self.config.get("ai_provider", "openai")
        if provider == "openai":
            return self.config.get("openai_api_key")
        elif provider == "anthropic":
            return self.config.get("anthropic_api_key")
        return None
```

### 步骤 3：扩展配置管理

#### 3.1 更新 `config.py`
```python
# 伪代码 - 在现有 Config 类中添加
class Config:
    DEFAULT_CONFIG = {
        # 保持现有配置
        "openai_api_key": "sk-placeholder-key-here",
        "openai_model": "gpt-3.5-turbo",
        "max_tokens": 500,
        "temperature": 0.7,
        
        # 新增统一 AI 配置
        "ai_provider": "openai",  # 主要提供商
        "fallback_providers": [],  # 回退提供商列表
        
        # 多提供商 API 密钥
        "anthropic_api_key": "",
        "google_api_key": "",
        
        # 增强配置
        "retry_attempts": 3,
        "timeout": 30,
        "enable_cost_tracking": False,
        
        # 保持现有配置
        "chat_window_width": 600,
        "chat_window_height": 400,
        "save_conversations": True,
        "conversation_separator": "<hr><h3>AI Chat History</h3>",
        "debug_mode": False
    }
    
    @classmethod
    def get_ai_config(cls):
        """获取 AI 相关配置"""
        config = cls.get_config()
        return {
            "ai_provider": config.get("ai_provider", "openai"),
            "openai_api_key": config.get("openai_api_key", "sk-placeholder-key-here"),
            "openai_model": config.get("openai_model", "gpt-3.5-turbo"),
            "anthropic_api_key": config.get("anthropic_api_key", ""),
            "google_api_key": config.get("google_api_key", ""),
            "max_tokens": config.get("max_tokens", 500),
            "temperature": config.get("temperature", 0.7),
            "retry_attempts": config.get("retry_attempts", 3),
            "timeout": config.get("timeout", 30),
            "debug_mode": config.get("debug_mode", False)
        }
    
    @classmethod
    def get_openai_config(cls):
        """保持向后兼容的 OpenAI 配置方法"""
        ai_config = cls.get_ai_config()
        return {
            "api_key": ai_config["openai_api_key"],
            "model": ai_config["openai_model"],
            "max_tokens": ai_config["max_tokens"],
            "temperature": ai_config["temperature"]
        }
```

### 步骤 4：创建适配器模式

#### 4.1 更新 `services/openai_service.py`
```python
# 伪代码 - 保持向后兼容
from .unified_ai_service import UnifiedAIService

class OpenAIService:
    """OpenAI 服务适配器 - 保持向后兼容"""
    
    def __init__(self):
        # 使用统一 AI 服务作为后端
        self.unified_service = UnifiedAIService()
        
        # 保持原有属性用于兼容性
        config = Config.get_openai_config()
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        self.max_tokens = config.get("max_tokens")
        self.temperature = config.get("temperature")
    
    def get_response(self, conversation_history):
        """委托给统一服务"""
        return self.unified_service.get_response(conversation_history)
    
    def validate_api_key(self):
        """委托给统一服务"""
        return self.unified_service.validate_api_key()
    
    def get_service_status(self):
        """适配统一服务状态到原有格式"""
        status = self.unified_service.get_service_status()
        return {
            "openai_available": True,  # LiteLLM 处理可用性
            "api_key_set": status["api_key_set"],
            "model": status["model"],
            "max_tokens": status["max_tokens"],
            "temperature": status["temperature"]
        }
    
    def update_config(self, new_config):
        """更新配置 - 保持兼容性"""
        if "api_key" in new_config:
            self.api_key = new_config["api_key"]
        if "model" in new_config:
            self.model = new_config["model"]
        if "max_tokens" in new_config:
            self.max_tokens = new_config["max_tokens"]
        if "temperature" in new_config:
            self.temperature = new_config["temperature"]
        
        # 同步到统一配置
        # 这里需要实现配置同步逻辑
```

### 步骤 5：测试脚本创建

#### 5.1 创建 `test_unified_ai_service.py`
```python
# 伪代码
#!/usr/bin/env python3
"""
统一 AI 服务测试脚本
"""

def test_litellm_installation():
    """测试 LiteLLM 安装"""
    try:
        import litellm
        print("✅ LiteLLM 安装成功")
        print(f"   版本: {litellm.__version__}")
        return True
    except ImportError as e:
        print(f"❌ LiteLLM 安装失败: {e}")
        return False

def test_unified_service():
    """测试统一 AI 服务"""
    try:
        from services.unified_ai_service import UnifiedAIService
        service = UnifiedAIService()
        print("✅ 统一 AI 服务创建成功")
        
        # 测试配置
        status = service.get_service_status()
        print(f"   提供商: {status['ai_provider']}")
        print(f"   模型: {status['model']}")
        
        return True
    except Exception as e:
        print(f"❌ 统一 AI 服务测试失败: {e}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    try:
        from services.openai_service import OpenAIService
        service = OpenAIService()
        print("✅ OpenAI 服务兼容性测试通过")
        return True
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        return False

def main():
    print("=" * 60)
    print("统一 AI 服务迁移测试")
    print("=" * 60)
    
    tests = [
        test_litellm_installation,
        test_unified_service,
        test_backward_compatibility
    ]
    
    results = []
    for test in tests:
        print(f"\n{test.__doc__}...")
        results.append(test())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 所有测试通过！迁移准备就绪")
    else:
        print("❌ 部分测试失败，请检查配置")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

## 实施时间线

### 第 1 天：环境准备
- 安装 LiteLLM
- 创建基础文件结构
- 运行初始测试

### 第 2 天：核心实现
- 实现 UnifiedAIService
- 更新配置管理
- 创建适配器

### 第 3 天：测试和验证
- 创建测试脚本
- 验证功能完整性
- 修复发现的问题

### 第 4 天：优化和文档
- 性能优化
- 更新文档
- 最终测试

## 回滚计划
如果迁移出现问题，可以通过以下方式回滚：
1. 保持原有 `openai_service.py` 不变
2. 在配置中添加 `use_legacy_service: true` 选项
3. 根据配置选择使用新旧服务

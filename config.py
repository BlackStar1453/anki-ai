# 配置管理模块

import json
import os

# 尝试导入Anki模块，如果失败则在测试环境中
try:
    from aqt import mw
    ANKI_AVAILABLE = True
except ImportError:
    mw = None
    ANKI_AVAILABLE = False

class Config:
    """配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # OpenAI 配置（不再硬编码默认密钥与模型）
        "openai_api_key": "",
        "openai_model": "",
        "max_tokens": 500,
        "temperature": 0.7,

        # 统一 AI 配置已禁用（仅保留 openai 直连）
        "ai_provider": "openai",

        # 增强配置
        "retry_attempts": 3,
        "timeout": 30,
        "enable_cost_tracking": False,
        "use_unified_service": False,  # 禁用统一服务

        # 保持现有 UI 配置
        "chat_window_width": 600,
        "chat_window_height": 400,
        "save_conversations": True,
        "conversation_separator": "<hr><h3>AI Chat History</h3>",
        "debug_mode": False
    }
    
    _config = None
    
    @classmethod
    def load_config(cls):
        """加载配置"""
        try:
            # 尝试从Anki配置中加载（仅在Anki环境中）
            if ANKI_AVAILABLE and mw and hasattr(mw, 'addonManager'):
                # 更稳妥：根据文件系统路径获取插件目录名（安装后为数字ID）
                addon_root = os.path.dirname(__file__)
                addon_id = os.path.basename(addon_root)
                addon_config = mw.addonManager.getConfig(addon_id)
                if addon_config:
                    cls._config = {**cls.DEFAULT_CONFIG, **addon_config}
                    return cls._config
        except Exception as e:
            print(f"Failed to load config from Anki: {e}")

        # 使用默认配置
        cls._config = cls.DEFAULT_CONFIG.copy()
        return cls._config
    
    @classmethod
    def get_config(cls):
        """获取配置"""
        if cls._config is None:
            cls.load_config()
        return cls._config
    
    @classmethod
    def get(cls, key, default=None):
        """获取配置项"""
        config = cls.get_config()
        return config.get(key, default)
    
    @classmethod
    def set(cls, key, value):
        """设置配置项"""
        if cls._config is None:
            cls.load_config()
        cls._config[key] = value
    
    @classmethod
    def save_config(cls):
        """保存配置"""
        try:
            if ANKI_AVAILABLE and mw and hasattr(mw, 'addonManager') and cls._config:
                # 更稳妥：根据文件系统路径获取插件目录名（安装后为数字ID）
                addon_root = os.path.dirname(__file__)
                addon_id = os.path.basename(addon_root)
                mw.addonManager.writeConfig(addon_id, cls._config)
                return True

        except Exception as e:
            print(f"Failed to save config: {e}")
        return False
    
    @classmethod
    def get_openai_config(cls):
        """获取OpenAI相关配置"""
        config = cls.get_config()
        return {
            "api_key": config.get("openai_api_key", ""),
            "model": config.get("openai_model", ""),
            "max_tokens": config.get("max_tokens", 500),
            "temperature": config.get("temperature", 0.7)
        }
    
    @classmethod
    def get_ui_config(cls):
        """获取UI相关配置"""
        config = cls.get_config()
        return {
            "window_width": config.get("chat_window_width", 600),
            "window_height": config.get("chat_window_height", 400),
            "conversation_separator": config.get("conversation_separator", "<hr><h3>AI Chat History</h3>")
        }
    
    @classmethod
    def is_debug_mode(cls):
        """是否为调试模式"""
        return cls.get("debug_mode", False)
    
    @classmethod
    def should_save_conversations(cls):
        """是否应该保存对话"""
        return cls.get("save_conversations", True)

    @classmethod
    def get_ai_config(cls):
        """获取统一 AI 相关配置"""
        config = cls.get_config()
        return {
            # 主要配置
            "ai_provider": config.get("ai_provider", "openai"),
            "fallback_providers": config.get("fallback_providers", []),

            # API 密钥（仅保留 openai）
            "openai_api_key": config.get("openai_api_key", ""),

            # 模型配置
            "openai_model": config.get("openai_model", ""),
            "max_tokens": config.get("max_tokens", 500),
            "temperature": config.get("temperature", 0.7),

            # 增强配置
            "retry_attempts": config.get("retry_attempts", 3),
            "timeout": config.get("timeout", 30),
            "enable_cost_tracking": config.get("enable_cost_tracking", False),
            "debug_mode": config.get("debug_mode", False),

            # 服务选择
            "use_unified_service": False
        }

    @classmethod
    def should_use_unified_service(cls):
        """是否应该使用统一服务"""
        return cls.get("use_unified_service", True)

    @classmethod
    def get_provider_config(cls, provider: str):
        """获取特定提供商的配置"""
        config = cls.get_config()

        if provider == "openai":
            return {
                "api_key": config.get("openai_api_key", "sk-placeholder-key-here"),
                "model": config.get("openai_model", "gpt-3.5-turbo")
            }
        elif provider == "anthropic":
            return {
                "api_key": config.get("anthropic_api_key", ""),
                "model": "claude-3-sonnet-20240229"
            }
        elif provider == "google":
            return {
                "api_key": config.get("google_api_key", ""),
                "model": "gemini-pro"
            }
        else:
            return {}

    @classmethod
    def set_provider(cls, provider: str):
        """设置当前 AI 提供商"""
        if provider in ["openai", "anthropic", "google"]:
            cls.set("ai_provider", provider)
            return True
        return False

    @classmethod
    def add_fallback_provider(cls, provider: str):
        """添加回退提供商"""
        if provider in ["openai", "anthropic", "google"]:
            fallback_providers = cls.get("fallback_providers", [])
            if provider not in fallback_providers:
                fallback_providers.append(provider)
                cls.set("fallback_providers", fallback_providers)
                return True
        return False

    @classmethod
    def remove_fallback_provider(cls, provider: str):
        """移除回退提供商"""
        fallback_providers = cls.get("fallback_providers", [])
        if provider in fallback_providers:
            fallback_providers.remove(provider)
            cls.set("fallback_providers", fallback_providers)
            return True
        return False

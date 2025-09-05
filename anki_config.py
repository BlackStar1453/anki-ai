"""
简化的配置管理器
专门为 Anki 插件环境设计
"""

import json
import os

class AnkiConfigManager:
    """Anki 插件配置管理器"""
    
    def __init__(self):
        self.addon_dir = os.path.dirname(__file__)
        self.config_file = os.path.join(self.addon_dir, "config.json")
        self._config = None
    
    def load_config(self):
        """加载配置"""
        try:
            # 首先尝试从 Anki 配置管理器加载
            try:
                from aqt import mw
                if mw and hasattr(mw, 'addonManager'):
                    # 获取插件包名
                    addon_name = os.path.basename(self.addon_dir)
                    config = mw.addonManager.getConfig(addon_name)
                    if config:
                        self._config = config
                        return config
            except:
                pass
            
            # 回退到本地文件
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                    return self._config
            
            # 使用默认配置
            self._config = self.get_default_config()
            return self._config
            
        except Exception as e:
            print(f"Config load error: {e}")
            self._config = self.get_default_config()
            return self._config
    
    def save_config(self, config=None):
        """保存配置"""
        if config:
            self._config = config
        
        try:
            # 尝试保存到 Anki 配置管理器
            try:
                from aqt import mw
                if mw and hasattr(mw, 'addonManager'):
                    addon_name = os.path.basename(self.addon_dir)
                    mw.addonManager.writeConfig(addon_name, self._config)
                    return True
            except:
                pass
            
            # 回退到本地文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            return True
            
        except Exception as e:
            print(f"Config save error: {e}")
            return False
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "ai_provider": "openai",
            "openai_api_key": "your-openai-api-key-here",
            "use_unified_service": True,
            "max_tokens": 500,
            "temperature": 0.7
        }
    
    def get(self, key, default=None):
        """获取配置项"""
        if self._config is None:
            self.load_config()
        return self._config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        if self._config is None:
            self.load_config()
        self._config[key] = value

# 全局配置管理器实例
config_manager = AnkiConfigManager()

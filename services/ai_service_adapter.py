# AI 服务适配器 - 保持向后兼容性

import logging
from typing import Dict, Any, Tuple

# 尝试相对导入，如果失败则使用绝对导入
try:
    from ..config import Config
    from .openai_service import OpenAIService
except ImportError:
    from config import Config
    from services.openai_service import OpenAIService

class AIServiceAdapter:
    """AI 服务适配器 - 根据配置选择使用统一服务或原有 OpenAI 服务"""
    
    def __init__(self):
        """初始化适配器"""
        self.logger = logging.getLogger(__name__)
        self._service = None
        self._service_type = None
        self._initialize_service()
    
    def _initialize_service(self):
        """初始化服务实例"""
        try:
            # 统一服务已禁用：直接使用 OpenAIService（requests 直连）
            self._service = OpenAIService()
            self._service_type = "openai"
            self.logger.info("Using OpenAIService (requests direct)")
        except Exception as e:
            # 如果统一服务初始化失败，回退到 OpenAI 服务
            self.logger.warning(f"Failed to initialize preferred service: {e}")
            self.logger.info("Falling back to OpenAIService")
            try:
                self._service = OpenAIService()
                self._service_type = "openai"
            except Exception as fallback_error:
                self.logger.error(f"Failed to initialize fallback service: {fallback_error}")
                self._service = None
                self._service_type = None
    
    def get_response(self, conversation_history):
        """获取 AI 回复 - 统一接口"""
        if not self._service:
            return "AI服务暂时不可用: 服务未初始化"
        
        try:
            if self._service_type == "unified":
                # 使用统一服务，支持回退机制
                return self._service.get_response_with_fallback(conversation_history)
            else:
                # 使用原有 OpenAI 服务
                return self._service.get_response(conversation_history)
        except Exception as e:
            self.logger.error(f"Error in get_response: {e}")
            return f"AI服务暂时不可用: {str(e)}"
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """验证 API 密钥 - 统一接口"""
        if not self._service:
            return False, "服务未初始化"
        
        try:
            return self._service.validate_api_key()
        except Exception as e:
            self.logger.error(f"Error in validate_api_key: {e}")
            return False, f"验证失败: {str(e)}"
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态 - 统一接口"""
        if not self._service:
            return {
                "service_available": False,
                "service_type": None,
                "error": "服务未初始化"
            }
        
        try:
            status = self._service.get_service_status()
            
            # 添加适配器特有的状态信息
            status.update({
                "service_type": self._service_type,
                "adapter_version": "1.0.0",
                "service_available": True
            })
            
            # 为了向后兼容，确保包含 OpenAI 格式的状态
            if self._service_type == "unified":
                # 将统一服务状态转换为 OpenAI 格式
                status["openai_available"] = status.get("litellm_available", False)
                if "ai_provider" in status:
                    current_provider = status["ai_provider"]
                    status["api_key_set"] = current_provider in status.get("available_providers", [])
            
            return status
        except Exception as e:
            self.logger.error(f"Error in get_service_status: {e}")
            return {
                "service_available": False,
                "service_type": self._service_type,
                "error": str(e)
            }
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新配置 - 统一接口"""
        if not self._service:
            self.logger.error("Cannot update config: service not initialized")
            return
        
        try:
            # 更新服务配置
            self._service.update_config(new_config)
            
            # 如果配置中包含服务类型切换，重新初始化
            if "use_unified_service" in new_config:
                old_type = self._service_type
                self._initialize_service()
                if self._service_type != old_type:
                    self.logger.info(f"Service switched from {old_type} to {self._service_type}")
            
        except Exception as e:
            self.logger.error(f"Error in update_config: {e}")
    
    def switch_provider(self, provider: str) -> Tuple[bool, str]:
        """切换 AI 提供商（仅统一服务支持）"""
        if self._service_type != "unified":
            return False, "Provider switching only supported in unified service mode"
        
        if not self._service:
            return False, "服务未初始化"
        
        try:
            # 检查提供商是否有效
            if provider not in ["openai", "anthropic", "google"]:
                return False, f"Unsupported provider: {provider}"
            
            # 更新配置
            Config.set_provider(provider)
            
            # 更新服务配置
            self._service.update_config({"ai_provider": provider})
            
            return True, f"Successfully switched to {provider}"
        except Exception as e:
            self.logger.error(f"Error switching provider: {e}")
            return False, str(e)
    
    def add_fallback_provider(self, provider: str) -> Tuple[bool, str]:
        """添加回退提供商（仅统一服务支持）"""
        if self._service_type != "unified":
            return False, "Fallback providers only supported in unified service mode"
        
        try:
            success = Config.add_fallback_provider(provider)
            if success:
                # 更新服务配置
                fallback_providers = Config.get("fallback_providers", [])
                self._service.update_config({"fallback_providers": fallback_providers})
                return True, f"Added {provider} as fallback provider"
            else:
                return False, f"Failed to add {provider} as fallback provider"
        except Exception as e:
            self.logger.error(f"Error adding fallback provider: {e}")
            return False, str(e)
    
    def get_available_providers(self) -> list:
        """获取可用的提供商列表"""
        if self._service_type == "unified" and self._service:
            try:
                status = self._service.get_service_status()
                return status.get("available_providers", [])
            except Exception as e:
                self.logger.error(f"Error getting available providers: {e}")
                return []
        else:
            # 对于 OpenAI 服务，只返回 OpenAI
            return ["openai"] if self._service else []
    
    def get_current_provider(self) -> str:
        """获取当前提供商"""
        if self._service_type == "unified":
            return Config.get("ai_provider", "openai")
        else:
            return "openai"
    
    def is_unified_service(self) -> bool:
        """是否使用统一服务"""
        return self._service_type == "unified"
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            "service_type": self._service_type,
            "is_unified": self.is_unified_service(),
            "current_provider": self.get_current_provider(),
            "available_providers": self.get_available_providers(),
            "supports_provider_switching": self._service_type == "unified",
            "supports_fallback": self._service_type == "unified"
        }

# Services 包初始化
"""
AI 服务包
包含统一 AI 服务、适配器和相关工具
"""

# 导入主要类以便直接访问
try:
    from services.ai_service_adapter import AIServiceAdapter
    from services.card_service import CardService

    __all__ = ['AIServiceAdapter', 'CardService']

except ImportError as e:
    print(f"Services package import warning: {e}")
    __all__ = []

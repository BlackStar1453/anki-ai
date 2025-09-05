# UI 包初始化
"""
用户界面包
包含聊天对话框、配置对话框和相关 UI 组件
"""

# 导入主要类以便直接访问
try:
    from ui.chat_dialog import ChatDialog
    from ui.config_dialog import ConfigDialog
    from ui.button_injector import ButtonInjector

    __all__ = ['ChatDialog', 'ConfigDialog', 'ButtonInjector']

except ImportError as e:
    print(f"UI package import warning: {e}")
    __all__ = []

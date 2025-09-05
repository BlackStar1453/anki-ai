# Chat with Card v2.0
# 插件入口点 - 支持多语言

# 设置依赖路径
import sys
import os

# 添加插件目录到 Python 路径
addon_dir = os.path.dirname(__file__)
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

# 添加 vendor 目录到 Python 路径（用于打包的第三方库，如 mistune、requests 等）
vendor_dir = os.path.join(addon_dir, 'vendor')
if os.path.isdir(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)
    print(f"Added vendor directory to path: {vendor_dir}")

from aqt import mw, gui_hooks
from aqt.utils import showInfo
from aqt.qt import QAction
from config import Config

def initialize_addon():
    """插件初始化入口"""
    try:
        # 初始化配置
        Config.load_config()

        # 自检：依赖、配置与服务
        errors = []
        warnings = []

        import traceback as _tb

        # 1) 依赖检查（检查 mistune 和 requests）
        try:
            import mistune  # noqa: F401
            print("✅ Mistune loaded successfully")
        except Exception:
            errors.append("mistune 库不可用（用于 markdown 处理）: " + _tb.format_exc())

        try:
            import requests  # noqa: F401
            print("✅ Requests loaded successfully")
        except Exception:
            errors.append("requests 库不可用（用于直连 OpenAI）: " + _tb.format_exc())

        # 2) 配置读写检查
        try:
            if mw and hasattr(mw, 'addonManager'):
                # 通过路径获取 addon_id（安装后为数字ID或本地目录名）
                addon_root = os.path.dirname(__file__)
                addon_id = os.path.basename(addon_root)
                # 读
                _cfg = mw.addonManager.getConfig(addon_id)
                if _cfg is None:
                    warnings.append("未检测到持久化配置，将使用默认配置。可在配置界面保存以创建。")
                else:
                    # 写回（不改变内容）
                    mw.addonManager.writeConfig(addon_id, _cfg)
            else:
                warnings.append("未在 Anki 运行环境下，跳过配置持久化检查。")
        except Exception as e:
            errors.append("配置持久化失败: " + _tb.format_exc())

        # 3) 初始化多语言支持
        try:
            try:
                from .i18n.translator import init_translator, set_language
            except ImportError:
                from i18n.translator import init_translator, set_language

            init_translator(addon_dir)

            # 从配置中加载语言设置
            if mw and hasattr(mw, 'addonManager'):
                try:
                    addon_root = os.path.dirname(__file__)
                    addon_id = os.path.basename(addon_root)
                    config = mw.addonManager.getConfig(addon_id) or {}
                    saved_language = config.get('language', 'en')
                    set_language(saved_language)
                    print(f"✅ Language set to: {saved_language}")
                except Exception as e:
                    print(f"Warning: Could not load language from config: {e}")

            print("✅ Internationalization initialized")
        except Exception:
            errors.append("多语言初始化失败: " + _tb.format_exc())

        # 4) 服务初始化检查（仅直连路径）
        try:
            from services.ai_service_adapter import AIServiceAdapter
            adapter = AIServiceAdapter()
            status = adapter.get_service_status()
            if not status.get("service_available", False):
                warnings.append(f"服务不可用: {status.get('error')}")
        except Exception:
            errors.append("服务初始化失败: " + _tb.format_exc())

        # 提示信息（包含完整堆栈）
        if errors:
            showInfo("Anki AI Chat Tool 启动自检发现问题:\n\n- " + "\n- ".join(errors) + ("\n\n提示:\n- " + "\n- ".join(warnings) if warnings else ""))
        elif warnings:
            showInfo("Anki AI Chat Tool 启动自检提示:\n\n- " + "\n- ".join(warnings))

        # 注册钩子来注入按钮到卡片显示
        gui_hooks.card_will_show.append(inject_ask_ai_button)

        # 注册命令处理器
        gui_hooks.webview_did_receive_js_message.append(handle_js_message)

        # 添加配置菜单
        setup_menu()


    except Exception as e:
        showInfo(f"Failed to initialize Anki AI Chat Tool: {str(e)}")

def inject_ask_ai_button(html, card, context):
    """在卡片HTML中注入Ask AI按钮"""
    try:
        # 只在答案显示时添加按钮
        if context != "reviewAnswer":
            return html

        # 导入翻译函数
        try:
            from .i18n.translator import _
        except ImportError:
            try:
                from i18n.translator import _
            except ImportError:
                def _(text): return text

        # 创建按钮HTML
        button_html = f"""
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="pycmd('ask_ai')"
                    style="background: #0078d4;
                           color: white;
                           padding: 10px 20px;
                           border: none;
                           border-radius: 5px;
                           cursor: pointer;
                           font-size: 14px;
                           font-weight: bold;">
                {_("Chat with Card")}
            </button>
        </div>
        """

        return html + button_html

    except Exception as e:
        showInfo(f"Error injecting button: {str(e)}")
        return html

def handle_js_message(handled, message, context):
    """处理来自WebView的JavaScript消息"""
    if message == "ask_ai":
        try:
            from ui.chat_dialog import ChatDialog
            from services.card_service import CardService

            # 获取当前卡片内容
            card_content = CardService.get_current_card_content()

            if card_content:
                # 打开聊天窗口
                dialog = ChatDialog(card_content)
                # PyQt6兼容性：使用exec()而不是exec_()
                if hasattr(dialog, 'exec'):
                    dialog.exec()
                else:
                    dialog.exec_()
            else:
                showInfo("No card content available")

            return (True, None)
        except Exception as e:
            showInfo(f"Error opening chat dialog: {str(e)}")
            return (True, None)

    return handled

def setup_menu():
    """设置菜单"""
    try:
        # 注册配置回调（Anki 标准方式）
        mw.addonManager.setConfigAction(__name__, open_config_dialog)

        # 导入翻译函数
        try:
            from .i18n.translator import _
        except ImportError:
            try:
                from i18n.translator import _
            except ImportError:
                def _(text): return text

        # 可选：也添加到工具菜单
        config_action = QAction(_("Chat with Card") + " - " + _("Settings"), mw)
        config_action.triggered.connect(open_config_dialog)
        mw.form.menuTools.addAction(config_action)

    except Exception as e:
        showInfo(f"Error setting up menu: {str(e)}")

def open_config_dialog():
    """打开配置对话框"""
    try:
        from ui.config_dialog import ConfigDialog

        dialog = ConfigDialog(mw)
        # PyQt6兼容性：使用exec()而不是exec_()
        if hasattr(dialog, 'exec'):
            dialog.exec()
        else:
            dialog.exec_()

    except Exception as e:
        showInfo(f"Error opening config dialog: {str(e)}")

# 初始化插件
initialize_addon()

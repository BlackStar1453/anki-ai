# 聊天窗口 - AI对话界面

import logging
import threading
import queue
import re
# 尝试相对导入，如果失败则使用绝对导入
try:
    from ..i18n.translator import _
except ImportError:
    try:
        from i18n.translator import _
    except ImportError:
        # 如果翻译模块不可用，提供回退函数
        def _(text): return text

# 尝试相对导入，如果失败则使用绝对导入
try:
    from ..config import Config
except ImportError:
    from config import Config

# 使用Anki的Qt导入（推荐方式）
try:
    from aqt.qt import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                       QTextEdit, QLineEdit, QPushButton,
                       QLabel, QMessageBox, Qt, QTextCursor, QApplication, QTimer)
    QT_AVAILABLE = True
except ImportError:
    # 为测试环境提供Mock类
    class MockQtBase:
        def __init__(self, *args, **kwargs):
            pass
        def setStyleSheet(self, *args, **kwargs):
            pass
        def setWindowTitle(self, *args, **kwargs):
            pass
        def setFixedSize(self, *args, **kwargs):
            pass
        def setLayout(self, *args, **kwargs):
            pass
        def addWidget(self, *args, **kwargs):
            pass
        def addLayout(self, *args, **kwargs):
            pass
        def setText(self, *args, **kwargs):
            pass
        def setPlaceholderText(self, *args, **kwargs):
            pass
        def setReadOnly(self, *args, **kwargs):
            pass
        def clicked(self):
            return MockSignal()
        def returnPressed(self):
            return MockSignal()
        def exec_(self):
            pass
        def exec(self):
            pass
        def close(self):
            pass

    class MockSignal:
        def connect(self, *args, **kwargs):
            pass

    class QDialog(MockQtBase):
        pass

    class QWidget(MockQtBase):
        pass

    class QVBoxLayout(MockQtBase):
        def setSpacing(self, *args, **kwargs):
            pass
        def setContentsMargins(self, *args, **kwargs):
            pass

    class QHBoxLayout(MockQtBase):
        def setSpacing(self, *args, **kwargs):
            pass
        def setContentsMargins(self, *args, **kwargs):
            pass

    class QTextEdit(MockQtBase):
        pass

    class QLineEdit(MockQtBase):
        pass

    class QPushButton(MockQtBase):
        pass

    class QLabel(MockQtBase):
        pass

    class QMessageBox(MockQtBase):
        pass

    class QTimer(MockQtBase):
        pass

    class QApplication:
        @staticmethod
        def processEvents():
            pass

    class Qt:
        pass

    class QTextCursor:
        End = 0
        MoveAnchor = 0
        KeepAnchor = 1

        class MoveOperation:
            End = 0

        class MoveMode:
            MoveAnchor = 0
            KeepAnchor = 1

    QT_AVAILABLE = False

# 导入服务 - Anki 插件兼容
import sys
import os

# 添加插件目录到路径
addon_dir = os.path.dirname(os.path.dirname(__file__))
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

try:
    from services.ai_service_adapter import AIServiceAdapter
    from services.card_service import CardService
except ImportError as e:
    print(f"Import error in chat_dialog: {e}")
    # 创建占位符类
    class AIServiceAdapter:
        def get_response(self, conversation):
            return "AI服务导入失败，请检查插件安装"

    class CardService:
        @staticmethod
        def format_conversation_for_card(conversation):
            return "对话格式化失败"
        @staticmethod
        def get_conversation_separator():
            return "<hr>"

def _qt_cursor_consts():
    """兼容 PyQt5 / PyQt6 的 QTextCursor 常量获取"""
    try:
        END = QTextCursor.End
    except Exception:
        try:
            END = QTextCursor.MoveOperation.End
        except Exception:
            END = 0
    try:
        MOVE_ANCHOR = QTextCursor.MoveAnchor
    except Exception:
        try:
            MOVE_ANCHOR = QTextCursor.MoveMode.MoveAnchor
        except Exception:
            MOVE_ANCHOR = 0
    try:
        KEEP_ANCHOR = QTextCursor.KeepAnchor
    except Exception:
        try:
            KEEP_ANCHOR = QTextCursor.MoveMode.KeepAnchor
        except Exception:
            KEEP_ANCHOR = 1
    return END, MOVE_ANCHOR, KEEP_ANCHOR

class ChatDialog(QDialog):
    """AI聊天窗口"""

    def __init__(self, card_content, parent=None):
        """初始化聊天窗口"""
        super().__init__(parent)

        self.card_content = card_content
        self.conversation_history = []
        self.saved_message_count = 0  # 跟踪已保存的消息数量
        self.ai_service = AIServiceAdapter()
        self.logger = logging.getLogger(__name__ + ".ChatDialog")

        # 流式/线程相关状态
        self._stream_thread = None
        self._stream_queue = None
        self._stream_timer = None
        self._stream_active = False
        self._stream_accum = []
        self._stream_start_pos = None
        self._stream_end_pos = None

        # 初始化AI上下文
        self.initialize_ai_context()

        # 设置UI（如果Qt可用）
        if QT_AVAILABLE:
            self.setup_ui()

    def initialize_ai_context(self):
        """初始化AI上下文"""
        if not self.card_content:
            return

        # 创建系统消息，包含卡片内容
        context_message = f"""Current Anki Card:
Front: {self.card_content.get('front', '')}
Back: {self.card_content.get('back', '')}

Please help me understand this card better. You can explain concepts, provide examples, answer questions, or help with memorization techniques."""

        self.conversation_history = [
            {"role": "system", "content": context_message}
        ]

    def setup_ui(self):
        """设置用户界面"""
        if not QT_AVAILABLE:
            return

        # 获取UI配置
        ui_config = Config.get_ui_config()

        # 设置窗口属性 - 现代极简风格
        self.setWindowTitle(_("Chat with AI"))

        # 更新界面语言
        self.update_ui_language()
        self.setFixedSize(ui_config["window_width"], ui_config["window_height"])

        # 设置窗口整体样式
        self.setStyleSheet("""
            QDialog {
                background-color: #fefefe;
                border: 1px solid #e5e7eb;
            }
        """)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)  # 移除默认间距
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除默认边距

        # 聊天显示区域 - 现代极简风格
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: none;
                padding: 20px;
                font-size: 14px;
                selection-background-color: #e5e7eb;
            }
        """)
        main_layout.addWidget(self.chat_display)

        # 预先创建输入与按钮，避免调用 setup_ui 前缺失属性（便于测试环境）
        if not hasattr(self, 'input_field'):
            self.input_field = QLineEdit()
        if not hasattr(self, 'send_button'):
            self.send_button = QPushButton(_("Send"))


        # 输入区域 - 现代极简风格
        input_widget = QWidget()
        input_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #e5e7eb;
                padding: 20px;
            }
        """)
        input_layout = QHBoxLayout(input_widget)
        input_layout.setSpacing(12)
        input_layout.setContentsMargins(20, 20, 20, 20)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(_("Type your message..."))
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 1px solid #d1d5db;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #111827;
                background-color: white;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton(_("Send"))
        self.send_button.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                background-color: #111827;
                color: white;
                border: none;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #374151;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addWidget(input_widget)

        # 控制按钮区域 - 现代极简风格
        button_widget = QWidget()
        button_widget.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border-top: 1px solid #e5e7eb;
                padding: 16px 20px;
            }
        """)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(20, 16, 20, 16)

        # 统一的按钮样式
        button_style = """
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #d1d5db;
                background-color: white;
                font-size: 14px;
                color: #374151;
            }
            QPushButton:hover {
                background-color: #f9fafb;
            }
        """

        self.save_button = QPushButton(_("Save"))
        self.save_button.setStyleSheet(button_style)
        self.save_button.clicked.connect(self.save_to_card)
        button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton(_("Clear Chat"))
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)

        self.close_button = QPushButton(_("Close"))
        self.close_button.setStyleSheet(button_style)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        main_layout.addWidget(button_widget)

        # 设置主布局
        self.setLayout(main_layout)



    def send_message(self):
        """发送用户消息（线程化+主线程增量刷新）"""
        if not hasattr(self, 'input_field'):
            return

        user_message = self.input_field.text().strip()
        if not user_message:
            self.show_message(_("Please enter a message"), _("Warning"))
            return

        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # 显示用户消息
        self.display_message("User", user_message)

        # 清空输入框
        self.input_field.clear()

        # 禁用发送按钮，显示加载状态
        if hasattr(self, 'send_button'):
            self.send_button.setEnabled(False)
            self.send_button.setText("Thinking...")

        # 准备 UI 中的占位元素，并记录可原位更新的光标范围
        END, MOVE_ANCHOR, KEEP_ANCHOR = _qt_cursor_consts()
        if hasattr(self, 'chat_display'):
            self.chat_display.moveCursor(END)
            # 先追加一个空段落，确保占位块独立于上一条用户消息
            try:
                self.chat_display.append("")
            except Exception:
                # 兜底：若 append 不可用，插入一个段落 div
                self.chat_display.insertHtml("<div></div>")
            self.chat_display.moveCursor(END)
            self._stream_start_pos = self.chat_display.textCursor().position()
            # 插入loading状态，不显示空白消息框
            self.chat_display.insertHtml('<div style="margin:12px 0;padding:8px 16px;color:#6b7280;font-size:14px;max-width:75%;margin-right:auto;line-height:1.5;font-style:italic;">'
                                         'AI is thinking...'
                                         '</div>')
            self.chat_display.moveCursor(END)
            self._stream_end_pos = self.chat_display.textCursor().position()

        # 初始化流式状态
        self._stream_queue = queue.Queue()
        self._stream_active = True
        self._stream_accum = []

        def worker():
            final_text = None
            try:
                base_service = getattr(self.ai_service, '_service', None)
                stream = getattr(base_service, 'stream_response', None)
                if callable(stream):
                    for chunk in stream(self.conversation_history):
                        # 将分片推入队列供主线程消费
                        self._stream_queue.put(('chunk', chunk))
                    final_text = ''.join(self._stream_accum) if self._stream_accum else None
                else:
                    # 同步一次性请求
                    final_text = self.ai_service.get_response(self.conversation_history)
            except Exception as e:
                self._stream_queue.put(('error', str(e)))
            finally:
                self._stream_queue.put(('done', final_text))

        # 启动后台线程
        self._stream_thread = threading.Thread(target=worker, daemon=True)
        self._stream_thread.start()

        # 使用 QTimer 在主线程轮询队列，安全更新 UI
        if QT_AVAILABLE:
            if self._stream_timer is None:
                self._stream_timer = QTimer(self)
                self._stream_timer.setInterval(30)  # 约33FPS
                self._stream_timer.timeout.connect(self._on_stream_timer)
            self._stream_timer.start()

    def _on_stream_timer(self):
        """主线程定时器：消费分片、原位更新 Dom、处理完成/错误"""
        try:
            # 防御：队列/状态可能已被清理
            if self._stream_queue is None:
                self._finalize_stream()
                return

            processed_any = False
            while (self._stream_queue is not None) and (not self._stream_queue.empty()):
                processed_any = True
                kind, payload = self._stream_queue.get_nowait()
                if kind == 'chunk':
                    self._stream_accum.append(payload)
                    text = ''.join(self._stream_accum)
                    if hasattr(self, 'chat_display') and self._stream_start_pos is not None and self._stream_end_pos is not None:
                        END, MOVE_ANCHOR, KEEP_ANCHOR = _qt_cursor_consts()
                        cursor = self.chat_display.textCursor()
                        cursor.setPosition(self._stream_start_pos, MOVE_ANCHOR)
                        cursor.setPosition(self._stream_end_pos, KEEP_ANCHOR)
                        # 替换loading状态为实际消息内容（处理markdown）
                        processed_text = self._process_ai_message(text)
                        cursor.insertHtml(f'<div style="margin:12px 0;padding:12px 16px;border:1px solid #e5e7eb;color:#111827;font-size:14px;max-width:75%;margin-right:auto;line-height:1.5;">{processed_text}</div>')
                        self._stream_end_pos = cursor.position()
                        try:
                            QApplication.processEvents()
                        except Exception:
                            pass
                elif kind == 'error':
                    # 替换loading状态为错误消息
                    if hasattr(self, 'chat_display') and self._stream_start_pos is not None and self._stream_end_pos is not None:
                        END, MOVE_ANCHOR, KEEP_ANCHOR = _qt_cursor_consts()
                        cursor = self.chat_display.textCursor()
                        cursor.setPosition(self._stream_start_pos, MOVE_ANCHOR)
                        cursor.setPosition(self._stream_end_pos, KEEP_ANCHOR)
                        cursor.insertHtml(f'<div style="margin:12px 0;padding:12px 16px;background-color:#fef2f2;border:1px solid #fca5a5;color:#dc2626;font-size:14px;max-width:75%;margin-right:auto;line-height:1.5;">Error: {payload}</div>')
                        self._stream_end_pos = cursor.position()
                    else:
                        self.display_message("System", f"AI 流式错误: {payload}")
                elif kind == 'done':
                    final_text = payload
                    # 如果没有通过 chunk 路径累积，则 final_text 可能来自一次性请求
                    if final_text and not self._stream_accum:
                        if hasattr(self, 'chat_display') and self._stream_start_pos is not None and self._stream_end_pos is not None:
                            END, MOVE_ANCHOR, KEEP_ANCHOR = _qt_cursor_consts()
                            cursor = self.chat_display.textCursor()
                            cursor.setPosition(self._stream_start_pos, MOVE_ANCHOR)
                            cursor.setPosition(self._stream_end_pos, KEEP_ANCHOR)
                            # 替换loading状态为最终消息内容（处理markdown）
                            processed_final_text = self._process_ai_message(final_text)
                            cursor.insertHtml(f'<div style="margin:12px 0;padding:12px 16px;border:1px solid #e5e7eb;color:#111827;font-size:14px;max-width:75%;margin-right:auto;line-height:1.5;">{processed_final_text}</div>')
                            self._stream_end_pos = cursor.position()
                    # 写入会话历史
                    full = ''.join(self._stream_accum) if self._stream_accum else (final_text or '')
                    if full:
                        self.conversation_history.append({"role": "assistant", "content": full})
                    # 收尾
                    self._finalize_stream()
            # 若暂无事件，也保持 UI 活跃
            if processed_any:
                try:
                    QApplication.processEvents()
                except Exception:
                    pass
        except Exception as e:
            self.display_message("System", f"UI 更新异常: {e}")
            self._finalize_stream()

    def _finalize_stream(self):
        """结束流式：停止计时器、恢复按钮、清理状态"""
        if self._stream_timer:
            try:
                self._stream_timer.stop()
            except Exception:
                pass
        self._stream_active = False
        self._stream_thread = None
        self._stream_queue = None
        self._stream_start_pos = None
        self._stream_end_pos = None
        self._stream_accum = []
        if hasattr(self, 'send_button'):
            self.send_button.setEnabled(True)
            self.send_button.setText("Send")

    def display_message(self, sender, message):
        """显示消息 - 现代极简风格，AI消息支持markdown"""
        if not hasattr(self, 'chat_display'):
            return

        # 格式化消息 - Qt兼容的现代极简风格，使用Q&A格式
        if sender == "User":
            # 用户消息：右对齐，无背景色，有边框，黑色字体
            formatted_msg = f'''
            <div style="margin: 12px 0; padding: 12px 16px; border: 1px solid #e5e7eb; color: #111827; font-size: 14px; max-width: 75%; margin-left: auto; line-height: 1.5;">
            {self._escape_html(message)}
            </div>
            '''
        elif sender == "AI":
            # AI消息：左对齐，无背景色，有边框，黑色字体，支持markdown
            processed_message = self._process_ai_message(message)
            formatted_msg = f'''
            <div style="margin: 12px 0; padding: 12px 16px; border: 1px solid #e5e7eb; color: #111827; font-size: 14px; max-width: 75%; margin-right: auto; line-height: 1.5;">
            {processed_message}
            </div>
            '''
        else:  # System
            # 系统消息：居中，灰色背景
            formatted_msg = f'''
            <div style="margin: 12px 0; padding: 12px 16px; background-color: #f9fafb; border: 1px solid #e5e7eb; font-size: 14px; font-style: italic; text-align: center;">
            <strong>System:</strong> {self._escape_html(message)}
            </div>
            '''

        self.chat_display.append(formatted_msg)

        # 滚动到底部
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_ui_language(self):
        """更新界面语言"""
        if not QT_AVAILABLE:
            return

        try:
            # 更新窗口标题
            self.setWindowTitle(_("Chat with AI"))

            # 更新按钮文本
            if hasattr(self, 'send_button'):
                self.send_button.setText(_("Send"))

            if hasattr(self, 'save_button'):
                self.save_button.setText(_("Save to Card"))

            if hasattr(self, 'clear_button'):
                self.clear_button.setText(_("Clear Chat"))

            if hasattr(self, 'close_button'):
                self.close_button.setText(_("Close"))

            # 更新输入框占位符
            if hasattr(self, 'input_field'):
                self.input_field.setPlaceholderText(_("Type your message..."))

        except Exception as e:
            print(f"Warning: Failed to update UI language: {e}")

    def _escape_html(self, text):
        """HTML转义"""
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;")
        )

    def _process_ai_message(self, message):
        """处理AI消息，使用mistune进行markdown转换"""
        try:
            import mistune
            # 使用mistune转换markdown
            html = mistune.html(message)

            # 应用聊天界面样式
            html = re.sub(r"<h([1-6])([^>]*)>", r"<h3 style=\"color:#111827;font-weight:600;line-height:1.2;margin:8px 0 4px 0;font-size:1.1rem;\">", html)
            html = re.sub(r"</h[1-6]>", r"</h3>", html)
            html = re.sub(r"<ul([^>]*)>", r"<ul style=\"margin:8px 0;padding-left:20px;color:#111827;\">", html)
            html = re.sub(r"<ol([^>]*)>", r"<ol style=\"margin:8px 0;padding-left:20px;color:#111827;\">", html)
            html = re.sub(r"<li([^>]*)>", r"<li style=\"margin:2px 0;color:#111827;\">", html)
            html = re.sub(r"<p([^>]*)>", r"<p style=\"margin:4px 0;color:#111827;line-height:1.4;\">", html)
            html = re.sub(r"<strong([^>]*)>", r"<strong style=\"font-weight:600;color:#111827;\">", html)
            html = re.sub(r"<code([^>]*)>", r"<code style=\"background-color:#f3f4f6;color:#dc2626;padding:2px 4px;border-radius:3px;font-family:monospace;font-size:0.9em;\">", html)
            html = re.sub(r"<blockquote([^>]*)>", r"<blockquote style=\"margin:8px 0;padding:8px 12px;border-left:3px solid #e5e7eb;background-color:#f9fafb;color:#6b7280;font-style:italic;\">", html)

            return html

        except ImportError:
            # 如果mistune不可用，回退到简单的文本处理
            import logging
            logging.warning("Mistune library not available in chat dialog, using fallback")
            return self._escape_html(message).replace('\n', '<br>')
        except Exception as e:
            # 如果处理出错，回退到转义文本
            import logging
            logging.error(f"Error processing AI message with mistune: {e}")
            return self._escape_html(message).replace('\n', '<br>')

    def save_to_card(self):
        """保存对话到卡片"""
        try:
            # 过滤掉系统消息，只保存用户和AI的对话
            all_conversation = [
                msg for msg in self.conversation_history
                if msg["role"] in ["user", "assistant"]
            ]

            # 只保存新的对话内容（从上次保存后的消息）
            new_conversation = all_conversation[self.saved_message_count:]

            if not new_conversation:
                self.show_message(_("No new conversation to save"), _("Information"))
                return

            # 格式化对话内容
            formatted_conversation = CardService.format_conversation_for_card(new_conversation)

            # 保存到卡片
            success = CardService.append_to_card(formatted_conversation)

            if success:
                # 更新已保存的消息计数
                self.saved_message_count = len(all_conversation)
                self.show_success_message()
            else:
                self.show_message(_("Failed to Save to Card"), _("Error"))

        except Exception as e:
            self.show_message(_("Failed to Save to Card") + f": {str(e)}", _("Error"))
            logging.error(f"Error saving conversation to card: {e}")

    def clear_chat(self):
        """清空聊天记录"""
        if hasattr(self, 'chat_display'):
            self.chat_display.clear()

        # 重置保存计数器
        self.saved_message_count = 0

        # 重新初始化对话历史
        self.initialize_ai_context()

    def exec_(self):
        """显示对话框（Qt5兼容）"""
        # 在显示前更新语言
        self.update_ui_language()
        return super().exec_()

    def exec(self):
        """显示对话框（Qt6兼容）"""
        # 在显示前更新语言
        self.update_ui_language()
        return super().exec()

    def show_success_message(self):
        """显示成功消息 - 现代极简风格"""
        self.show_message(_("Conversation saved to card successfully"), _("Information"))

    def show_message(self, message, title="Message"):
        """显示消息框 - 现代极简风格"""
        if QT_AVAILABLE and hasattr(self, 'chat_display'):
            msg_box = QMessageBox()
            msg_box.setWindowTitle(title)
            msg_box.setText(message)

            # 设置现代极简风格的消息框样式
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    border: 1px solid #e5e7eb;
                    font-size: 14px;
                }
                QMessageBox QLabel {
                    color: #111827;
                    padding: 12px;
                }
                QMessageBox QPushButton {
                    padding: 8px 20px;
                    background-color: #111827;
                    color: white;
                    border: none;
                    font-size: 14px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #374151;
                }
            """)

            # PyQt6兼容性：使用exec()而不是exec_()
            if hasattr(msg_box, 'exec'):
                msg_box.exec()
            else:
                msg_box.exec_()
        else:
            print(f"{title}: {message}")

    def format_conversation_for_display(self, conversation):
        """格式化对话用于显示"""
        formatted_parts = []
        for msg in conversation:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "user":
                formatted_parts.append(f"You: {content}")
            elif role == "assistant":
                formatted_parts.append(f"AI: {content}")

        return "\n\n".join(formatted_parts)

    def get_conversation_summary(self):
        """获取对话摘要"""
        user_messages = sum(1 for msg in self.conversation_history if msg["role"] == "user")
        ai_messages = sum(1 for msg in self.conversation_history if msg["role"] == "assistant")

        return {
            "total_messages": len(self.conversation_history),
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "card_id": self.card_content.get("card_id") if self.card_content else None
        }

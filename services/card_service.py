# 卡片数据服务

import re
import logging

# 尝试相对导入，如果失败则使用绝对导入
try:
    from ..config import Config
except ImportError:
    from config import Config

# 尝试导入Anki模块
try:
    from aqt import mw
    ANKI_AVAILABLE = True
except ImportError:
    mw = None
    ANKI_AVAILABLE = False

class CardService:
    """卡片数据服务类"""
    
    @staticmethod
    def get_current_card_content():
        """获取当前卡片内容"""
        try:
            # 检查Anki环境是否可用
            if not ANKI_AVAILABLE or not mw:
                return None
            
            # 获取当前卡片
            current_card = mw.reviewer.card
            if not current_card:
                return None
            
            # 提取正面和背面内容
            front_html = current_card.question()
            back_html = current_card.answer()
            
            front_content = CardService.extract_text_from_html(front_html)
            back_content = CardService.extract_text_from_html(back_html)
            
            return {
                "front": front_content,
                "back": back_content,
                "card_id": current_card.id
            }
            
        except Exception as e:
            logging.error(f"Error getting current card content: {e}")
            return None
    
    @staticmethod
    def extract_text_from_html(html_content):
        """从HTML中提取纯文本"""
        if not html_content:
            return ""
        
        try:
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', '', html_content)
            
            # 清理多余的空白字符
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logging.error(f"Error extracting text from HTML: {e}")
            return html_content  # 如果提取失败，返回原始内容
    
    @staticmethod
    def append_to_card(conversation_content):
        """将对话内容添加到卡片"""
        try:
            # 检查Anki环境是否可用
            if not ANKI_AVAILABLE or not mw:
                return False
            
            # 获取当前卡片
            current_card = mw.reviewer.card
            if not current_card:
                return False
            
            # 获取卡片的note
            note = current_card.note()
            if not note or len(note.fields) < 2:
                return False
            
            # 获取当前背面内容
            current_back = note.fields[1]  # 假设背面是第二个字段
            
            # 添加对话内容（不再显示 AI Chat History 标题，只保留细分隔线）
            # 将分隔符规范为细线，避免干扰阅读
            separator = "<hr style=\"margin: 6px 0; padding: 0; border: none; border-top: 1px solid #e5e7eb;\">"
            updated_back = current_back + separator + conversation_content
            
            # 更新字段
            note.fields[1] = updated_back
            
            # 保存更改
            note.flush()
            
            # 刷新显示
            if hasattr(mw.reviewer, 'refresh'):
                mw.reviewer.refresh()
            
            return True
            
        except Exception as e:
            logging.error(f"Error appending to card: {e}")
            return False
    
    @staticmethod
    def format_conversation_for_card(conversation_history):
        """格式化对话内容用于添加到卡片（紧凑样式，仿照前端渲染）"""
        if not conversation_history:
            return ""

        def _escape_html(s: str) -> str:
            return (
                s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("'", "&#39;")
            )

        def _light_md_to_html(text: str) -> str:
            """使用 mistune 库进行 Markdown 转 HTML，并应用 Anki 卡片样式"""
            try:
                import mistune
                # 使用mistune转换markdown
                html = mistune.html(text)

                # 应用Anki卡片样式
                html = re.sub(r"<h([1-6])([^>]*)>", r"<h3 style=\"color:#333333;font-weight:600;line-height:1.2;margin:0;padding:0;text-align:left;font-size:1.2rem;display:block;\">", html)
                html = re.sub(r"</h[1-6]>", r"</h3>", html)
                html = re.sub(r"<ul([^>]*)>", r"<ul style=\"margin:0;padding:0 0 0 1.5rem;text-align:left;display:block;\">", html)
                html = re.sub(r"<ol([^>]*)>", r"<ol style=\"margin:0;padding:0 0 0 1.5rem;text-align:left;display:block;\">", html)
                html = re.sub(r"<li([^>]*)>", r"<li style=\"margin:0;padding:0;text-align:left;display:list-item;\">", html)
                html = re.sub(r"<p([^>]*)>", r"<p style=\"margin:0;padding:0;text-align:left;line-height:1.2;display:block;\">", html)
                html = re.sub(r"<strong([^>]*)>", r"<strong style=\"font-weight:600;color:#333333;\">", html)
                html = re.sub(r"<code([^>]*)>", r"<code style=\"background-color:#f3f4f6;color:#dc2626;padding:2px 4px;border-radius:3px;font-family:monospace;font-size:0.875em;\">", html)

                return html

            except ImportError:
                # 如果mistune不可用，回退到简化版本
                logging.warning("Mistune library not available, using fallback markdown parser")
                return _escape_html(text).replace('\n', '<br>')

        try:
            html_parts = []
            for msg in conversation_history:
                role = msg.get("role", "")
                raw = (msg.get("content", "") or "").strip()
                if not raw:
                    continue
                is_user = (role == "user")
                label_color = "#2563eb" if is_user else "#059669"
                label_text = "Question:" if is_user else "Answer:"

                # 检测简单 markdown：特殊字符或双换行
                has_md = bool(re.search(r"[#*`\[\]_~>\-]", raw)) or ("\n\n" in raw)
                if has_md:
                    converted = _light_md_to_html(raw)
                    # 只显示处理后的内容，不显示摘要行
                    styled = converted
                    # 规范化常见块元素样式
                    styled = re.sub(r"<div[^>]*>|</div>", "", styled)
                    styled = re.sub(r"<h3([^>]*)>", "<h3 style=\"color:#333333;font-weight:600;line-height:1.2;margin:0;padding:0;text-align:left;font-size:1.2rem;display:block;\">", styled)
                    styled = re.sub(r"<ul([^>]*)>", "<ul style=\"margin:0;padding:0 0 0 1.5rem;text-align:left;display:block;\">", styled)
                    styled = re.sub(r"<ol([^>]*)>", "<ol style=\"margin:0;padding:0 0 0 1.5rem;text-align:left;display:block;\">", styled)
                    styled = re.sub(r"<li([^>]*)>", "<li style=\"margin:0;padding:0;text-align:left;display:list-item;\">", styled)
                    styled = re.sub(r"<p([^>]*)>", "<p style=\"margin:0;padding:0;text-align:left;line-height:1.2;display:block;\">", styled)
                    styled = re.sub(r"<strong([^>]*)>", "<strong style=\"font-weight:600;color:#333333;\">", styled)
                    styled = re.sub(r"<code([^>]*)>", "<code style=\"background-color:#f3f4f6;color:#dc2626;padding:2px 4px;border-radius:3px;font-family:monospace;font-size:0.875em;\">", styled)

                    # 添加标签和边框包装
                    margin_bottom = "8px" if is_user else "16px"
                    html_parts.append(
                        f"<div style=\"margin:0 0 {margin_bottom} 0;padding:12px 16px;border:1px solid #e5e7eb;text-align:left;line-height:1.2;display:block;\">"
                        f"<span style=\"color:{label_color};font-weight:600;\">{label_text}</span><br>"
                        f"{styled}"
                        f"</div>"
                    )
                else:
                    # 在Q和A之间添加适当的换行间距，并添加边框
                    margin_bottom = "8px" if is_user else "16px"
                    html_parts.append(
                        f"<p style=\"margin:0 0 {margin_bottom} 0;padding:12px 16px;border:1px solid #e5e7eb;text-align:left;line-height:1.2;display:block;\">"
                        f"<span style=\"color:{label_color};font-weight:600;\">{label_text}</span> { _escape_html(raw) }"
                        f"</p>"
                    )
            return "".join(html_parts)
        except Exception as e:
            logging.error(f"Error formatting conversation: {e}")
            return str(conversation_history)
    
    @staticmethod
    def get_conversation_separator():
        """获取对话分隔符"""
        ui_config = Config.get_ui_config()
        return ui_config.get("conversation_separator", "<hr><h3>AI Chat History</h3>")
    
    @staticmethod
    def validate_card_structure(card):
        """验证卡片结构"""
        try:
            if not card:
                return False, "No card provided"
            
            note = card.note()
            if not note:
                return False, "Card has no associated note"
            
            if len(note.fields) < 2:
                return False, "Card must have at least 2 fields (front and back)"
            
            return True, "Card structure is valid"
            
        except Exception as e:
            return False, f"Error validating card structure: {e}"
    
    @staticmethod
    def backup_card_content(card):
        """备份卡片内容（用于错误恢复）"""
        try:
            if not card:
                return None
            
            note = card.note()
            if not note:
                return None
            
            # 创建字段备份
            backup = {
                "card_id": card.id,
                "fields": note.fields.copy(),
                "timestamp": None  # 可以添加时间戳
            }
            
            return backup
            
        except Exception as e:
            logging.error(f"Error backing up card content: {e}")
            return None
    
    @staticmethod
    def restore_card_content(card, backup):
        """从备份恢复卡片内容"""
        try:
            if not card or not backup:
                return False
            
            note = card.note()
            if not note:
                return False
            
            # 恢复字段内容
            note.fields = backup["fields"].copy()
            note.flush()
            
            return True
            
        except Exception as e:
            logging.error(f"Error restoring card content: {e}")
            return False

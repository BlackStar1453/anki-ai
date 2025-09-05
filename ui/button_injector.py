# 按钮注入器 - 在Anki答案界面注入askAI按钮
# 注意：在新版本中，我们直接在__init__.py中使用card_will_show钩子

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

class ButtonInjector:
    """按钮注入器类 - 保留用于向后兼容"""

    @staticmethod
    def inject_ask_ai_button(reviewer):
        """在答案界面注入askAI按钮 - 保留用于测试兼容性"""
        try:
            if not reviewer or not hasattr(reviewer, 'web'):
                return

            # 获取注入JavaScript代码
            js_code = ButtonInjector.get_injection_javascript()

            # 执行JavaScript注入按钮
            reviewer.web.eval(js_code)

            if Config.is_debug_mode():
                print("Ask AI button injected successfully")

        except Exception as e:
            logging.error(f"Error injecting Ask AI button: {e}")
            if Config.is_debug_mode():
                print(f"Error injecting Ask AI button: {e}")

    @staticmethod
    def create_ask_ai_button_html():
        """创建askAI按钮的HTML"""
        button_html = '''
        <div style="text-align: center; margin-top: 20px;">
            <button id="ask-ai-btn" onclick="pycmd('ask_ai')"
                    style="background: #0078d4;
                           color: white;
                           padding: 10px 20px;
                           border: none;
                           border-radius: 5px;
                           cursor: pointer;
                           font-size: 14px;
                           font-weight: bold;
                           transition: background-color 0.3s ease;">
                🤖 Ask AI
            </button>
        </div>
        '''
        return button_html.strip()

    @staticmethod
    def get_injection_javascript():
        """获取注入JavaScript代码"""
        button_html = ButtonInjector.create_ask_ai_button_html()

        js_code = f'''
        (function() {{
            // 检查是否已经注入过按钮
            if (document.getElementById('ask-ai-btn')) {{
                return;
            }}

            // 创建按钮容器
            var buttonContainer = document.createElement('div');
            buttonContainer.innerHTML = `{button_html}`;

            // 将按钮添加到页面底部
            document.body.appendChild(buttonContainer);
        }})();
        '''

        return js_code.strip()
    
    @staticmethod
    def get_injection_javascript():
        """获取注入JavaScript代码"""
        button_html = ButtonInjector.create_ask_ai_button_html()
        
        # 转义HTML中的引号和换行符
        escaped_html = button_html.replace("'", "\\'").replace("\n", "\\n")
        
        js_code = f'''
        (function() {{
            // 检查是否已经存在Ask AI按钮，避免重复注入
            if (document.getElementById('ask-ai-btn')) {{
                return;
            }}
            
            // 查找答案容器
            var answerContainer = document.querySelector('.card') || 
                                document.querySelector('#answer') || 
                                document.body;
            
            if (answerContainer) {{
                // 创建按钮容器
                var buttonContainer = document.createElement('div');
                buttonContainer.innerHTML = '{escaped_html}';
                
                // 添加到答案容器末尾
                answerContainer.appendChild(buttonContainer);
                
                // 添加悬停效果
                var button = document.getElementById('ask-ai-btn');
                if (button) {{
                    button.addEventListener('mouseenter', function() {{
                        this.style.backgroundColor = '#106ebe';
                    }});
                    button.addEventListener('mouseleave', function() {{
                        this.style.backgroundColor = '#0078d4';
                    }});
                }}
            }}
        }})();
        '''
        
        return js_code
    
    @staticmethod
    def remove_ask_ai_button(reviewer):
        """移除askAI按钮"""
        try:
            if not reviewer or not hasattr(reviewer, 'web'):
                return
            
            js_code = '''
            (function() {
                var button = document.getElementById('ask-ai-btn');
                if (button) {
                    var container = button.parentElement;
                    if (container) {
                        container.remove();
                    }
                }
            })();
            '''
            
            reviewer.web.eval(js_code)
            
        except Exception as e:
            logging.error(f"Error removing Ask AI button: {e}")
    
    @staticmethod
    def update_button_state(reviewer, state="normal"):
        """更新按钮状态"""
        try:
            if not reviewer or not hasattr(reviewer, 'web'):
                return
            
            if state == "loading":
                js_code = '''
                (function() {
                    var button = document.getElementById('ask-ai-btn');
                    if (button) {
                        button.innerHTML = '⏳ Processing...';
                        button.disabled = true;
                        button.style.backgroundColor = '#666';
                        button.style.cursor = 'not-allowed';
                    }
                })();
                '''
            elif state == "error":
                js_code = '''
                (function() {
                    var button = document.getElementById('ask-ai-btn');
                    if (button) {
                        button.innerHTML = '❌ Error';
                        button.disabled = false;
                        button.style.backgroundColor = '#d13438';
                        button.style.cursor = 'pointer';
                        
                        // 3秒后恢复正常状态
                        setTimeout(function() {
                            button.innerHTML = '🤖 Ask AI';
                            button.style.backgroundColor = '#0078d4';
                        }, 3000);
                    }
                })();
                '''
            else:  # normal state
                js_code = '''
                (function() {
                    var button = document.getElementById('ask-ai-btn');
                    if (button) {
                        button.innerHTML = '🤖 Ask AI';
                        button.disabled = false;
                        button.style.backgroundColor = '#0078d4';
                        button.style.cursor = 'pointer';
                    }
                })();
                '''
            
            reviewer.web.eval(js_code)
            
        except Exception as e:
            logging.error(f"Error updating button state: {e}")
    
    @staticmethod
    def is_button_injected(reviewer):
        """检查按钮是否已注入"""
        try:
            if not reviewer or not hasattr(reviewer, 'web'):
                return False
            
            # 这个方法在实际使用中可能需要异步处理
            # 这里提供一个基础实现
            return True  # 简化实现，实际中可以通过JavaScript回调检查
            
        except Exception as e:
            logging.error(f"Error checking button injection: {e}")
            return False

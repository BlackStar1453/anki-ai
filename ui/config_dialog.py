# 配置对话框 - 用户友好的设置界面

import logging

# Anki 插件导入
import sys
import os
# 尝试相对导入，如果失败则使用绝对导入
try:
    from ..i18n.translator import _, get_translator, get_supported_languages, set_language
except ImportError:
    try:
        from i18n.translator import _, get_translator, get_supported_languages, set_language
    except ImportError:
        # 如果翻译模块不可用，提供回退函数
        def _(text): return text
        def get_translator(): return None
        def get_supported_languages(): return {'en': 'English'}
        def set_language(lang): pass

# 添加插件目录到路径
addon_dir = os.path.dirname(os.path.dirname(__file__))
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

try:
    from aqt import mw
    from config import Config
    from services.ai_service_adapter import AIServiceAdapter
except ImportError as e:
    print(f"Import error in config_dialog: {e}")
    mw = None
    Config = None
    AIServiceAdapter = None

# 使用Anki的Qt导入（推荐方式）
try:
    from aqt.qt import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                       QLineEdit, QPushButton, QLabel, QMessageBox, 
                       QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
                       QTabWidget, QWidget, QTextEdit, QGroupBox,
                       Qt, QFont)
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
        def setMinimumSize(self, *args, **kwargs):
            pass
        def addTab(self, *args, **kwargs):
            pass
        def addWidget(self, *args, **kwargs):
            pass
        def addLayout(self, *args, **kwargs):
            pass
        def addRow(self, *args, **kwargs):
            pass
        def setText(self, *args, **kwargs):
            pass
        def text(self, *args, **kwargs):
            return ""
        def currentText(self, *args, **kwargs):
            return ""
        def value(self, *args, **kwargs):
            return 0
        def isChecked(self, *args, **kwargs):
            return False
        def toPlainText(self, *args, **kwargs):
            return ""
        def clicked(self):
            return MockSignal()
        def exec_(self):
            pass
        def exec(self):
            pass
        def accept(self):
            pass
        def reject(self):
            pass

    class MockSignal:
        def connect(self, *args, **kwargs):
            pass

    # Mock所有需要的Qt类
    QDialog = MockQtBase
    QVBoxLayout = MockQtBase
    QHBoxLayout = MockQtBase
    QFormLayout = MockQtBase
    QLineEdit = MockQtBase
    QPushButton = MockQtBase
    QLabel = MockQtBase
    QMessageBox = MockQtBase
    QComboBox = MockQtBase
    QSpinBox = MockQtBase
    QDoubleSpinBox = MockQtBase
    QCheckBox = MockQtBase
    QTabWidget = MockQtBase
    QWidget = MockQtBase
    QTextEdit = MockQtBase
    QGroupBox = MockQtBase
    Qt = MockQtBase
    QFont = MockQtBase

    QT_AVAILABLE = False

class ConfigDialog(QDialog):
    """配置对话框"""
    
    def __init__(self, parent=None):
        """初始化配置对话框"""
        super().__init__(parent)
        
        self.setWindowTitle(_("Chat with Card Settings"))
        self.setMinimumSize(600, 500)
        
        # 加载当前配置
        if mw and hasattr(mw, 'addonManager'):
            # 通过当前文件路径可靠地获取插件根目录名作为 addon_id
            import os
            addon_root = os.path.dirname(os.path.dirname(__file__))
            addon_id = os.path.basename(addon_root)
            try:
                self.config = mw.addonManager.getConfig(addon_id) or {}
            except Exception:
                self.config = Config.get_ai_config()
        else:
            self.config = Config.get_ai_config()

        # 设置语言（如果配置中有语言设置）
        if 'language' in self.config:
            set_language(self.config['language'])
        
        # 设置UI（如果Qt可用）
        if QT_AVAILABLE:
            self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()

        # 语言设置标签页
        language_tab = self.create_language_tab()
        tab_widget.addTab(language_tab, _("Language"))

        # API 密钥标签页
        api_tab = self.create_api_tab()
        tab_widget.addTab(api_tab, _("API Key"))

        # 模型配置标签页
        model_tab = self.create_model_tab()
        tab_widget.addTab(model_tab, _("Model"))

        # 高级设置标签页
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, _("Settings"))
        
        layout.addWidget(tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 测试连接按钮
        test_button = QPushButton("🔍 " + _("Test Connection"))
        test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(test_button)

        button_layout.addStretch()

        # 保存和取消按钮
        save_button = QPushButton("💾 " + _("Save"))
        save_button.clicked.connect(self.save_config)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("❌ " + _("Cancel"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)

    def create_language_tab(self):
        """创建语言设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 说明文本
        info_label = QLabel(f"""
        <h3>🌍 {_("Language Settings")}</h3>
        <p>{_("Choose your preferred language for the interface.")}</p>
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 语言选择
        form_layout = QFormLayout()

        self.language_combo = QComboBox()
        supported_languages = get_supported_languages()

        # 从配置中获取当前语言，如果没有则使用默认值
        current_lang = self.config.get('language', 'en')

        for lang_code, lang_name in supported_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
            if lang_code == current_lang:
                self.language_combo.setCurrentText(lang_name)

        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        form_layout.addRow(_("Language") + ":", self.language_combo)

        layout.addLayout(form_layout)

        # 语言说明
        lang_info = QLabel(f"""
        <p><b>{_("Supported Languages")}:</b></p>
        <ul>
        <li><b>English:</b> Full support</li>
        <li><b>简体中文:</b> 完整支持</li>
        <li><b>繁體中文:</b> 完整支援</li>
        <li><b>日本語:</b> 完全サポート</li>
        </ul>
        <p><i>{_("Language changes will take effect after restarting Anki.")}</i></p>
        """)
        lang_info.setWordWrap(True)
        layout.addWidget(lang_info)

        layout.addStretch()
        return widget

    def on_language_changed(self):
        """语言改变时的处理"""
        if hasattr(self, 'language_combo'):
            lang_code = self.language_combo.currentData()
            if lang_code:
                set_language(lang_code)
                # 保存语言设置到配置
                self.config["language"] = lang_code

    def create_api_tab(self):
        """创建API密钥标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明文本
        info_label = QLabel("""
        <h3>🔑 API 密钥配置</h3>
        <p>配置您的 AI 提供商 API 密钥。至少需要配置一个提供商。</p>
        <p><b>获取 API 密钥:</b></p>
        <ul>
        <li><b>OpenAI:</b> <a href="https://platform.openai.com/api-keys">https://platform.openai.com/api-keys</a></li>
        <li><b>Anthropic:</b> <a href="https://console.anthropic.com/">https://console.anthropic.com/</a></li>
        <li><b>Google:</b> <a href="https://makersuite.google.com/app/apikey">https://makersuite.google.com/app/apikey</a></li>
        </ul>
        """)
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)
        
        # API 密钥表单
        form_layout = QFormLayout()
        
        # 主要提供商选择
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "anthropic", "google"])
        self.provider_combo.setCurrentText(self.config.get("ai_provider", "openai"))
        form_layout.addRow("🎯 主要提供商:", self.provider_combo)
        
        # OpenAI API 密钥
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setText(self.config.get("openai_api_key", ""))
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_edit.setPlaceholderText("sk-...")
        form_layout.addRow("🔵 OpenAI API 密钥:", self.openai_key_edit)
        
        # Anthropic API 密钥
        self.anthropic_key_edit = QLineEdit()
        self.anthropic_key_edit.setText(self.config.get("anthropic_api_key", ""))
        self.anthropic_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key_edit.setPlaceholderText("sk-ant-...")
        form_layout.addRow("🟠 Anthropic API 密钥:", self.anthropic_key_edit)
        
        # Google API 密钥
        self.google_key_edit = QLineEdit()
        self.google_key_edit.setText(self.config.get("google_api_key", ""))
        self.google_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.google_key_edit.setPlaceholderText("AI...")
        form_layout.addRow("🔴 Google API 密钥:", self.google_key_edit)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        return widget
    
    def create_model_tab(self):
        """创建模型配置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明文本
        info_label = QLabel("""
        <h3>🤖 模型配置</h3>
        <p>调整 AI 模型的行为参数。</p>
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 模型配置表单
        form_layout = QFormLayout()
        
        # OpenAI 模型选择（改为动态填充）
        self.model_combo = QComboBox()
        self.model_combo.setEditable(False)
        saved_model = self.config.get("openai_model", "")
        if saved_model:
            self.model_combo.addItem(saved_model)
        form_layout.addRow("🔵 OpenAI 模型:", self.model_combo)

        # 刷新模型按钮
        self.refresh_models_btn = QPushButton("刷新模型")
        self.refresh_models_btn.clicked.connect(self.refresh_models)
        form_layout.addRow("", self.refresh_models_btn)
        
        # 最大令牌数
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(50, 4000)
        self.max_tokens_spin.setValue(self.config.get("max_tokens", 500))
        self.max_tokens_spin.setSuffix(" tokens")
        form_layout.addRow("📏 最大令牌数:", self.max_tokens_spin)
        
        # 温度（创造性）
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.config.get("temperature", 0.7))
        self.temperature_spin.setDecimals(1)
        form_layout.addRow("🌡️ 温度 (创造性):", self.temperature_spin)
        
        layout.addLayout(form_layout)
        
        # 温度说明
        temp_info = QLabel("""
        <p><b>温度说明:</b></p>
        <ul>
        <li><b>0.0-0.3:</b> 更准确、一致的回答</li>
        <li><b>0.4-0.7:</b> 平衡的创造性和准确性</li>
        <li><b>0.8-2.0:</b> 更有创造性、多样化的回答</li>
        </ul>
        """)
        temp_info.setWordWrap(True)
        layout.addWidget(temp_info)
        
        layout.addStretch()
        
        return widget
    
    def create_advanced_tab(self):
        """创建高级设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明文本
        info_label = QLabel("""
        <h3>⚙️ 高级设置</h3>
        <p>配置高级功能和性能参数。</p>
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 高级设置表单
        form_layout = QFormLayout()
        
        # 使用统一服务（已禁用）
        self.unified_service_check = QCheckBox()
        self.unified_service_check.setChecked(False)
        self.unified_service_check.setEnabled(False)
        form_layout.addRow("🔄 使用统一服务 (已禁用):", self.unified_service_check)
        
        # 重试次数
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 10)
        self.retry_spin.setValue(self.config.get("retry_attempts", 3))
        form_layout.addRow("🔁 重试次数:", self.retry_spin)
        
        # 超时时间
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 120)
        self.timeout_spin.setValue(self.config.get("timeout", 30))
        self.timeout_spin.setSuffix(" 秒")
        form_layout.addRow("⏱️ 超时时间:", self.timeout_spin)
        
        # 调试模式
        self.debug_check = QCheckBox()
        self.debug_check.setChecked(self.config.get("debug_mode", False))
        form_layout.addRow("🐛 调试模式:", self.debug_check)
        
        layout.addLayout(form_layout)
        
        # 回退提供商配置
        fallback_group = QGroupBox("🔄 回退提供商")
        fallback_layout = QVBoxLayout(fallback_group)
        
        fallback_info = QLabel("当主要提供商失败时，自动尝试这些提供商:")
        fallback_layout.addWidget(fallback_info)
        
        self.fallback_text = QTextEdit()
        self.fallback_text.setMaximumHeight(80)
        fallback_providers = self.config.get("fallback_providers", [])
        self.fallback_text.setPlainText(", ".join(fallback_providers))
        self.fallback_text.setPlaceholderText("例如: anthropic, google")
        fallback_layout.addWidget(self.fallback_text)
        
        layout.addWidget(fallback_group)
        layout.addStretch()
        
        return widget
    
    def test_connection(self):
        """测试连接（直连 OpenAI）"""
        try:
            # 临时保存配置进行测试
            temp_config = self.get_current_config()

            # 检查 API 密钥
            api_key = temp_config.get('openai_api_key', '').strip()
            if not api_key:
                QMessageBox.warning(self, "连接测试", "❌ 请先设置有效的 API 密钥")
                return

            # 更新配置
            if Config:
                for key, value in temp_config.items():
                    Config.set(key, value)

            # 测试连接
            if AIServiceAdapter:
                adapter = AIServiceAdapter()
            else:
                QMessageBox.warning(self, "连接测试", "❌ 无法导入 AI 服务模块")
                return

            # 显示测试进度
            from aqt.qt import QProgressDialog
            progress = QProgressDialog("正在测试连接...", "取消", 0, 0, self)
            progress.setWindowModality(2)  # Qt.WindowModal
            progress.show()

            try:
                is_valid, message = adapter.validate_api_key()

                if is_valid:
                    QMessageBox.information(self, "连接测试", f"✅ 连接成功!\n\n{message}")
                else:
                    QMessageBox.warning(self, "连接测试", f"❌ 连接失败!\n\n{message}")
            finally:
                progress.close()

        except Exception as e:
            error_msg = f"💥 测试过程中发生错误:\n\n{str(e)}"
            QMessageBox.critical(self, "连接测试", error_msg)
    
    def get_current_config(self):
        """获取当前配置"""
        # 处理回退提供商
        fallback_text = self.fallback_text.toPlainText().strip()
        fallback_providers = []
        if fallback_text:
            fallback_providers = [p.strip() for p in fallback_text.split(",") if p.strip()]
        
        # 获取语言设置
        language_code = 'en'  # 默认值
        if hasattr(self, 'language_combo') and self.language_combo.currentData():
            language_code = self.language_combo.currentData()

        return {
            "language": language_code,
            "ai_provider": self.provider_combo.currentText(),
            "openai_api_key": self.openai_key_edit.text().strip(),
            "anthropic_api_key": self.anthropic_key_edit.text().strip(),
            "google_api_key": self.google_key_edit.text().strip(),
            "openai_model": self.model_combo.currentText(),
            "max_tokens": self.max_tokens_spin.value(),
            "temperature": self.temperature_spin.value(),
            "use_unified_service": self.unified_service_check.isChecked(),
            "retry_attempts": self.retry_spin.value(),
            "timeout": self.timeout_spin.value(),
            "debug_mode": self.debug_check.isChecked(),
            "fallback_providers": fallback_providers
        }
    
    def save_config(self):
        """保存配置"""
        try:
            # 获取当前配置
            new_config = self.get_current_config()

            # 验证配置
            if not self.validate_config(new_config):
                return

            # 保存配置到 Anki
            if mw and hasattr(mw, 'addonManager'):
                # 通过当前文件路径可靠地获取插件根目录名作为 addon_id
                # 如果是通过本地安装，不存在addon_id，而是使用文件名作为目录，比如/Users/cengyaohua/Library/Application Support/Anki2/addons21/anki-ai-chat
                import os
                addon_root = os.path.dirname(os.path.dirname(__file__))
                addon_id = os.path.basename(addon_root)
                mw.addonManager.writeConfig(addon_id, new_config)
            else:
                # 回退到传统方式
                for key, value in new_config.items():
                    Config.set(key, value)
                Config.save_config()

            QMessageBox.information(self, "保存配置", "✅ 配置已保存成功!\n\n请重启 Anki 以使配置生效。")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "保存配置", f"💥 保存配置时发生错误:\n\n{str(e)}")
    
    def validate_config(self, config):
        """验证配置"""
        # 检查是否至少有一个 API 密钥
        api_keys = [
            config.get("openai_api_key", ""),
            config.get("anthropic_api_key", ""),
            config.get("google_api_key", "")
        ]
        
        if not any(key.strip() for key in api_keys):
            QMessageBox.warning(self, "配置验证", "⚠️ 请至少配置一个 AI 提供商的 API 密钥!")
            return False
        
        # 检查主要提供商是否有对应的 API 密钥
        provider = config.get("ai_provider", "openai")
        provider_key = config.get(f"{provider}_api_key", "")
        
        if not provider_key.strip():
            QMessageBox.warning(self, "配置验证", f"⚠️ 主要提供商 {provider} 的 API 密钥未配置!")
            return False
        
        return True

    def refresh_models(self):
        """使用当前 API Key 从 OpenAI 获取模型列表并填充下拉框"""
        try:
            api_key = self.openai_key_edit.text().strip()
            if not api_key:
                QMessageBox.warning(self, "刷新模型", "请先填写 OpenAI API 密钥")
                return
            # 临时更新配置供服务使用
            if Config:
                Config.set("openai_api_key", api_key)
            if AIServiceAdapter:
                adapter = AIServiceAdapter()
                svc = adapter._service
                ok, models, msg = svc.list_models()
                if not ok:
                    QMessageBox.warning(self, "刷新模型", f"获取模型失败: {msg}")
                    return
                # 填充下拉
                self.model_combo.clear()
                # 优先保留当前保存的模型
                saved = self.config.get("openai_model", "").strip()
                if saved and saved not in models:
                    self.model_combo.addItem(saved)
                for m in models:
                    if not saved or m != saved:
                        self.model_combo.addItem(m)
                QMessageBox.information(self, "刷新模型", f"已加载 {len(models)} 个模型")
            else:
                QMessageBox.warning(self, "刷新模型", "服务不可用")
        except Exception as e:
            QMessageBox.critical(self, "刷新模型", f"异常: {str(e)}")

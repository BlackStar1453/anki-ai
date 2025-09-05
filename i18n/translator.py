"""
多语言支持模块
支持英文、中文简体、中文繁体、日文
"""

import os
import locale
import gettext
from typing import Dict, Optional

# 内置翻译字典作为回退
FALLBACK_TRANSLATIONS = {
    'zh_CN': {
        'Chat with Card': 'Chat with Card',
        'Open Chat': '打开聊天',
        'Settings': '设置',
        'Chat with AI': '与AI聊天',
        'Type your message...': '输入您的消息...',
        'Send': '发送',
        'Clear Chat': '清空聊天',
        'Save to Card': '保存到卡片',
        'Save': '保存',
        'Failed to Save to Card': '保存到卡片失败',
        'Conversation saved to card successfully': '对话已成功保存到卡片',
        'Close': '关闭',
        'Chat with Card Settings': 'Chat with Card设置',
        'Language': '语言',
        'AI Provider': 'AI提供商',
        'API Key': 'API密钥',
        'Model': '模型',
        'Save': '保存',
        'Cancel': '取消',
        'Error': '错误',
        'Warning': '警告',
        'Information': '信息',
        'Card created successfully': '卡片创建成功',
        'Failed to create card': '创建卡片失败',
        'No new conversation to save': '没有新的对话需要保存',
        'Please enter a message': '请输入消息',
        'Test Connection': '测试连接',
    },
    'zh_TW': {
        'Chat with Card': 'Chat with Card',
        'Open Chat': '開啟聊天',
        'Settings': '設定',
        'Chat with AI': '與AI聊天',
        'Type your message...': '輸入您的訊息...',
        'Send': '傳送',
        'Clear Chat': '清空聊天',
        'Save to Card': '儲存到卡片',
        'Save': '儲存',
        'Failed to Save to Card': '儲存到卡片失敗',
        'Conversation saved to card successfully': '對話已成功儲存到卡片',
        'Close': '關閉',
        'Chat with Card Settings': 'Chat with Card設定',
        'Language': '語言',
        'AI Provider': 'AI提供商',
        'API Key': 'API金鑰',
        'Model': '模型',
        'Save': '儲存',
        'Cancel': '取消',
        'Error': '錯誤',
        'Warning': '警告',
        'Information': '資訊',
        'Card created successfully': '卡片建立成功',
        'Failed to create card': '建立卡片失敗',
        'No new conversation to save': '沒有新的對話需要儲存',
        'Please enter a message': '請輸入訊息',
        'Test Connection': '測試連線',
    },
    'ja': {
        'Chat with Card': 'カードチャット',
        'Open Chat': 'チャットを開く',
        'Settings': '設定',
        'Chat with AI': 'AIとチャット',
        'Type your message...': 'メッセージを入力してください...',
        'Send': '送信',
        'Clear Chat': 'チャットをクリア',
        'Create Card': 'カードを作成',
        'Close': '閉じる',
        'Chat with Card Settings': 'カードチャット設定',
        'Language': '言語',
        'AI Provider': 'AIプロバイダー',
        'API Key': 'APIキー',
        'Model': 'モデル',
        'Save': '保存',
        'Cancel': 'キャンセル',
        'Error': 'エラー',
        'Warning': '警告',
        'Information': '情報',
        'Card created successfully': 'カードが正常に作成されました',
        'Failed to create card': 'カードの作成に失敗しました',
        'No new conversation to save': '保存する新しい会話がありません',
        'Please enter a message': 'メッセージを入力してください',
        'Test Connection': '接続テスト',
        'Save to Card': 'カードに保存',
        'Save': '保存',
        'Failed to Save to Card': 'カードへの保存に失敗しました',
        'Conversation saved to card successfully': '会話がカードに正常に保存されました',
    }
}

class Translator:
    """多语言翻译器"""

    def __init__(self, addon_dir: str):
        self.addon_dir = addon_dir
        self.locale_dir = os.path.join(addon_dir, 'i18n', 'locales')
        self.domain = 'chat_with_card'
        self.current_lang = 'en'
        self._translations: Dict[str, gettext.GNUTranslations] = {}

        # 支持的语言
        self.supported_languages = {
            'en': 'English',
            'zh_CN': '简体中文',
            'zh_TW': '繁體中文',
            'ja': '日本語'
        }

        # 优先使用回退翻译，如果可用则尝试gettext
        self._detect_system_language()
        try:
            self._setup_translations()
        except Exception as e:
            print(f"Warning: gettext setup failed, using fallback translations: {e}")
    
    def _setup_translations(self):
        """设置翻译"""
        for lang_code in self.supported_languages.keys():
            try:
                # 确保locale目录存在
                if not os.path.exists(self.locale_dir):
                    print(f"Warning: Locale directory not found: {self.locale_dir}")
                    self._translations[lang_code] = gettext.NullTranslations()
                    continue

                translation = gettext.translation(
                    self.domain,
                    localedir=self.locale_dir,
                    languages=[lang_code],
                    fallback=True
                )
                self._translations[lang_code] = translation
            except Exception as e:
                print(f"Warning: Could not load translation for {lang_code}: {e}")
                # 使用空翻译作为回退
                self._translations[lang_code] = gettext.NullTranslations()
    
    def _detect_system_language(self):
        """检测系统语言"""
        try:
            # 获取系统语言设置
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # 处理不同的语言代码格式
                if system_locale.startswith('zh_CN') or system_locale.startswith('zh-CN'):
                    self.current_lang = 'zh_CN'
                elif system_locale.startswith('zh_TW') or system_locale.startswith('zh-TW'):
                    self.current_lang = 'zh_TW'
                elif system_locale.startswith('ja'):
                    self.current_lang = 'ja'
                else:
                    self.current_lang = 'en'
        except Exception:
            self.current_lang = 'en'
    
    def set_language(self, lang_code: str):
        """设置当前语言"""
        if lang_code in self.supported_languages:
            self.current_lang = lang_code
            print(f"Language switched to: {self.supported_languages[lang_code]} ({lang_code})")
        else:
            print(f"Warning: Unsupported language code: {lang_code}, using English")
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_lang
    
    def get_language_name(self, lang_code: Optional[str] = None) -> str:
        """获取语言名称"""
        code = lang_code or self.current_lang
        return self.supported_languages.get(code, 'English')
    
    def get_supported_languages(self) -> Dict[str, str]:
        """获取支持的语言列表"""
        return self.supported_languages.copy()
    
    def _(self, message: str) -> str:
        """翻译消息"""
        try:
            translation = self._translations.get(self.current_lang)
            if translation:
                translated = translation.gettext(message)
                # 如果gettext返回原始消息（未翻译），尝试使用回退翻译
                if translated == message and self.current_lang in FALLBACK_TRANSLATIONS:
                    return FALLBACK_TRANSLATIONS[self.current_lang].get(message, message)
                return translated
        except Exception as e:
            print(f"Translation error: {e}")

        # 尝试使用回退翻译
        if self.current_lang in FALLBACK_TRANSLATIONS:
            return FALLBACK_TRANSLATIONS[self.current_lang].get(message, message)

        # 回退到原始消息
        return message
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """复数形式翻译"""
        try:
            translation = self._translations.get(self.current_lang)
            if translation:
                return translation.ngettext(singular, plural, n)
        except Exception as e:
            print(f"Translation error: {e}")
        
        # 回退到简单的复数处理
        return singular if n == 1 else plural

# 全局翻译器实例
_translator: Optional[Translator] = None

def init_translator(addon_dir: str):
    """初始化翻译器"""
    global _translator
    try:
        _translator = Translator(addon_dir)
        print("✅ 多语言翻译器初始化成功（使用内置翻译）")
    except Exception as e:
        print(f"Warning: Failed to initialize translator: {e}")
        _translator = None

def get_translator() -> Optional[Translator]:
    """获取翻译器实例"""
    return _translator

def _(message: str) -> str:
    """快捷翻译函数"""
    if _translator:
        return _translator._(message)
    return message

def ngettext(singular: str, plural: str, n: int) -> str:
    """快捷复数翻译函数"""
    if _translator:
        return _translator.ngettext(singular, plural, n)
    return singular if n == 1 else plural

def set_language(lang_code: str):
    """设置语言"""
    if _translator:
        _translator.set_language(lang_code)
    else:
        # 如果翻译器未初始化，至少记录语言选择
        print(f"Language set to: {lang_code} (translator not initialized)")

def get_current_language() -> str:
    """获取当前语言"""
    if _translator:
        return _translator.get_current_language()
    return 'en'

def get_supported_languages() -> Dict[str, str]:
    """获取支持的语言"""
    # 始终返回完整的语言列表，即使翻译器未初始化
    supported_languages = {
        'en': 'English',
        'zh_CN': '简体中文',
        'zh_TW': '繁體中文',
        'ja': '日本語'
    }

    if _translator:
        return _translator.get_supported_languages()
    return supported_languages

#!/usr/bin/env python3
"""
测试多语言功能
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_translations():
    """测试翻译功能"""
    print("🌍 测试多语言功能")
    print("=" * 50)

    try:
        # 导入翻译模块
        from i18n.translator import init_translator, _, set_language, get_supported_languages

        # 初始化翻译器
        addon_dir = os.path.dirname(__file__)
        init_translator(addon_dir)

        # 首先测试语言列表
        languages = get_supported_languages()
        print(f"支持的语言: {languages}")

        # 测试文本
        test_texts = [
            "Chat with Card",
            "Open Chat",
            "Settings",
            "Chat with AI",
            "Send",
            "Close"
        ]

        # 测试所有支持的语言
        for lang_code, lang_name in languages.items():
            print(f"\n📝 测试语言: {lang_name} ({lang_code})")
            print("-" * 30)

            # 设置语言
            set_language(lang_code)

            # 翻译测试文本
            for text in test_texts:
                translated = _(text)
                if translated != text:
                    print(f"  ✅ '{text}' -> '{translated}'")
                else:
                    print(f"  ➡️  '{text}' (unchanged)")

        print(f"\n🎉 多语言测试完成！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_translations():
    """测试回退翻译"""
    print("\n🔄 测试回退翻译功能")
    print("=" * 50)
    
    try:
        from i18n.translator import FALLBACK_TRANSLATIONS
        
        for lang_code, translations in FALLBACK_TRANSLATIONS.items():
            print(f"\n📝 {lang_code} 回退翻译:")
            print("-" * 20)
            for en_text, translated_text in translations.items():
                print(f"  '{en_text}' -> '{translated_text}'")
        
        print(f"\n✅ 回退翻译测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 回退翻译测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Chat with Card 多语言测试")
    print("=" * 60)
    
    success1 = test_translations()
    success2 = test_fallback_translations()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)

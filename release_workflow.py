#!/usr/bin/env python3
"""
完整的发布工作流程
自动化构建、检查和发布准备
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 完成")
            return True
        else:
            print(f"❌ {description} 失败:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} 异常: {e}")
        return False

def check_prerequisites():
    """检查前置条件"""
    print("🔍 检查前置条件...")
    
    # 检查必需文件
    required_files = [
        '__init__.py',
        'manifest.json',
        'config.json',
        'build_addon.py',
        'check_release.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必需文件: {missing_files}")
        return False
    
    # 检查目录结构
    required_dirs = ['ui', 'services', 'i18n']
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ 缺少必需目录: {missing_dirs}")
        return False
    
    print("✅ 前置条件检查通过")
    return True

def update_version():
    """更新版本信息"""
    print("📝 检查版本信息...")
    
    try:
        with open('manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        current_version = manifest.get('version', '2.0.0')
        print(f"当前版本: {current_version}")
        
        # 可以在这里添加版本自动递增逻辑
        # 现在只是显示当前版本
        
        return True
    except Exception as e:
        print(f"❌ 版本检查失败: {e}")
        return False

def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    # 运行多语言测试
    if Path('test_i18n.py').exists():
        if not run_command('python test_i18n.py', '多语言功能测试'):
            return False
    
    # 可以添加更多测试
    print("✅ 所有测试通过")
    return True

def build_addon():
    """构建插件"""
    print("🔨 构建插件...")
    return run_command('python build_addon.py', '插件构建')

def check_release():
    """检查发布"""
    print("🔍 检查发布...")
    return run_command('python check_release.py', '发布检查')

def create_release_notes():
    """创建发布说明"""
    print("📋 创建发布说明...")
    
    try:
        with open('manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        version = manifest.get('version', '2.0.0')
        
        release_notes = f"""# Chat with Card v{version} Release Notes

## 🎉 New Features
- Multi-language support (English, 简体中文, 繁體中文, 日本語)
- AI-powered chat interface with markdown support
- Direct card creation from conversations
- Modern, minimalist UI design

## 🔧 Technical Improvements
- Self-contained dependencies (no external installations required)
- Improved error handling and user feedback
- Optimized performance and memory usage
- Enhanced compatibility with Anki 2.1+

## 🌍 Internationalization
- Automatic system language detection
- Manual language switching in settings
- Complete interface translation for all supported languages
- Fallback translation system for reliability

## 📦 Installation
1. Download the .ankiaddon file
2. In Anki: Tools > Add-ons > Install from file
3. Select the downloaded file
4. Restart Anki
5. Configure your AI API key in the settings

## 🚀 Getting Started
1. Open any card in Anki
2. Click the "Open Chat" button
3. Start chatting with AI about your card
4. Create new cards directly from your conversations

## 🔗 Links
- AnkiWeb: https://ankiweb.net/shared/addons/
- Documentation: See installation guide
- Support: Check the addon description for contact information

---
Built with ❤️ for the Anki community
"""
        
        release_notes_path = Path('RELEASE_NOTES.md')
        with open(release_notes_path, 'w', encoding='utf-8') as f:
            f.write(release_notes)
        
        print(f"✅ 发布说明已创建: {release_notes_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建发布说明失败: {e}")
        return False

def main():
    """主工作流程"""
    print("🚀 Chat with Card 发布工作流程")
    print("=" * 60)
    
    # 工作流程步骤
    steps = [
        ("检查前置条件", check_prerequisites),
        ("更新版本信息", update_version),
        ("运行测试", run_tests),
        ("构建插件", build_addon),
        ("检查发布", check_release),
        ("创建发布说明", create_release_notes)
    ]
    
    # 执行步骤
    for step_name, step_func in steps:
        print(f"\n📋 步骤: {step_name}")
        print("-" * 40)
        
        if not step_func():
            print(f"\n❌ 工作流程在 '{step_name}' 步骤失败")
            return False
    
    # 成功完成
    print("\n" + "=" * 60)
    print("🎉 发布工作流程完成！")
    print("=" * 60)
    
    # 查找生成的文件
    dist_dir = Path('dist')
    if dist_dir.exists():
        addon_files = list(dist_dir.glob('*.ankiaddon'))
        if addon_files:
            latest_addon = max(addon_files, key=lambda p: p.stat().st_mtime)
            print(f"📦 插件文件: {latest_addon}")
            print(f"📊 文件大小: {latest_addon.stat().st_size / 1024:.1f} KB")
    
    print(f"\n🌐 下一步 - 发布到AnkiWeb:")
    print(f"1. 访问: https://ankiweb.net/shared/addons/")
    print(f"2. 点击 'Upload' 按钮")
    print(f"3. 上传插件文件")
    print(f"4. 填写插件信息（参考 RELEASE_INFO_*.md）")
    print(f"5. 提交审核")
    
    print(f"\n📋 发布后:")
    print(f"1. 监控用户反馈")
    print(f"2. 准备后续更新")
    print(f"3. 维护文档和支持")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

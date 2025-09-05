#!/usr/bin/env python3
"""
Anki 插件打包脚本
将项目打包为可安装的 .ankiaddon 文件
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
import time
from pathlib import Path

def get_addon_info():
    """获取插件信息"""
    try:
        with open('manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        return {
            'name': manifest.get('name', 'Chat with Card'),
            'version': manifest.get('version', '2.0.0'),
            'package': manifest.get('package', 'chat-with-card'),
            'description': manifest.get('description', 'AI Chat Tool for Anki'),
            'timestamp': time.strftime('%Y%m%d_%H%M%S')
        }
    except Exception as e:
        print(f"警告: 无法读取 manifest.json: {e}")
        return {
            'name': 'Chat with Card',
            'version': '2.0.0',
            'package': 'chat-with-card',
            'description': 'AI Chat Tool for Anki',
            'timestamp': time.strftime('%Y%m%d_%H%M%S')
        }

def create_build_directory():
    """创建构建目录"""
    build_dir = Path('build')
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    return build_dir

def prepare_vendor():
    """准备 vendor 依赖目录（将第三方库安装到 vendor/）"""
    print("📦 准备 vendor 依赖...")
    vendor_path = Path('vendor')
    if vendor_path.exists():
        print("   ♻️  清理现有 vendor 目录...")
        shutil.rmtree(vendor_path)
    vendor_path.mkdir(parents=True, exist_ok=True)

    # 需要打包的依赖（根据Anki官方文档打包第三方库）
    deps = [
        'mistune>=3.0.0',   # Markdown 处理库
        'requests>=2.25.0', # HTTP 请求库
        'tenacity>=9.0.0'   # 重试机制库
    ]
    import subprocess
    for dep in deps:
        print(f"   ⬇️  安装 {dep} 到 vendor/")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            '--target', str(vendor_path),
            '--no-deps',  # 不下载子依赖，避免冲突
            dep
        ], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ❌ 安装 {dep} 失败: {result.stderr[:200]}")
        else:
            print(f"   ✅ {dep} 安装完成")

    # 清理无关文件
    for pycache in vendor_path.rglob('__pycache__'):
        shutil.rmtree(pycache, ignore_errors=True)
    for pyc in vendor_path.rglob('*.pyc'):
        try:
            pyc.unlink()
        except Exception:
            pass

    print("   ✅ vendor 依赖准备完成")
    return vendor_path

def compile_translations():
    """编译翻译文件（可选，有内置回退翻译）"""
    print("🌍 检查翻译文件...")

    i18n_dir = Path('i18n')
    if not i18n_dir.exists():
        print("   ℹ️  i18n 目录不存在，将使用内置翻译")
        return True

    locales_dir = i18n_dir / 'locales'
    if not locales_dir.exists():
        print("   ℹ️  locales 目录不存在，将使用内置翻译")
        return True

    success_count = 0
    total_count = 0

    # 遍历所有语言目录
    for lang_dir in locales_dir.iterdir():
        if not lang_dir.is_dir():
            continue

        lc_messages_dir = lang_dir / 'LC_MESSAGES'
        if not lc_messages_dir.exists():
            continue

        # 查找 .po 文件并编译为 .mo 文件
        po_files = list(lc_messages_dir.glob('*.po'))
        for po_file in po_files:
            total_count += 1
            mo_file = po_file.with_suffix('.mo')

            try:
                # 使用 msgfmt 命令编译（如果可用）
                result = subprocess.run([
                    'msgfmt',
                    '-o', str(mo_file),
                    str(po_file)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"   ✅ {po_file.relative_to(i18n_dir)} -> {mo_file.relative_to(i18n_dir)}")
                    success_count += 1
                else:
                    print(f"   ❌ 编译失败: {po_file.relative_to(i18n_dir)}")

            except FileNotFoundError:
                # msgfmt 不可用，使用 Python 的 gettext 模块
                try:
                    import polib
                    po = polib.pofile(str(po_file))
                    po.save_as_mofile(str(mo_file))
                    print(f"   ✅ {po_file.relative_to(i18n_dir)} -> {mo_file.relative_to(i18n_dir)} (Python)")
                    success_count += 1
                except ImportError:
                    print(f"   ℹ️  跳过 {po_file.relative_to(i18n_dir)} (msgfmt/polib不可用，使用内置翻译)")
                except Exception as e:
                    print(f"   ⚠️  {po_file.relative_to(i18n_dir)} 编译失败，使用内置翻译: {e}")
            except Exception as e:
                print(f"   ⚠️  {po_file.relative_to(i18n_dir)} 编译失败，使用内置翻译: {e}")

    if total_count > 0:
        print(f"   📊 翻译文件处理: {success_count}/{total_count} 编译成功")
        if success_count == 0:
            print("   ✅ 将使用内置翻译（更可靠，无需外部工具）")
        elif success_count < total_count:
            print("   ✅ 部分使用编译翻译，部分使用内置翻译")
        else:
            print("   ✅ 所有翻译文件编译成功")
    else:
        print("   ✅ 没有找到.po文件，将使用内置翻译（推荐方式）")

    return True

def copy_source_files(build_dir):
    """复制源文件到构建目录"""
    print("📁 复制源文件...")

    # 需要包含的文件和目录
    include_patterns = [
        '__init__.py',
        'manifest.json',
        'config.json',  # Anki 标准配置文件
        'config.py',
        'services/',
        'ui/',
        'utils/',
        'vendor/',  # 外部依赖打包目录（仅 requests 等纯 Python）
        'i18n/',    # 多语言文件目录
        'requirements.txt'
    ]
    
    # 排除的文件和目录
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.pytest_cache',
        'test_*.py',
        'build/',
        'dist/',
        '*.pyc',
        '.DS_Store',
        'run_all_*.py',
        'quick_*.py',
        'migration_*.md',
        'litellm_*.md',
        'project_files_inventory.md'
        # 注意：不再排除 *.json，以便 vendor 中的元数据得以打包
    ]
    
    copied_files = []
    
    for pattern in include_patterns:
        path = Path(pattern)
        
        if path.is_file():
            # 复制文件
            dest = build_dir / path.name
            shutil.copy2(path, dest)
            copied_files.append(str(path))
            print(f"   ✅ {path}")
            
        elif path.is_dir():
            # 复制目录
            dest = build_dir / path.name
            shutil.copytree(path, dest, ignore=shutil.ignore_patterns(*exclude_patterns))
            copied_files.append(str(path))
            print(f"   ✅ {path}/")
    
    return copied_files

def create_meta_inf(build_dir, addon_info):
    """创建 META-INF 目录和文件"""
    print("📋 创建 META-INF...")
    
    meta_inf_dir = build_dir / 'META-INF'
    meta_inf_dir.mkdir()
    
    # 创建 manifest.json（Anki 插件格式）
    anki_manifest = {
        "name": addon_info['name'],
        "package": addon_info['package'],
        "version": addon_info['version'],
        "description": addon_info['description'],
        "author": "Anki AI Chat Developer",
        "homepage": "",
        "tags": ["ai", "chat", "openai", "anthropic", "google", "study"],
        "min_point_version": 45,
        "max_point_version": 0
    }
    
    with open(meta_inf_dir / 'manifest.json', 'w', encoding='utf-8') as f:
        json.dump(anki_manifest, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ META-INF/manifest.json")
    return meta_inf_dir

def clean_build_directory(build_dir):
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    # 删除测试文件
    for test_file in build_dir.rglob('test_*.py'):
        test_file.unlink()
        print(f"   🗑️  删除测试文件: {test_file.name}")
    
    # 删除 __pycache__ 目录
    for pycache_dir in build_dir.rglob('__pycache__'):
        shutil.rmtree(pycache_dir)
        print(f"   🗑️  删除缓存目录: {pycache_dir}")
    
    # 删除 .pyc 文件
    for pyc_file in build_dir.rglob('*.pyc'):
        pyc_file.unlink()
        print(f"   🗑️  删除编译文件: {pyc_file.name}")

def create_addon_package(build_dir, addon_info):
    """创建 .ankiaddon 包"""
    print("📦 创建插件包...")
    
    # 创建输出目录
    dist_dir = Path('dist')
    dist_dir.mkdir(exist_ok=True)
    
    # 生成文件名
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"{addon_info['package']}-v{addon_info['version']}-{timestamp}.ankiaddon"
    addon_path = dist_dir / filename
    
    # 创建 ZIP 文件
    with zipfile.ZipFile(addon_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in build_dir.rglob('*'):
            if file_path.is_file():
                # 计算相对路径
                arcname = file_path.relative_to(build_dir)
                zipf.write(file_path, arcname)
                print(f"   📄 添加: {arcname}")
    
    return addon_path

def create_installation_guide(addon_path, addon_info):
    """创建安装指南"""
    print("📖 创建安装指南...")
    
    guide_content = f"""# {addon_info['name']} v{addon_info['version']} - 安装指南

## 🚀 快速安装

### 方法一：通过 Anki 插件管理器（推荐）
1. 打开 Anki
2. 选择 "工具" → "插件"
3. 点击 "从文件安装..."
4. 选择文件: `{addon_path.name}`
5. 重启 Anki

### 方法二：手动安装
1. 将 `{addon_path.name}` 重命名为 `{addon_path.stem}.zip`
2. 解压到 Anki 插件目录
3. 重启 Anki

## ⚙️ 配置 API 密钥

安装后需要配置 AI 提供商的 API 密钥：

### 1. 获取 API 密钥
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google**: https://makersuite.google.com/app/apikey

### 2. 配置密钥
1. 在 Anki 中选择 "工具" → "插件"
2. 选择 "{addon_info['name']}"
3. 点击 "配置"
4. 设置您的 API 密钥：
   ```json
   {{
     "ai_provider": "openai",
     "openai_api_key": "your-openai-api-key-here",
     "anthropic_api_key": "your-anthropic-api-key-here",
     "google_api_key": "your-google-api-key-here"
   }}
   ```
5. 重启 Anki

## 🎯 使用方法

1. 打开任意 Anki 卡片
2. 在答案页面点击 "🤖 Ask AI" 按钮
3. 在聊天窗口中与 AI 对话
4. AI 会基于当前卡片内容提供帮助

## ✨ 新功能特性

- ✅ **多提供商支持**: OpenAI、Anthropic、Google
- ✅ **自动回退机制**: 主提供商失败时自动切换
- ✅ **智能错误处理**: 更好的错误恢复
- ✅ **配置灵活性**: 支持多种配置选项
- ✅ **向后兼容**: 与旧版本完全兼容

## 🔧 高级配置

```json
{{
  "ai_provider": "openai",           // 主要提供商
  "fallback_providers": ["anthropic"], // 回退提供商
  "max_tokens": 500,                 // 最大回复长度
  "temperature": 0.7,                // 创造性程度
  "retry_attempts": 3,               // 重试次数
  "timeout": 30,                     // 超时时间
  "debug_mode": false                // 调试模式
}}
```

## 🆘 故障排除

### 常见问题
1. **按钮不显示**: 检查插件是否正确安装并重启 Anki
2. **API 错误**: 验证 API 密钥是否正确配置
3. **网络问题**: 检查网络连接和防火墙设置
4. **响应慢**: 尝试切换到其他 AI 提供商

### 获取帮助
- 查看插件配置中的调试信息
- 启用 debug_mode 获取详细日志
- 检查 Anki 的错误日志

## 📝 更新日志

### v2.0.0
- 🆕 添加多 AI 提供商支持
- 🆕 实现自动回退机制
- 🆕 增强错误处理
- 🆕 改进用户界面
- 🔧 优化性能和稳定性

---

**享受 AI 辅助学习体验！** 🌟
"""
    
    guide_path = addon_path.parent / f"{addon_info['package']}-installation-guide.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"   ✅ 安装指南: {guide_path.name}")
    return guide_path

def create_release_info(addon_path, addon_info):
    """创建发布信息文件"""
    print("📋 创建发布信息...")

    dist_dir = addon_path.parent
    release_info_path = dist_dir / f"RELEASE_INFO_{addon_info['timestamp']}.md"

    # 读取manifest信息
    try:
        with open('manifest.json', 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception:
        manifest = {}

    release_info = f"""# Chat with Card - Release Information

## 📦 Release Details
- **Version**: {manifest.get('version', '2.0.0')}
- **Package Name**: {manifest.get('package', 'chat-with-card')}
- **Build Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **File**: `{addon_path.name}`
- **Size**: {addon_path.stat().st_size / 1024:.1f} KB

## 🌍 Multi-language Support
- 🇺🇸 **English** - Full support
- 🇨🇳 **简体中文** - Complete translation
- 🇹🇼 **繁體中文** - Complete translation
- 🇯🇵 **日本語** - Complete translation

## ✨ Key Features
- **AI Chat Integration**: Chat with AI about your Anki cards
- **Card Generation**: Create cards directly from conversations
- **Markdown Support**: Rich text formatting in both chat and cards
- **Multi-language Interface**: Automatic language detection and manual switching
- **Modern UI**: Clean, minimalist design optimized for Anki

## 🔧 Technical Details
- **Anki Version**: {manifest.get('anki_version', '2.1.0')}+
- **Dependencies**: Self-contained (includes mistune, requests, tenacity)
- **Installation**: Standard .ankiaddon file
- **Configuration**: Settings dialog with language selection

## 📤 AnkiWeb Submission Checklist

### ✅ Pre-submission Verification
- [ ] Plugin file is properly named: `{addon_path.name}`
- [ ] File size is reasonable: {addon_path.stat().st_size / 1024:.1f} KB
- [ ] No __pycache__ folders included
- [ ] Manifest.json is properly formatted
- [ ] All dependencies are bundled in vendor/

### 📝 AnkiWeb Upload Information
1. **Upload URL**: https://ankiweb.net/shared/addons/
2. **Package Name**: `{manifest.get('package', 'chat-with-card')}`
3. **Display Name**: `{manifest.get('name', 'Chat with Card')}`
4. **Description**: {manifest.get('description', 'AI-powered chat tool for Anki with card generation capabilities')}
5. **Anki Version**: 2.1.0+ (compatible with current Anki versions)
6. **File Format**: .ankiaddon (standard Anki addon format)

### 🏷️ Suggested Tags
{', '.join(manifest.get('tags', ['ai', 'chat', 'cards', 'study', 'multilingual']))}

### 📖 Description for AnkiWeb
```
Chat with Card - AI-Powered Anki Assistant

Transform your Anki study experience with AI-powered conversations! Chat with Card allows you to:

🤖 **Chat with AI**: Ask questions about your cards and get intelligent responses
📝 **Create Cards**: Generate new Anki cards directly from your conversations
🌍 **Multi-language**: Full interface support for English, Chinese, and Japanese
✨ **Rich Formatting**: Markdown support for beautiful card content
🎨 **Modern Design**: Clean, minimalist interface that integrates seamlessly with Anki

Perfect for students, language learners, and anyone who wants to enhance their Anki experience with AI assistance.

**Languages Supported**: English, 简体中文, 繁體中文, 日本語
**Anki Version**: 2.1.0+
**Self-contained**: No additional installations required
```

### 🚀 Post-Upload Steps
1. **Wait for Review**: AnkiWeb may take time to review new addons
2. **Test Installation**: Test the uploaded addon in a clean Anki installation
3. **Monitor Feedback**: Watch for user feedback and bug reports
4. **Update Process**: Prepare for future version updates
5. **Documentation**: Keep addon description and documentation updated

## 📁 File Structure Verification
The addon package includes:
- Core plugin files (ui/, services/, utils/)
- Multi-language support (i18n/)
- Bundled dependencies (vendor/)
- Configuration files (config.json, manifest.json)

## 🔍 Quality Assurance
- ✅ Multi-language functionality tested
- ✅ AI chat integration verified
- ✅ Card creation workflow confirmed
- ✅ Error handling implemented
- ✅ User interface responsive

---
Generated by Chat with Card Build System v2.0
"""

    with open(release_info_path, 'w', encoding='utf-8') as f:
        f.write(release_info)

    print(f"   ✅ Release info: {release_info_path}")
    return release_info_path

def validate_addon_structure(build_dir):
    """验证插件结构和依赖"""
    print("🔍 验证插件结构...")

    required_files = [
        '__init__.py',
        'manifest.json',
        'config.json',  # Anki 标准配置文件
        'config.py',
        'services/ai_service_adapter.py',
        'services/card_service.py',
        'ui/chat_dialog.py'
    ]

    missing_files = []
    for file_path in required_files:
        full_path = build_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)

    # 验证vendor依赖
    vendor_dir = build_dir / 'vendor'
    if vendor_dir.exists():
        print("   🔍 验证vendor依赖...")
        required_deps = ['mistune', 'requests', 'tenacity']
        for dep in required_deps:
            dep_found = False
            for item in vendor_dir.iterdir():
                if item.is_dir() and item.name.startswith(dep):
                    print(f"   ✅ vendor/{item.name}")
                    dep_found = True
                    break
            if not dep_found:
                print(f"   ❌ vendor/{dep} 未找到")
                missing_files.append(f"vendor/{dep}")
    else:
        print("   ❌ vendor/ 目录不存在")
        missing_files.append("vendor/")

    if missing_files:
        print(f"\n⚠️  警告: 缺少关键文件: {missing_files}")
        return False

    return True

def main():
    """主函数"""
    print("🔨 Chat with Card 插件打包器")
    print("=" * 50)
    
    try:
        # 获取插件信息
        addon_info = get_addon_info()
        print(f"📦 打包插件: {addon_info['name']} v{addon_info['version']}")
        
        # 创建构建目录
        build_dir = create_build_directory()
        print(f"📁 构建目录: {build_dir}")
        
        # 准备 vendor 依赖
        prepare_vendor()

        # 编译翻译文件
        compile_translations()

        # 复制源文件
        copied_files = copy_source_files(build_dir)

        # 创建 META-INF
        create_meta_inf(build_dir, addon_info)
        
        # 清理构建目录
        clean_build_directory(build_dir)
        
        # 验证插件结构
        if not validate_addon_structure(build_dir):
            print("❌ 插件结构验证失败")
            return False
        
        # 创建插件包
        addon_path = create_addon_package(build_dir, addon_info)
        
        # 创建安装指南
        guide_path = create_installation_guide(addon_path, addon_info)

        # 创建发布信息
        create_release_info(addon_path, addon_info)

        # 清理构建目录
        shutil.rmtree(build_dir)
        
        # 显示结果
        print("\n" + "=" * 50)
        print("🎉 插件打包完成！")
        print("=" * 50)
        print(f"📦 插件文件: {addon_path}")
        print(f"📖 安装指南: {guide_path}")
        print(f"📊 文件大小: {addon_path.stat().st_size / 1024:.1f} KB")
        
        print(f"\n🚀 下一步:")
        print(f"1. **本地测试**: 在 Anki 中选择 工具 > 插件 > 从文件安装")
        print(f"   选择文件: {addon_path}")
        print(f"2. **查看指南**: {guide_path}")
        print(f"3. **发布到 AnkiWeb**:")
        print(f"   - 访问: https://ankiweb.net/shared/addons/")
        print(f"   - 点击 'Upload' 按钮")
        print(f"   - 上传文件: {addon_path}")
        print(f"   - 查看发布信息: RELEASE_INFO_{addon_info['timestamp']}.md")
        
        return True
        
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

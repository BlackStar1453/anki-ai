#!/usr/bin/env python3
"""
发布前检查脚本
验证插件包是否符合AnkiWeb要求
"""

import os
import sys
import zipfile
import json
from pathlib import Path

def check_ankiaddon_file(addon_path):
    """检查.ankiaddon文件"""
    print(f"🔍 检查插件文件: {addon_path}")
    
    if not addon_path.exists():
        print(f"❌ 文件不存在: {addon_path}")
        return False
    
    if not addon_path.name.endswith('.ankiaddon'):
        print(f"❌ 文件扩展名错误，应该是.ankiaddon")
        return False
    
    print(f"✅ 文件存在: {addon_path.name}")
    print(f"📊 文件大小: {addon_path.stat().st_size / 1024:.1f} KB")
    
    return True

def check_zip_structure(addon_path):
    """检查ZIP文件结构"""
    print(f"\n📁 检查ZIP文件结构...")
    
    try:
        with zipfile.ZipFile(addon_path, 'r') as zf:
            file_list = zf.namelist()
            
            # 检查必需文件
            required_files = ['__init__.py', 'manifest.json']
            missing_files = []
            
            for required in required_files:
                if required not in file_list:
                    missing_files.append(required)
            
            if missing_files:
                print(f"❌ 缺少必需文件: {missing_files}")
                return False
            
            # 检查是否有__pycache__文件夹
            pycache_files = [f for f in file_list if '__pycache__' in f]
            if pycache_files:
                print(f"❌ 包含__pycache__文件夹: {pycache_files[:3]}...")
                return False
            
            # 检查顶级文件夹结构（根据AnkiWeb要求，不应该有顶级插件文件夹）
            top_level_dirs = set()
            for f in file_list:
                if '/' in f:
                    top_dir = f.split('/')[0]
                    # 允许的顶级目录
                    if top_dir not in ['ui', 'services', 'utils', 'i18n', 'vendor']:
                        top_level_dirs.add(top_dir)

            if top_level_dirs:
                print(f"⚠️  发现可能的问题目录: {top_level_dirs}")
                print("   注意：AnkiWeb要求ZIP文件不包含顶级插件文件夹")
            
            print(f"✅ ZIP结构检查通过")
            print(f"📄 包含文件数: {len(file_list)}")
            
            return True
            
    except Exception as e:
        print(f"❌ ZIP文件检查失败: {e}")
        return False

def check_manifest(addon_path):
    """检查manifest.json"""
    print(f"\n📋 检查manifest.json...")
    
    try:
        with zipfile.ZipFile(addon_path, 'r') as zf:
            manifest_data = zf.read('manifest.json')
            manifest = json.loads(manifest_data.decode('utf-8'))
            
            required_keys = ['package', 'name']
            missing_keys = []
            
            for key in required_keys:
                if key not in manifest:
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"❌ manifest.json缺少必需字段: {missing_keys}")
                return False
            
            print(f"✅ Package: {manifest.get('package')}")
            print(f"✅ Name: {manifest.get('name')}")
            print(f"✅ Version: {manifest.get('version', 'N/A')}")
            print(f"✅ Description: {manifest.get('description', 'N/A')[:50]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ manifest.json检查失败: {e}")
        return False

def check_dependencies(addon_path):
    """检查依赖"""
    print(f"\n📦 检查依赖...")
    
    try:
        with zipfile.ZipFile(addon_path, 'r') as zf:
            file_list = zf.namelist()
            
            # 检查vendor目录
            vendor_files = [f for f in file_list if f.startswith('vendor/')]
            if vendor_files:
                print(f"✅ 找到vendor目录，包含 {len(vendor_files)} 个文件")
                
                # 检查关键依赖
                deps = ['mistune', 'requests', 'tenacity']
                found_deps = []
                
                for dep in deps:
                    dep_files = [f for f in vendor_files if dep in f]
                    if dep_files:
                        found_deps.append(dep)
                
                print(f"✅ 找到依赖: {found_deps}")
                
                if len(found_deps) < len(deps):
                    missing_deps = set(deps) - set(found_deps)
                    print(f"⚠️  可能缺少依赖: {missing_deps}")
            else:
                print(f"⚠️  没有找到vendor目录")
            
            return True
            
    except Exception as e:
        print(f"❌ 依赖检查失败: {e}")
        return False

def check_i18n(addon_path):
    """检查多语言文件"""
    print(f"\n🌍 检查多语言支持...")
    
    try:
        with zipfile.ZipFile(addon_path, 'r') as zf:
            file_list = zf.namelist()
            
            # 检查i18n目录
            i18n_files = [f for f in file_list if f.startswith('i18n/')]
            if i18n_files:
                print(f"✅ 找到i18n目录，包含 {len(i18n_files)} 个文件")
                
                # 检查语言文件
                languages = ['en', 'zh_CN', 'zh_TW', 'ja']
                found_langs = []
                
                for lang in languages:
                    lang_files = [f for f in i18n_files if f'/{lang}/' in f]
                    if lang_files:
                        found_langs.append(lang)
                
                print(f"✅ 支持的语言: {found_langs}")
            else:
                print(f"⚠️  没有找到i18n目录")
            
            return True
            
    except Exception as e:
        print(f"❌ 多语言检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 Chat with Card 发布前检查")
    print("=" * 50)
    
    # 查找最新的.ankiaddon文件
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ dist目录不存在，请先运行 python build_addon.py")
        return False
    
    addon_files = list(dist_dir.glob('*.ankiaddon'))
    if not addon_files:
        print("❌ 没有找到.ankiaddon文件，请先运行 python build_addon.py")
        return False
    
    # 使用最新的文件
    addon_path = max(addon_files, key=lambda p: p.stat().st_mtime)
    
    # 执行检查
    checks = [
        check_ankiaddon_file,
        check_zip_structure,
        check_manifest,
        check_dependencies,
        check_i18n
    ]
    
    results = []
    for check_func in checks:
        try:
            result = check_func(addon_path)
            results.append(result)
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results.append(False)
    
    # 显示总结
    print("\n" + "=" * 50)
    print("📊 检查结果总结")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 所有检查通过！插件已准备好发布到AnkiWeb")
        print(f"\n📤 发布步骤:")
        print(f"1. 访问: https://ankiweb.net/shared/addons/")
        print(f"2. 点击 'Upload' 按钮")
        print(f"3. 上传文件: {addon_path}")
        return True
    else:
        print(f"⚠️  {passed}/{total} 项检查通过，请修复问题后重新打包")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

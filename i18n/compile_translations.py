#!/usr/bin/env python3
"""
编译翻译文件脚本
将 .po 文件编译为 .mo 文件
"""

import os
import sys
import subprocess
from pathlib import Path

def compile_po_file(po_file_path, mo_file_path):
    """编译单个 .po 文件为 .mo 文件"""
    try:
        # 使用 msgfmt 命令编译
        result = subprocess.run([
            'msgfmt', 
            '-o', str(mo_file_path), 
            str(po_file_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Compiled: {po_file_path} -> {mo_file_path}")
            return True
        else:
            print(f"❌ Failed to compile {po_file_path}: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ msgfmt command not found. Please install gettext tools.")
        print("   On Ubuntu/Debian: sudo apt-get install gettext")
        print("   On macOS: brew install gettext")
        print("   On Windows: Install gettext from https://mlocati.github.io/articles/gettext-iconv-windows.html")
        return False
    except Exception as e:
        print(f"❌ Error compiling {po_file_path}: {e}")
        return False

def compile_all_translations():
    """编译所有翻译文件"""
    script_dir = Path(__file__).parent
    locales_dir = script_dir / 'locales'
    
    if not locales_dir.exists():
        print(f"❌ Locales directory not found: {locales_dir}")
        return False
    
    success_count = 0
    total_count = 0
    
    # 遍历所有语言目录
    for lang_dir in locales_dir.iterdir():
        if not lang_dir.is_dir():
            continue
            
        lc_messages_dir = lang_dir / 'LC_MESSAGES'
        if not lc_messages_dir.exists():
            continue
        
        # 查找 .po 文件
        po_files = list(lc_messages_dir.glob('*.po'))
        for po_file in po_files:
            total_count += 1
            mo_file = po_file.with_suffix('.mo')
            
            if compile_po_file(po_file, mo_file):
                success_count += 1
    
    print(f"\n📊 Compilation Summary:")
    print(f"   Total files: {total_count}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {total_count - success_count}")
    
    return success_count == total_count

def main():
    """主函数"""
    print("🔨 Compiling translation files...")
    print("=" * 50)
    
    if compile_all_translations():
        print("\n🎉 All translation files compiled successfully!")
        return 0
    else:
        print("\n❌ Some translation files failed to compile.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Anki AI Chat Tool 安装脚本
自动检查依赖、配置和安装状态
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step, description):
    """打印步骤"""
    print(f"\n{step}. {description}")

def check_python_version():
    """检查Python版本"""
    print_step(1, "检查Python版本")
    
    version = sys.version_info
    print(f"   当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("   ✅ Python版本符合要求 (3.7+)")
        return True
    else:
        print("   ❌ Python版本过低，需要3.7或更高版本")
        return False

def check_dependencies():
    """检查依赖库"""
    print_step(2, "检查依赖库")

    required_packages = ['requests']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}库已安装")
        except ImportError:
            print(f"   ❌ {package}库未安装")
            missing_packages.append(package)

    return len(missing_packages) == 0, missing_packages

def install_dependencies(missing_packages):
    """安装缺失的依赖库"""
    print("   正在安装缺失的依赖库...")

    try:
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package}库安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 依赖库安装失败: {e}")
        return False

def check_project_structure():
    """检查项目结构"""
    print_step(3, "检查项目结构")
    
    required_files = [
        "__init__.py",
        "config.py", 
        "manifest.json",
        "ui/__init__.py",
        "ui/chat_dialog.py",
        "ui/button_injector.py",
        "services/__init__.py",
        "services/ai_service.py",
        "services/card_service.py",
        "utils/__init__.py",
        "utils/helpers.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if not missing_files:
        print("   ✅ 所有必需文件都存在")
        return True
    else:
        print("   ❌ 缺少以下文件:")
        for file_path in missing_files:
            print(f"      - {file_path}")
        return False

def find_anki_addons_directory():
    """查找Anki插件目录"""
    print_step(4, "查找Anki插件目录")
    
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        anki_dir = home / "AppData" / "Roaming" / "Anki2" / "addons21"
    elif system == "Darwin":  # macOS
        anki_dir = home / "Library" / "Application Support" / "Anki2" / "addons21"
    else:  # Linux
        anki_dir = home / ".local" / "share" / "Anki2" / "addons21"
    
    if anki_dir.exists():
        print(f"   ✅ 找到Anki插件目录: {anki_dir}")
        return anki_dir
    else:
        print(f"   ❌ 未找到Anki插件目录: {anki_dir}")
        print("   请确保Anki已正确安装")
        return None

def check_api_key_configuration():
    """检查API密钥配置"""
    print_step(5, "检查API密钥配置")
    
    try:
        from config import Config
        config = Config.get_openai_config()
        
        if config['api_key'] == "sk-placeholder-key-here":
            print("   ⚠️  API密钥尚未配置（使用占位符）")
            print("   请按照INSTALLATION_GUIDE.md配置您的OpenAI API密钥")
            return False
        else:
            print("   ✅ API密钥已配置")
            return True
            
    except Exception as e:
        print(f"   ❌ 配置检查失败: {e}")
        return False

def run_tests():
    """运行测试"""
    print_step(6, "运行测试套件")
    
    try:
        result = subprocess.run([sys.executable, "run_tests.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("   ✅ 所有测试通过")
            return True
        else:
            print("   ❌ 部分测试失败")
            print("   详细信息请查看test_report.txt")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ 测试超时")
        return False
    except Exception as e:
        print(f"   ❌ 测试运行失败: {e}")
        return False

def main():
    """主安装流程"""
    print_header("Anki AI Chat Tool 安装检查")
    
    checks = []
    
    # 1. 检查Python版本
    checks.append(check_python_version())
    
    # 2. 检查/安装依赖库
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        if install_dependencies(missing_deps):
            checks.append(True)
        else:
            checks.append(False)
    else:
        checks.append(True)
    
    # 3. 检查项目结构
    checks.append(check_project_structure())
    
    # 4. 查找Anki目录
    anki_dir = find_anki_addons_directory()
    checks.append(anki_dir is not None)
    
    # 5. 检查API密钥
    api_key_ok = check_api_key_configuration()
    checks.append(api_key_ok)
    
    # 6. 运行测试
    if all(checks[:4]):  # 只有前4项都通过才运行测试
        checks.append(run_tests())
    else:
        print_step(6, "跳过测试（前置条件未满足）")
        checks.append(False)
    
    # 总结
    print_header("安装检查结果")
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"通过检查: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 恭喜！所有检查都通过了")
        print("您的Anki AI Chat Tool已准备就绪")
        
        if anki_dir:
            print(f"\n📁 下一步：将插件复制到Anki目录")
            print(f"   目标目录: {anki_dir}")
            print(f"   然后重启Anki并启用插件")
            
    elif passed >= 4:
        print("\n⚠️  基本安装完成，但需要配置API密钥")
        print("请按照INSTALLATION_GUIDE.md完成配置")
        
    else:
        print("\n❌ 安装检查未完全通过")
        print("请解决上述问题后重新运行此脚本")
    
    print("\n📖 详细说明请参考 INSTALLATION_GUIDE.md")
    print("🧪 AI连接测试请运行 python3 test_ai_connection.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

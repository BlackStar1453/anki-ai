#!/usr/bin/env python3
"""
依赖安装脚本
为 Anki AI Chat Tool 安装必需的依赖
"""

import sys
import subprocess
import os

def check_dependency(package_name):
    """检查依赖是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """安装包"""
    try:
        print(f"正在安装 {package_name}...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package_name
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {package_name} 安装成功")
            return True
        else:
            print(f"❌ {package_name} 安装失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {package_name} 安装超时")
        return False
    except Exception as e:
        print(f"💥 {package_name} 安装异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Anki AI Chat Tool 依赖安装器")
    print("=" * 50)
    
    # 必需的依赖
    dependencies = [
        ('litellm', 'litellm>=1.76.0'),
        ('openai', 'openai>=1.0.0'),
        ('requests', 'requests>=2.25.0'),
        ('tenacity', 'tenacity>=9.0.0')
    ]
    
    print("📋 检查依赖状态...")
    missing_deps = []
    
    for import_name, package_spec in dependencies:
        if check_dependency(import_name):
            print(f"✅ {import_name} 已安装")
        else:
            print(f"❌ {import_name} 未安装")
            missing_deps.append(package_spec)
    
    if not missing_deps:
        print("\n🎉 所有依赖都已安装！")
        return True
    
    print(f"\n📦 需要安装 {len(missing_deps)} 个依赖:")
    for dep in missing_deps:
        print(f"   - {dep}")
    
    # 询问是否安装
    try:
        response = input("\n是否现在安装这些依赖？(y/n): ").lower().strip()
        if response not in ['y', 'yes', '是']:
            print("安装已取消")
            return False
    except KeyboardInterrupt:
        print("\n安装已取消")
        return False
    
    # 安装依赖
    print("\n🚀 开始安装依赖...")
    success_count = 0
    
    for package_spec in missing_deps:
        if install_package(package_spec):
            success_count += 1
    
    # 总结
    print(f"\n📊 安装结果:")
    print(f"成功安装: {success_count}/{len(missing_deps)}")
    
    if success_count == len(missing_deps):
        print("\n🎉 所有依赖安装成功！")
        print("现在可以正常使用 Anki AI Chat Tool 了。")
        return True
    else:
        print("\n⚠️  部分依赖安装失败")
        print("请手动安装失败的依赖或检查网络连接")
        return False

def create_manual_install_guide():
    """创建手动安装指南"""
    guide = """# Anki AI Chat Tool 依赖安装指南

## 自动安装（推荐）
运行以下命令：
```bash
python install_dependencies.py
```

## 手动安装
如果自动安装失败，请手动运行以下命令：

### 必需依赖
```bash
pip install litellm>=1.76.0
pip install openai>=1.0.0
pip install requests>=2.25.0
pip install tenacity>=9.0.0
```

### 验证安装
```bash
python -c "import litellm; print('LiteLLM OK')"
python -c "import openai; print('OpenAI OK')"
```

## 常见问题

### 问题1: pip 命令不存在
**解决**: 使用 `python -m pip` 替代 `pip`

### 问题2: 权限错误
**解决**: 添加 `--user` 参数
```bash
pip install --user litellm>=1.76.0
```

### 问题3: 网络连接问题
**解决**: 使用国内镜像
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple litellm>=1.76.0
```

### 问题4: Anki 环境问题
如果在 Anki 中仍然提示 "LiteLLM library not available"：

1. 确认 Python 版本一致
2. 重启 Anki
3. 检查 Anki 使用的 Python 环境

## 验证插件功能
安装完成后：
1. 重启 Anki
2. 打开插件配置界面
3. 点击"测试连接"按钮
4. 应该显示连接成功

---
如果仍有问题，请提供详细的错误信息。
"""
    
    try:
        with open('DEPENDENCY_INSTALL_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        print("✅ 手动安装指南已创建: DEPENDENCY_INSTALL_GUIDE.md")
    except Exception as e:
        print(f"⚠️  无法创建安装指南: {e}")

if __name__ == "__main__":
    try:
        success = main()
        
        # 创建手动安装指南
        create_manual_install_guide()
        
        if success:
            print("\n🌟 依赖安装完成！现在可以使用插件了。")
        else:
            print("\n📖 请查看 DEPENDENCY_INSTALL_GUIDE.md 了解手动安装方法")
        
    except KeyboardInterrupt:
        print("\n\n安装已中断")
    except Exception as e:
        print(f"\n💥 安装过程异常: {e}")
        print("请查看 DEPENDENCY_INSTALL_GUIDE.md 了解手动安装方法")

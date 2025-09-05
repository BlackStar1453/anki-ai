"""
依赖加载器
在插件启动时加载打包的依赖
"""

import sys
import os

def load_vendor_dependencies():
    """加载 vendor 目录中的依赖"""
    addon_dir = os.path.dirname(__file__)
    vendor_dir = os.path.join(addon_dir, "vendor")
    
    if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
        sys.path.insert(0, vendor_dir)
        print(f"Added vendor directory to path: {vendor_dir}")
    
    # 验证关键依赖是否可用
    try:
        import mistune
        print("✅ Mistune loaded from vendor")
        return True
    except ImportError as e:
        print(f"❌ Failed to load Mistune: {e}")
        # 尝试加载其他依赖
        try:
            import requests
            print("✅ Requests loaded from vendor")
            return True
        except ImportError as e2:
            print(f"❌ Failed to load Requests: {e2}")
            return False

# 在模块导入时自动加载依赖
load_vendor_dependencies()

#!/bin/bash
# 测试构建流程脚本（不实际运行，仅验证配置）
# 用法: ./scripts/test-build.sh

set -e

echo "🧪 测试构建流程配置..."
echo "=================================="

# 检查必需文件
echo "📋 检查必需文件..."
required_files=(
    "manifest.json"
    "build_addon.py"
    "check_release.py"
    "__init__.py"
    "config.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
        exit 1
    fi
done

# 检查目录结构
echo "📁 检查目录结构..."
required_dirs=(
    "ui"
    "services"
    "i18n"
    "utils"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/"
    else
        echo "  ❌ $dir/ (缺失)"
        exit 1
    fi
done

# 检查Python语法
echo "🐍 检查Python语法..."
python_files=(
    "build_addon.py"
    "check_release.py"
    "__init__.py"
    "config.py"
)

for file in "${python_files[@]}"; do
    if [ -f "$file" ]; then
        if python -m py_compile "$file" 2>/dev/null; then
            echo "  ✅ $file (语法正确)"
        else
            echo "  ❌ $file (语法错误)"
            exit 1
        fi
    fi
done

# 检查manifest.json格式
echo "📋 检查manifest.json格式..."
if python -c "import json; json.load(open('manifest.json'))" 2>/dev/null; then
    echo "  ✅ manifest.json (格式正确)"
else
    echo "  ❌ manifest.json (格式错误)"
    exit 1
fi

# 检查GitHub Actions配置
echo "🔧 检查GitHub Actions配置..."
if [ -f ".github/workflows/build-and-release.yml" ]; then
    echo "  ✅ build-and-release.yml"
else
    echo "  ❌ build-and-release.yml (缺失)"
fi

if [ -f ".github/workflows/ankiweb-upload.yml" ]; then
    echo "  ✅ ankiweb-upload.yml"
else
    echo "  ❌ ankiweb-upload.yml (缺失)"
fi

# 检查脚本权限
echo "🔐 检查脚本权限..."
if [ -x "scripts/release.sh" ]; then
    echo "  ✅ scripts/release.sh (可执行)"
else
    echo "  ⚠️  scripts/release.sh (需要设置执行权限: chmod +x scripts/release.sh)"
fi

# 检查Git配置
echo "📝 检查Git配置..."
if [ -d ".git" ]; then
    echo "  ✅ Git仓库已初始化"
    
    # 检查远程仓库
    if git remote -v | grep -q "github.com"; then
        echo "  ✅ GitHub远程仓库已配置"
    else
        echo "  ⚠️  未检测到GitHub远程仓库"
    fi
else
    echo "  ⚠️  Git仓库未初始化"
fi

echo ""
echo "=================================="
echo "✅ 构建流程配置检查完成！"
echo ""
echo "🚀 可用的发布方式："
echo "1. 本地脚本: ./scripts/release.sh 2.0.0"
echo "2. Makefile: make release VERSION=2.0.0"
echo "3. 手动构建: python build_addon.py"
echo ""
echo "📋 GitHub Actions触发方式："
echo "1. 推送标签: git tag v2.0.0 && git push origin v2.0.0"
echo "2. 手动触发: 访问GitHub Actions页面"
echo ""
echo "🔍 下一步："
echo "1. 确保所有文件都已提交到Git"
echo "2. 选择一种发布方式进行测试"
echo "3. 检查生成的.ankiaddon文件"

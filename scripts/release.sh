#!/bin/bash
# Chat with Card 发布脚本
# 用法: ./scripts/release.sh [version]
# 注意: 首次使用需要设置执行权限: chmod +x scripts/release.sh

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查参数
VERSION=${1:-"2.0.0"}

print_info "开始发布 Chat with Card v$VERSION"
echo "=================================="

# 检查是否在正确的目录
if [ ! -f "manifest.json" ]; then
    print_error "未找到 manifest.json，请在项目根目录运行此脚本"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    print_warning "检测到未提交的更改"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "发布已取消"
        exit 0
    fi
fi

# 更新版本号
print_info "更新版本号到 $VERSION"
sed -i.bak "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" manifest.json

# 更新修改日期
DATE=$(date +%Y-%m-%d)
sed -i.bak "s/\"mod\": \".*\"/\"mod\": \"$DATE\"/" manifest.json

print_success "版本信息已更新"

# 运行构建
print_info "构建插件包..."
python build_addon.py

if [ $? -ne 0 ]; then
    print_error "构建失败"
    exit 1
fi

print_success "构建完成"

# 运行检查
print_info "运行发布检查..."
python check_release.py

if [ $? -ne 0 ]; then
    print_error "发布检查失败"
    exit 1
fi

print_success "发布检查通过"

# 查找生成的文件
ADDON_FILE=$(find dist -name "*.ankiaddon" -type f | head -1)
if [ -z "$ADDON_FILE" ]; then
    print_error "未找到生成的 .ankiaddon 文件"
    exit 1
fi

ADDON_NAME=$(basename "$ADDON_FILE")
FILE_SIZE=$(du -h "$ADDON_FILE" | cut -f1)

print_success "插件包已生成: $ADDON_NAME ($FILE_SIZE)"

# 提交更改（如果有的话）
if [ -n "$(git status --porcelain)" ]; then
    print_info "提交版本更新..."
    git add manifest.json
    git commit -m "Release v$VERSION"
    
    # 创建标签
    git tag -a "v$VERSION" -m "Release v$VERSION"
    
    print_success "已创建版本标签 v$VERSION"
    
    # 询问是否推送
    read -p "是否推送到远程仓库？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        git push origin "v$VERSION"
        print_success "已推送到远程仓库"
        print_info "GitHub Actions 将自动构建和发布"
    fi
fi

# 显示下一步操作
echo
echo "=================================="
print_success "发布准备完成！"
echo "=================================="
echo
print_info "生成的文件:"
echo "  📦 插件包: $ADDON_FILE"
echo "  📊 文件大小: $FILE_SIZE"
echo
print_info "下一步操作:"
echo "  1. 🔍 检查生成的文件"
echo "  2. 🌐 访问 https://ankiweb.net/shared/addons/"
echo "  3. 📤 上传 $ADDON_NAME"
echo "  4. 📋 使用 dist/RELEASE_INFO_*.md 中的信息填写表单"
echo
print_info "GitHub Actions:"
if git remote -v | grep -q "github.com"; then
    echo "  🚀 如果已推送标签，GitHub Actions 将自动构建"
    echo "  📋 查看: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"
else
    echo "  ⚠️  未检测到 GitHub 远程仓库"
fi

# 清理备份文件
rm -f manifest.json.bak

print_success "发布脚本执行完成！"

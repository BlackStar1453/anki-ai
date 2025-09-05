#!/bin/bash
# 准备 v1.0.0 发布脚本

set -e

echo "🚀 准备 Chat with Card v1.0.0 发布"
echo "=================================="

# 检查Git状态
echo "📋 检查Git状态..."
if [ -n "$(git status --porcelain)" ]; then
    echo "✅ 检测到未提交的更改，准备提交..."
else
    echo "ℹ️  工作目录干净"
fi

# 显示当前更改
echo ""
echo "📝 当前更改摘要:"
echo "- 更新UI文本：'Create Card' -> 'Save to Card'"
echo "- 更新按钮文本：'Open Chat' -> 'Chat with Card'"
echo "- 添加新的翻译文本"
echo "- 版本号设置为 v1.0.0"

# 提交更改
echo ""
echo "💾 提交更改..."
git add .
git commit -m "Prepare for v1.0.0 release

- Update UI text: 'Create Card' -> 'Save to Card'
- Update button text: 'Open Chat' -> 'Chat with Card'
- Add new translation strings for all languages
- Set version to 1.0.0
- Ready for GitHub Actions release"

echo "✅ 更改已提交"

# 创建标签
echo ""
echo "🏷️  创建版本标签 v1.0.0..."
git tag -a v1.0.0 -m "Release v1.0.0

Chat with Card - First stable release

Features:
- AI-powered chat interface with markdown support
- Direct card creation from conversations
- Multi-language support (English, 简体中文, 繁體中文, 日本語)
- Modern, minimalist UI design
- Self-contained dependencies (no external installations required)

Technical:
- Anki 2.1.0+ compatibility
- Automatic language detection
- Complete error handling and user feedback
- Optimized performance and memory usage"

echo "✅ 标签 v1.0.0 已创建"

# 显示下一步
echo ""
echo "=================================="
echo "🎉 v1.0.0 发布准备完成！"
echo "=================================="
echo ""
echo "🚀 下一步 - 选择发布方式："
echo ""
echo "方式一：推送标签触发 GitHub Actions（推荐）"
echo "  git push origin main"
echo "  git push origin v1.0.0"
echo ""
echo "方式二：手动触发 GitHub Actions"
echo "  1. 访问 GitHub 仓库的 Actions 页面"
echo "  2. 选择 'Build and Release Chat with Card'"
echo "  3. 点击 'Run workflow'"
echo "  4. 输入版本号: 1.0.0"
echo "  5. 点击 'Run workflow'"
echo ""
echo "📊 GitHub Actions 将会："
echo "  ✅ 自动构建 .ankiaddon 文件"
echo "  ✅ 运行所有检查和验证"
echo "  ✅ 创建 GitHub Release v1.0.0"
echo "  ✅ 上传构建产物和安装指南"
echo "  ✅ 生成 AnkiWeb 上传指导文档"
echo ""
echo "🌐 发布后："
echo "  📥 从 GitHub Release 下载 .ankiaddon 文件"
echo "  📤 访问 https://ankiweb.net/shared/addons/ 上传到 AnkiWeb"
echo "  📋 使用生成的模板填写插件信息"

echo ""
echo "准备就绪！请选择一种方式来触发 GitHub Actions 构建。"

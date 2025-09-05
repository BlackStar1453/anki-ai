#!/bin/bash
# 创建干净的Git历史，移除所有API密钥

set -e

echo "🔄 创建干净的Git历史..."
echo "=================================="

# 备份当前状态
echo "📋 备份当前状态..."
git branch backup-with-api-keys 2>/dev/null || echo "备份分支已存在"

# 创建一个新的孤儿分支
echo "🌱 创建新的干净分支..."
git checkout --orphan clean-main

# 添加所有当前文件（已经清理过API密钥）
echo "📁 添加所有文件..."
git add .

# 创建初始提交
echo "💾 创建初始提交..."
git commit -m "Initial commit: Chat with Card v1.0.0

Features:
- 🤖 AI-powered chat interface with markdown support
- 📝 Direct card creation from conversations  
- 🌍 Multi-language support (English, 简体中文, 繁體中文, 日本語)
- 🎨 Modern, minimalist UI design
- 📦 Self-contained dependencies (no external installations required)
- 🚀 GitHub Actions CI/CD pipeline
- 🔧 Complete build and release automation

Technical:
- Anki 2.1.0+ compatibility
- Automatic language detection with manual switching
- Complete error handling and user feedback
- Optimized performance and memory usage
- AnkiWeb-ready packaging"

# 创建v1.0.0标签
echo "🏷️  创建v1.0.0标签..."
git tag -a v1.0.0 -m "Release v1.0.0

Chat with Card - First stable release

This is a clean release without any sensitive information in the Git history.

Features:
- AI-powered chat interface
- Card generation from conversations
- Multi-language support
- Modern UI design
- Self-contained dependencies
- GitHub Actions automation"

# 删除旧的main分支并重命名
echo "🔄 替换main分支..."
git branch -D main 2>/dev/null || echo "旧main分支不存在"
git branch -m clean-main main

echo ""
echo "=================================="
echo "✅ 干净的Git历史创建完成！"
echo "=================================="
echo ""
echo "📋 新历史摘要："
echo "- 创建了全新的Git历史"
echo "- 移除了所有包含API密钥的提交"
echo "- 保留了所有当前文件和功能"
echo "- 创建了v1.0.0标签"
echo ""
echo "🚀 现在可以安全推送到GitHub："
echo "git push origin main --force"
echo "git push origin v1.0.0 --force"
echo ""
echo "⚠️  注意：这会完全重写远程仓库历史"
echo "如果其他人已经克隆了仓库，他们需要重新克隆"

#!/bin/bash
# 清理Git历史中的API密钥

set -e

echo "🔒 清理Git历史中的API密钥..."
echo "=================================="

# 备份当前分支
echo "📋 创建备份分支..."
git branch backup-before-cleanup 2>/dev/null || echo "备份分支已存在"

# 使用git filter-branch清理API密钥
echo "🧹 清理API密钥..."

# 要替换的API密钥模式
API_KEY_PATTERN="your-openai-api-key-here"
REPLACEMENT="your-openai-api-key-here"

# 清理所有文件中的API密钥
git filter-branch --force --index-filter '
    git ls-files -z | xargs -0 -I {} sh -c "
        if git show :\"{}\" 2>/dev/null | grep -q \"your-openai-api-key-here\"; then
            git show :\"{}\" | sed \"s/your-openai-api-key-here/your-openai-api-key-here/g\" | git hash-object -w --stdin | xargs git update-index --add --cacheinfo 100644
        fi
    "
' --tag-name-filter cat -- --all

echo "✅ API密钥清理完成"

# 清理引用
echo "🧹 清理引用..."
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# 清理reflog
echo "🧹 清理reflog..."
git reflog expire --expire=now --all

# 垃圾回收
echo "🧹 垃圾回收..."
git gc --prune=now --aggressive

echo ""
echo "=================================="
echo "✅ Git历史清理完成！"
echo "=================================="
echo ""
echo "📋 清理摘要："
echo "- 已从所有提交中移除API密钥"
echo "- 已清理引用和reflog"
echo "- 已执行垃圾回收"
echo ""
echo "🚀 现在可以安全推送到GitHub："
echo "git push origin main --force"
echo ""
echo "⚠️  注意：这是强制推送，会重写远程历史"
echo "如果其他人已经克隆了仓库，他们需要重新克隆"

# Chat with Card - Makefile
# 简化常用开发和发布命令

.PHONY: help build check test clean release install-deps

# 默认目标
help:
	@echo "Chat with Card - 可用命令:"
	@echo ""
	@echo "开发命令:"
	@echo "  make install-deps  - 安装开发依赖"
	@echo "  make test          - 运行测试"
	@echo "  make build         - 构建插件包"
	@echo "  make check         - 运行发布检查"
	@echo "  make clean         - 清理构建文件"
	@echo ""
	@echo "发布命令:"
	@echo "  make release VERSION=2.0.0  - 完整发布流程"
	@echo "  make quick-build             - 快速构建（开发用）"
	@echo ""
	@echo "工具命令:"
	@echo "  make setup         - 初始化开发环境"
	@echo "  make lint          - 代码检查"
	@echo "  make format        - 代码格式化"

# 安装开发依赖
install-deps:
	@echo "📦 安装开发依赖..."
	pip install --upgrade pip
	pip install requests mistune tenacity
	@echo "✅ 依赖安装完成"

# 运行测试
test:
	@echo "🧪 运行测试..."
	@if [ -f "test_i18n.py" ]; then \
		python test_i18n.py; \
	else \
		echo "⚠️  未找到测试文件"; \
	fi

# 构建插件包
build:
	@echo "🔨 构建插件包..."
	python build_addon.py
	@echo "✅ 构建完成"

# 运行发布检查
check:
	@echo "🔍 运行发布检查..."
	python check_release.py
	@echo "✅ 检查完成"

# 快速构建（跳过一些检查，用于开发）
quick-build:
	@echo "⚡ 快速构建..."
	python build_addon.py
	@echo "✅ 快速构建完成"

# 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf vendor/
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ 清理完成"

# 完整发布流程
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ 请指定版本号: make release VERSION=2.0.0"; \
		exit 1; \
	fi
	@echo "🚀 开始发布 v$(VERSION)..."
	@echo "=================================="
	
	# 检查Git状态
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  检测到未提交的更改"; \
		read -p "是否继续？(y/N): " confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "发布已取消"; \
			exit 0; \
		fi; \
	fi
	
	# 更新版本
	@echo "📝 更新版本号..."
	sed -i.bak 's/"version": "[^"]*"/"version": "$(VERSION)"/' manifest.json
	sed -i.bak 's/"mod": "[^"]*"/"mod": "'$$(date +%Y-%m-%d)'"/' manifest.json
	rm -f manifest.json.bak
	
	# 构建和检查
	$(MAKE) build
	$(MAKE) check
	
	# Git操作
	@echo "📋 提交版本更新..."
	git add manifest.json
	git commit -m "Release v$(VERSION)" || true
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	
	@echo "✅ 发布准备完成！"
	@echo "=================================="
	@echo "下一步："
	@echo "1. 推送标签: git push origin v$(VERSION)"
	@echo "2. GitHub Actions 将自动构建和发布"
	@echo "3. 或访问 https://ankiweb.net/shared/addons/ 手动上传"

# 初始化开发环境
setup:
	@echo "🔧 初始化开发环境..."
	$(MAKE) install-deps
	@if [ ! -d ".git" ]; then \
		echo "📋 初始化Git仓库..."; \
		git init; \
		git add .; \
		git commit -m "Initial commit"; \
	fi
	@echo "✅ 开发环境设置完成"

# 代码检查（如果有工具的话）
lint:
	@echo "🔍 代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 --max-line-length=100 --ignore=E501,W503 .; \
	else \
		echo "⚠️  flake8 未安装，跳过代码检查"; \
	fi

# 代码格式化（如果有工具的话）
format:
	@echo "🎨 代码格式化..."
	@if command -v black >/dev/null 2>&1; then \
		black --line-length=100 .; \
	else \
		echo "⚠️  black 未安装，跳过代码格式化"; \
	fi

# 显示项目状态
status:
	@echo "📊 项目状态:"
	@echo "=================================="
	@if [ -f "manifest.json" ]; then \
		echo "📦 当前版本: $$(grep '"version"' manifest.json | sed 's/.*": "\([^"]*\)".*/\1/')"; \
	fi
	@if [ -d "dist" ]; then \
		echo "📁 构建文件: $$(ls -1 dist/ | wc -l) 个文件"; \
		echo "📄 最新构建: $$(ls -t dist/*.ankiaddon 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo '无')"; \
	fi
	@if command -v git >/dev/null 2>&1 && [ -d ".git" ]; then \
		echo "🏷️  Git标签: $$(git tag --sort=-version:refname | head -1 || echo '无')"; \
		echo "📝 未提交更改: $$(git status --porcelain | wc -l) 个文件"; \
	fi

# 开发服务器（如果需要的话）
dev:
	@echo "🔧 开发模式..."
	@echo "监控文件变化并自动重建..."
	@while true; do \
		$(MAKE) quick-build; \
		echo "⏳ 等待文件变化... (Ctrl+C 退出)"; \
		sleep 5; \
	done

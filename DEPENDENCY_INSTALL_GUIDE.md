# 🔧 Anki AI Chat Tool 依赖安装指南

## 问题说明
如果您看到 "LiteLLM library not available" 错误，这是因为插件需要额外的 Python 库。

## 解决方案

### 方法1：使用 pip 安装（推荐）
打开终端/命令提示符，运行：

```bash
pip install litellm>=1.76.0 openai>=1.0.0
```

### 方法2：使用 Anki 的 Python 环境
如果方法1不工作，尝试：

```bash
# macOS/Linux
python3 -m pip install litellm>=1.76.0 openai>=1.0.0

# Windows
python -m pip install litellm>=1.76.0 openai>=1.0.0
```

### 方法3：针对 Anki 特定环境
如果您使用的是 Anki 的独立安装：

```bash
# 找到 Anki 的 Python 路径
# 通常在 Anki 安装目录下
/path/to/anki/python -m pip install litellm>=1.76.0 openai>=1.0.0
```

## 验证安装
安装完成后：
1. 重启 Anki
2. 重新加载插件
3. 测试配置界面的"测试连接"功能

## 如果仍有问题
1. 确保网络连接正常
2. 检查 Python 版本（需要 3.8+）
3. 尝试使用管理员权限安装
4. 考虑使用虚拟环境

## 联系支持
如果按照上述步骤仍无法解决，请提供：
- Anki 版本信息
- Python 版本
- 操作系统信息
- 完整的错误信息

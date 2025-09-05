# Anki AI Chat Tool - 安装配置指南

## 📋 安装前准备

### 1. 系统要求
- Anki 2.1.45 或更高版本
- Python 3.7 或更高版本
- 稳定的网络连接

### 2. 获取OpenAI API密钥
1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册或登录账户
3. 进入 [API Keys页面](https://platform.openai.com/api-keys)
4. 点击"Create new secret key"创建新密钥
5. 复制并保存密钥（格式类似：`sk-...`）

⚠️ **重要提示**: 
- API密钥只显示一次，请妥善保存
- 使用API会产生费用，请查看OpenAI定价
- 建议设置使用限额以控制费用

## 🚀 安装步骤

### 步骤1: 安装依赖
```bash
# 在终端中运行
pip install openai
```

### 步骤2: 下载插件
1. 下载完整的插件文件夹
2. 确保包含以下文件结构：
```
anki-ai-chat/
├── __init__.py
├── config.py
├── manifest.json
├── ui/
├── services/
└── utils/
```

### 步骤3: 安装到Anki
1. 打开Anki
2. 选择 工具 → 插件 → 获取插件
3. 或者直接将插件文件夹复制到Anki插件目录：
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **macOS**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`

### 步骤4: 配置API密钥

#### 方法1: 通过Anki插件配置（推荐）
1. 重启Anki
2. 选择 工具 → 插件
3. 找到"Anki AI Chat Tool"
4. 点击"配置"按钮
5. 修改配置：
```json
{
  "openai_api_key": "sk-your-actual-api-key-here",
  "openai_model": "gpt-3.5-turbo",
  "max_tokens": 500,
  "temperature": 0.7
}
```

#### 方法2: 直接修改配置文件
1. 打开插件目录中的 `config.py` 文件
2. 找到 `DEFAULT_CONFIG` 部分
3. 将 `"openai_api_key": "sk-placeholder-key-here"` 
   替换为 `"openai_api_key": "sk-your-actual-api-key-here"`

### 步骤5: 验证安装
1. 在插件目录中运行测试脚本：
```bash
python3 test_openai_connection.py
```

2. 如果看到 "🎉 所有测试通过！" 说明安装成功

## 🎯 使用方法

### 基本使用流程
1. 在Anki中开始复习卡片
2. 查看卡片答案
3. 点击答案下方的 "🤖 Ask AI" 按钮
4. 在弹出的聊天窗口中输入问题
5. 查看AI回复
6. 可选：点击"Save to Card"保存有用的对话

### 使用技巧
- **解释概念**: "Can you explain this in simpler terms?"
- **举例说明**: "Can you give me some examples?"
- **记忆技巧**: "How can I remember this better?"
- **相关知识**: "What else should I know about this topic?"
- **练习题目**: "Can you give me a practice question?"

## ⚙️ 高级配置

### 模型选择
- `gpt-3.5-turbo`: 快速、经济（推荐）
- `gpt-4`: 更智能但更昂贵

### 参数调整
- `max_tokens`: 控制回复长度（100-2000）
- `temperature`: 控制创造性（0.0-1.0）
  - 0.0: 更确定性的回答
  - 1.0: 更有创造性的回答

### 界面定制
```json
{
  "chat_window_width": 800,
  "chat_window_height": 600,
  "conversation_separator": "<hr><h3>💬 AI Chat History</h3>"
}
```

## 🔧 故障排除

### 常见问题

**Q: 按钮没有出现**
- 确保插件已启用并重启Anki
- 检查是否在答案显示界面
- 查看Anki控制台是否有错误信息

**Q: AI不回复或显示错误**
- 检查API密钥是否正确
- 确认网络连接正常
- 检查OpenAI账户余额
- 运行 `python3 test_openai_connection.py` 诊断

**Q: 聊天窗口无法打开**
- 检查PyQt是否正确安装
- 重启Anki
- 查看错误日志

**Q: 对话保存失败**
- 确保当前卡片支持编辑
- 检查卡片模板格式
- 尝试手动刷新卡片

### 调试模式
启用调试模式获取更多信息：
```json
{
  "debug_mode": true
}
```

### 日志查看
- Anki控制台：工具 → 调试控制台
- 插件日志：查看Anki日志文件

## 💰 费用说明

### OpenAI API定价（参考）
- GPT-3.5-turbo: ~$0.002/1K tokens
- GPT-4: ~$0.03/1K tokens

### 费用估算
- 平均每次对话：50-200 tokens
- 每日使用20次：约$0.01-0.05（GPT-3.5）
- 建议设置月度使用限额

## 🔒 隐私安全

### 数据处理
- 卡片内容会发送到OpenAI服务器
- 不会永久存储您的数据
- 建议避免在敏感内容卡片上使用

### 安全建议
- 定期更换API密钥
- 监控API使用情况
- 不要分享您的API密钥

## 📞 支持与反馈

如果遇到问题：
1. 查看本指南的故障排除部分
2. 运行测试脚本诊断问题
3. 查看项目文档和错误日志
4. 提交问题报告

---

**祝您使用愉快！🎉**

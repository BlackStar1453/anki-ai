# Anki AI Chat Tool

一个为Anki卡片提供AI聊天功能的插件，使用OpenAI API帮助用户更好地理解和学习卡片内容。

## 功能特点

- 🤖 **AI对话**: 与AI就当前卡片内容进行对话
- 💬 **智能问答**: 询问解释、举例、记忆技巧等
- 💾 **对话保存**: 将有用的对话保存到卡片中
- 🎨 **友好界面**: 简洁直观的聊天窗口
- 🔒 **安全可靠**: 完善的错误处理和输入验证

## 安装要求

- Anki 2.1.45+
- Python 3.7+
- OpenAI API密钥

## 安装步骤

### 1. 安装依赖
```bash
pip install openai
```

### 2. 安装插件
1. 下载插件文件到Anki插件目录
2. 重启Anki
3. 在插件管理中启用"Anki AI Chat Tool"

### 3. 配置API密钥
1. 获取OpenAI API密钥 (https://platform.openai.com/api-keys)
2. 在插件配置中替换占位符密钥：
   ```json
   {
     "openai_api_key": "your-actual-api-key-here",
     "openai_model": "gpt-3.5-turbo",
     "max_tokens": 500,
     "temperature": 0.7
   }
   ```

## 使用方法

### 1. 基本使用
1. 在Anki中复习卡片
2. 查看答案后，点击"🤖 Ask AI"按钮
3. 在弹出的聊天窗口中输入问题
4. AI会基于当前卡片内容回答问题

### 2. 常见用法示例

**请求解释**:
- "Can you explain this concept in simpler terms?"
- "What are some real-world examples of this?"

**记忆技巧**:
- "How can I better remember this information?"
- "What's a good mnemonic for this?"

**深入学习**:
- "What are the related concepts I should know?"
- "Can you give me practice questions about this?"

### 3. 保存对话
- 点击"Save to Card"将有用的对话保存到卡片
- 对话会添加到卡片背面，标记为"AI Chat History"

## 配置选项

### OpenAI设置
- `openai_api_key`: OpenAI API密钥
- `openai_model`: 使用的模型 (推荐: gpt-3.5-turbo)
- `max_tokens`: 最大回复长度 (默认: 500)
- `temperature`: 创造性程度 (0-1, 默认: 0.7)

### 界面设置
- `chat_window_width`: 聊天窗口宽度 (默认: 600)
- `chat_window_height`: 聊天窗口高度 (默认: 400)
- `save_conversations`: 是否允许保存对话 (默认: true)

### 其他设置
- `debug_mode`: 调试模式 (默认: false)

## 开发信息

### 项目结构
```
anki-ai-chat/
├── __init__.py              # 插件入口
├── config.py               # 配置管理
├── manifest.json           # 插件清单
├── ui/                     # 用户界面
│   ├── chat_dialog.py      # 聊天窗口
│   └── button_injector.py  # 按钮注入
├── services/               # 核心服务
│   ├── openai_service.py   # OpenAI API
│   └── card_service.py     # 卡片操作
└── utils/                  # 工具函数
    └── helpers.py
```

### 运行测试
```bash
python3 run_tests.py
```

### 测试覆盖
- 47个测试用例
- 100%测试通过率
- 覆盖所有核心功能

## 故障排除

### 常见问题

**Q: 按钮没有出现**
A: 检查插件是否正确安装并启用，重启Anki后再试

**Q: AI不回复**
A: 检查API密钥是否正确配置，网络连接是否正常

**Q: 对话保存失败**
A: 确保当前有打开的卡片，检查卡片格式是否支持

**Q: 界面显示异常**
A: 检查PyQt版本兼容性，尝试重启Anki

### 错误日志
插件会记录错误信息到Anki日志中，可以通过以下方式查看：
- 启用调试模式: `"debug_mode": true`
- 查看Anki控制台输出

## 隐私和安全

- 卡片内容会发送到OpenAI进行处理
- 不会存储或记录用户数据
- 建议不要在敏感内容卡片上使用
- API密钥仅存储在本地配置中

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交问题报告和功能请求！

## 更新日志

### v1.0.0 (2025-08-26)
- 初始版本发布
- 基础AI聊天功能
- 对话保存功能
- 完整测试覆盖

## 支持

如果遇到问题或需要帮助，请：
1. 查看故障排除部分
2. 检查错误日志
3. 提交问题报告

---

**注意**: 使用本插件需要OpenAI API密钥，可能产生API调用费用。请合理使用。

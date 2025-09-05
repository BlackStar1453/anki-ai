# 🚀 Anki AI Chat Tool v2.0 - 最终安装指南

## 📦 修复完成的问题

### ✅ 已解决的问题
1. **"No module named 'services'"** - 导入路径问题已修复
2. **配置保存错误** - 插件模块名识别问题已修复  
3. **"LiteLLM library not available"** - 依赖检查和安装已完善

### 🔧 技术修复详情
- 统一使用绝对导入替代相对导入
- 修复包初始化文件中的导入问题
- 改进配置保存时的模块名识别逻辑
- 增强依赖检查和错误提示

## 📋 安装步骤

### 第一步：安装依赖（重要！）

**选项A：自动安装（推荐）**
```bash
python install_dependencies.py
```

**选项B：手动安装**
```bash
pip install litellm>=1.76.0
pip install openai>=1.0.0
pip install requests>=2.25.0
pip install tenacity>=9.0.0
```

**验证依赖安装**
```bash
python -c "import litellm; print('✅ LiteLLM OK')"
python -c "import openai; print('✅ OpenAI OK')"
```

### 第二步：安装插件

1. **卸载旧版本**
   - 打开 Anki
   - 工具 → 插件
   - 选择旧的 "Anki AI Chat Tool"
   - 点击 "删除"

2. **安装新版本**
   - 使用文件：`anki-ai-chat-v2.0.0-20250904_105628.ankiaddon`
   - 工具 → 插件 → 从文件安装
   - 选择插件文件
   - **重启 Anki**

### 第三步：配置插件

1. **打开配置界面**
   - 工具 → 插件
   - 选择 "Anki AI Chat Tool"
   - 点击 "配置"

2. **设置 API 密钥**
   - OpenAI API 密钥已预设，可直接使用
   - 如需自定义，请输入您的 API 密钥

3. **测试连接**
   - 点击 "测试连接" 按钮
   - 应该显示 "✅ 连接成功"

### 第四步：使用插件

1. **打开任意卡片**
2. **在答案页面查找 "🤖 Ask AI" 按钮**
3. **点击按钮开始 AI 聊天**

## 🔍 故障排除

### 问题1：依赖安装失败
**症状**：pip 安装报错
**解决**：
```bash
# 使用用户安装
pip install --user litellm>=1.76.0

# 或使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple litellm>=1.76.0
```

### 问题2：配置无法保存
**症状**：点击保存后提示路径错误
**解决**：
1. 确保插件正确安装在 Anki 插件目录
2. 重启 Anki
3. 检查插件是否在插件列表中显示

### 问题3：测试连接失败
**症状**：点击测试连接显示 "LiteLLM library not available"
**解决**：
1. 确认依赖已安装：`python -c "import litellm"`
2. 重启 Anki
3. 检查 Anki 使用的 Python 环境是否与安装依赖的环境一致

### 问题4：Ask AI 按钮不显示
**症状**：在卡片中看不到按钮
**解决**：
1. 确保在答案页面（不是问题页面）
2. 重启 Anki
3. 检查插件是否启用

### 问题5：点击按钮无反应
**症状**：按钮存在但点击无效果
**解决**：
1. 检查 Anki 调试控制台是否有错误信息
2. 确认插件配置正确
3. 重新安装插件

## 📞 获取支持

### 收集诊断信息
如果问题仍然存在，请提供：

1. **Anki 版本**：帮助 → 关于 Anki
2. **Python 版本**：`python --version`
3. **依赖状态**：运行 `python install_dependencies.py`
4. **错误信息**：Anki 调试控制台的完整错误

### 常见错误代码含义
- **"No module named 'services'"** → 导入路径问题（已修复）
- **"LiteLLM library not available"** → 依赖未安装
- **"保存配置时发生错误"** → 插件模块识别问题（已修复）
- **"AI服务暂时不可用"** → API 密钥或网络问题

## ✅ 成功标志

插件正常工作的标志：
- ✅ 配置界面可以正常打开
- ✅ API 密钥可以保存
- ✅ 测试连接显示成功
- ✅ Ask AI 按钮在卡片中显示
- ✅ 点击按钮可以打开聊天窗口
- ✅ AI 可以正常回复

## 🎯 版本信息

- **插件版本**：v2.0.0
- **插件文件**：`anki-ai-chat-v2.0.0-20250904_105628.ankiaddon`
- **文件大小**：29.7 KB
- **修复日期**：2025-09-04
- **状态**：生产就绪 ✅

---

**如果按照本指南操作后插件仍有问题，请提供详细的错误信息和系统环境信息。**

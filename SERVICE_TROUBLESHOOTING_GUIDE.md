# 🔧 AI 服务故障排除指南

## 问题描述
如果您遇到以下问题：
- 点击 "Ask AI" 按钮后显示 "AI服务暂时不可用: All providers failed"
- 插件配置界面中的"测试连接"功能无法使用
- 服务集成不正确

## 🚀 快速解决方案

### 第一步：快速测试
运行快速测试脚本来确定问题：
```bash
python quick_service_test.py
```

**如果测试通过**：
- 问题可能在 Anki 集成层面
- 重启 Anki 并重新测试插件

**如果测试失败**：
- 继续执行下面的修复步骤

### 第二步：自动修复
运行综合修复脚本：
```bash
python comprehensive_service_fix.py
```

这个脚本会：
- 检查所有依赖
- 修复配置问题
- 诊断服务状态
- 运行测试验证

### 第三步：手动诊断
如果自动修复失败，运行详细诊断：
```bash
python diagnose_service_integration.py
```

查看诊断报告，根据失败的测试项目进行针对性修复。

## 🔍 详细故障排除

### 常见问题 1：依赖缺失
**症状**：导入错误，LiteLLM 不可用
**解决**：
```bash
pip install litellm openai requests
```

### 常见问题 2：配置问题
**症状**：API 密钥无效，配置加载失败
**解决**：
1. 检查 `config.json` 文件是否存在
2. 运行修复脚本：
```bash
python fix_service_integration.py
```

### 常见问题 3：网络问题
**症状**：API 调用超时，连接失败
**解决**：
1. 检查网络连接
2. 检查防火墙设置
3. 验证 API 密钥权限

### 常见问题 4：环境变量问题
**症状**：API 密钥未正确设置
**解决**：
手动设置环境变量：
```python
import os
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'
```

## 📋 测试脚本说明

### 1. quick_service_test.py
**用途**：快速验证服务是否正常
**运行时间**：1-2 分钟
**适用场景**：初步检查问题

### 2. diagnose_service_integration.py
**用途**：详细诊断所有组件
**运行时间**：3-5 分钟
**适用场景**：深入分析问题

### 3. fix_service_integration.py
**用途**：自动修复常见问题
**运行时间**：2-3 分钟
**适用场景**：配置和环境修复

### 4. comprehensive_service_fix.py
**用途**：一键诊断和修复
**运行时间**：5-10 分钟
**适用场景**：全面解决问题

## 🛠️ 手动修复步骤

### 步骤 1：检查配置文件
确保 `config.json` 包含正确的 API 密钥：
```json
{
  "ai_provider": "openai",
  "openai_api_key": "your-openai-api-key-here",
  "use_unified_service": true
}
```

### 步骤 2：验证依赖安装
```bash
python -c "import litellm; print('LiteLLM OK')"
python -c "import openai; print('OpenAI OK')"
```

### 步骤 3：测试基本功能
```python
from services.ai_service_adapter import AIServiceAdapter
adapter = AIServiceAdapter()
response = adapter.get_response([{"role": "user", "content": "Hello"}])
print(response)
```

### 步骤 4：检查环境变量
```python
import os
print("OPENAI_API_KEY:", os.environ.get('OPENAI_API_KEY', 'Not set'))
```

## 🔄 重新打包和安装

如果修复成功，重新打包插件：

### 1. 重新打包
```bash
python build_addon.py
```

### 2. 重新安装
1. 在 Anki 中卸载旧版本插件
2. 安装新生成的 `.ankiaddon` 文件
3. 重启 Anki

### 3. 验证安装
1. 工具 → 插件 → 确认插件已安装
2. 点击"配置"按钮测试配置界面
3. 打开卡片测试 "Ask AI" 按钮

## 📞 获取帮助

### 收集诊断信息
如果问题仍然存在，请收集以下信息：

1. **运行诊断脚本**：
```bash
python diagnose_service_integration.py > diagnosis.log 2>&1
```

2. **检查 Anki 日志**：
- 在 Anki 中：帮助 → 调试控制台
- 查看错误信息

3. **系统信息**：
- 操作系统版本
- Python 版本
- Anki 版本
- 插件版本

### 常见错误代码
- **"All providers failed"**：所有 AI 提供商都无法连接
- **"LiteLLM not available"**：LiteLLM 库未安装或导入失败
- **"API key validation failed"**：API 密钥无效或权限不足
- **"Service not initialized"**：服务初始化失败

## ✅ 成功指标

修复成功的标志：
- ✅ `quick_service_test.py` 全部测试通过
- ✅ 插件配置界面可以正常打开
- ✅ "测试连接"功能正常工作
- ✅ "Ask AI" 按钮可以正常响应

## 🎯 预防措施

为避免将来出现问题：
1. 定期检查 API 密钥有效性
2. 保持依赖库更新
3. 备份工作配置
4. 定期运行快速测试

---

**如果按照本指南仍无法解决问题，请提供详细的错误日志和诊断信息。**

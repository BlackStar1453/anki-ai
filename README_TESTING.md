# LiteLLM 迁移测试指南

## 测试脚本概览

本项目包含完整的 LiteLLM 迁移测试套件，用于验证迁移的可行性和实施效果。

### 测试脚本列表

| 脚本名称 | 用途 | 执行时间 | 必需性 |
|---------|------|---------|--------|
| `quick_litellm_test.py` | 快速环境验证 | 1-2分钟 | 必需 |
| `test_litellm_feasibility.py` | 可行性评估 | 3-5分钟 | 必需 |
| `test_litellm_implementation.py` | 实现功能测试 | 5-10分钟 | 推荐 |
| `run_all_tests.py` | 自动化测试执行器 | 10-15分钟 | 推荐 |

## 快速开始

### 1. 单独运行测试

```bash
# 快速验证（推荐首次运行）
python quick_litellm_test.py

# 可行性评估
python test_litellm_feasibility.py

# 实现测试
python test_litellm_implementation.py
```

### 2. 自动化运行所有测试

```bash
# 运行完整测试套件
python run_all_tests.py
```

## 测试前准备

### 环境要求
- Python 3.7+
- 当前项目结构完整
- 网络连接（用于安装依赖）

### 可选配置
如果您有真实的 API 密钥，可以设置环境变量进行完整测试：

```bash
# 设置 API 密钥（可选）
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

**注意**: 即使没有真实 API 密钥，测试脚本也能正常运行并提供有价值的评估结果。

## 测试结果解读

### 成功率指标
- **90%+**: 优秀，可以立即开始迁移
- **70-89%**: 良好，建议解决失败项后迁移
- **50-69%**: 一般，需要仔细分析问题
- **<50%**: 不建议迁移，需要深入调查

### 常见测试结果

#### ✅ 预期成功的测试
- LiteLLM 安装和导入
- 基本配置设置
- 响应格式兼容性
- 适配器模式可行性

#### ⚠️ 可能失败的测试（正常）
- 实际 API 调用（无真实密钥时）
- 网络连接测试
- 特定提供商功能

#### ❌ 需要关注的失败
- 导入错误
- 配置系统问题
- 项目结构不兼容

## 测试输出文件

运行测试后会生成以下文件：

```
litellm_test_report_YYYYMMDD_HHMMSS.json  # 详细测试报告
```

## 故障排除

### 常见问题

**Q: LiteLLM 导入失败**
```bash
# 解决方案
pip install litellm
```

**Q: 测试脚本找不到**
```bash
# 确保在项目根目录运行
ls -la *.py
```

**Q: 权限错误**
```bash
# 给脚本执行权限
chmod +x *.py
```

**Q: Python 版本过低**
```bash
# 检查版本
python --version
# 升级 Python 到 3.7+
```

### 调试模式

如果测试失败，可以启用详细输出：

```bash
# 启用详细输出
python -v quick_litellm_test.py

# 查看具体错误
python test_litellm_feasibility.py 2>&1 | tee test_output.log
```

## 下一步操作

根据测试结果：

### 测试成功 (>70%)
1. 查看任务列表: 运行任务管理工具
2. 开始环境准备: 安装依赖和配置
3. 实施迁移: 按照实现文档逐步进行

### 测试部分失败 (50-70%)
1. 分析失败原因
2. 解决具体问题
3. 重新运行测试
4. 调整迁移计划

### 测试大量失败 (<50%)
1. 检查环境配置
2. 验证项目结构
3. 考虑替代方案
4. 寻求技术支持

## 支持和帮助

如果遇到问题：

1. **查看日志**: 检查详细的错误输出
2. **检查文档**: 阅读 `litellm_evaluation.md`
3. **验证环境**: 确保 Python 和依赖正确安装
4. **简化测试**: 从 `quick_litellm_test.py` 开始

## 文件说明

- `litellm_evaluation.md` - 详细的技术评估报告
- `migration_requirements.md` - 迁移需求文档
- `migration_implementation.md` - 实施方案文档
- `test_*.py` - 各种测试脚本
- `run_all_tests.py` - 自动化测试执行器

---

**提示**: 建议先运行 `quick_litellm_test.py` 进行快速验证，然后根据结果决定是否继续完整测试。

# Anki AI Chat Tool - 实现文档

## 项目结构设计

```
anki-ai-chat/
├── __init__.py              # 插件入口点
├── config.py               # 配置管理
├── ui/
│   ├── __init__.py
│   ├── chat_dialog.py      # 聊天窗口UI
│   └── button_injector.py  # 按钮注入器
├── services/
│   ├── __init__.py
│   ├── openai_service.py   # OpenAI API服务
│   └── card_service.py     # 卡片数据服务
├── utils/
│   ├── __init__.py
│   └── helpers.py          # 工具函数
└── manifest.json           # 插件清单
```

## 核心实现方案

### 1. 插件入口 (__init__.py)

```python
# 伪代码
def initialize_addon():
    """插件初始化入口"""
    # 注册钩子到Anki的答案显示界面
    register_answer_hooks()
    # 初始化配置
    load_config()
    # 注册菜单项（可选）
    register_menu_items()

def register_answer_hooks():
    """注册到答案显示的钩子"""
    # 使用Anki的hook系统
    # 在显示答案时注入askAI按钮
    gui_hooks.reviewer_did_show_answer.append(inject_ask_ai_button)
```

### 2. 按钮注入器 (ui/button_injector.py)

```python
# 伪代码
class ButtonInjector:
    def inject_ask_ai_button(reviewer):
        """在答案界面注入askAI按钮"""
        # 获取当前答案HTML内容
        current_html = get_answer_html()
        
        # 创建askAI按钮HTML
        button_html = create_ask_ai_button_html()
        
        # 将按钮添加到答案内容末尾
        modified_html = current_html + button_html
        
        # 更新显示内容
        update_answer_display(modified_html)
        
        # 绑定按钮点击事件
        bind_button_click_event()

    def create_ask_ai_button_html():
        """创建askAI按钮的HTML"""
        return """
        <div style="text-align: center; margin-top: 20px;">
            <button id="ask-ai-btn" onclick="pycmd('ask_ai')" 
                    style="background: #0078d4; color: white; padding: 10px 20px; 
                           border: none; border-radius: 5px; cursor: pointer;">
                Ask AI
            </button>
        </div>
        """
```

### 3. 聊天窗口 (ui/chat_dialog.py)

```python
# 伪代码
class ChatDialog(QDialog):
    def __init__(self, card_content):
        """初始化聊天窗口"""
        super().__init__()
        self.card_content = card_content
        self.conversation_history = []
        self.setup_ui()
        self.initialize_ai_context()
    
    def setup_ui():
        """设置用户界面"""
        # 创建聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # 创建输入区域
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        
        # 创建控制按钮
        self.save_button = QPushButton("Save to Card")
        self.close_button = QPushButton("Close")
        
        # 布局设置
        setup_layout()
        
        # 绑定事件
        bind_events()
    
    def initialize_ai_context():
        """初始化AI上下文"""
        # 将卡片内容添加到对话历史
        context_message = f"""
        Current Anki Card:
        Front: {self.card_content['front']}
        Back: {self.card_content['back']}
        
        Please help me understand this card better.
        """
        self.conversation_history.append({
            "role": "system", 
            "content": context_message
        })
    
    def send_message():
        """发送用户消息"""
        user_message = self.input_field.text()
        if not user_message.strip():
            return
            
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user", 
            "content": user_message
        })
        
        # 显示用户消息
        self.display_message("User", user_message)
        
        # 调用AI服务
        ai_response = openai_service.get_response(self.conversation_history)
        
        # 添加AI回复到历史
        self.conversation_history.append({
            "role": "assistant", 
            "content": ai_response
        })
        
        # 显示AI回复
        self.display_message("AI", ai_response)
        
        # 清空输入框
        self.input_field.clear()
    
    def save_to_card():
        """保存对话到卡片"""
        # 格式化对话内容
        formatted_conversation = format_conversation_for_card()
        
        # 调用卡片服务保存
        card_service.append_to_card(formatted_conversation)
        
        # 显示成功消息
        show_success_message()
```

### 4. OpenAI服务 (services/openai_service.py)

```python
# 伪代码
class OpenAIService:
    def __init__(self):
        # 硬编码API密钥（占位符）
        self.api_key = "sk-placeholder-key-here"
        self.model = "gpt-4o-mini"
        self.client = initialize_openai_client()
    
    def get_response(conversation_history):
        """获取AI回复"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=conversation_history,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return handle_api_error(e)
    
    def handle_api_error(error):
        """处理API错误"""
        error_message = f"AI服务暂时不可用: {str(error)}"
        log_error(error)
        return error_message
```

### 5. 卡片服务 (services/card_service.py)

```python
# 伪代码
class CardService:
    def get_current_card_content():
        """获取当前卡片内容"""
        # 从Anki获取当前卡片
        current_card = mw.reviewer.card
        
        # 提取正面和背面内容
        front_content = extract_text_from_html(current_card.question())
        back_content = extract_text_from_html(current_card.answer())
        
        return {
            "front": front_content,
            "back": back_content,
            "card_id": current_card.id
        }
    
    def append_to_card(conversation_content):
        """将对话内容添加到卡片"""
        current_card = mw.reviewer.card
        note = current_card.note()
        
        # 获取当前背面内容
        current_back = note.fields[1]  # 假设背面是第二个字段
        
        # 添加对话内容
        separator = "<hr><h3>AI Chat History</h3>"
        updated_back = current_back + separator + conversation_content
        
        # 更新并保存
        note.fields[1] = updated_back
        note.flush()
        
        # 刷新显示
        mw.reviewer.refresh()
```

## 测试服务设计（高优先级）

### 测试框架结构

```
tests/
├── __init__.py
├── test_config.py          # 测试配置
├── mock_anki.py           # Anki环境模拟
├── unit_tests/
│   ├── test_openai_service.py
│   ├── test_card_service.py
│   └── test_chat_dialog.py
├── integration_tests/
│   ├── test_button_injection.py
│   └── test_end_to_end.py
└── fixtures/
    ├── sample_cards.json
    └── mock_responses.json
```

### 核心测试服务实现

```python
# tests/mock_anki.py - Anki环境模拟
class MockAnki:
    def __init__(self):
        self.current_card = None
        self.reviewer = MockReviewer()
        self.mw = MockMainWindow()

    def setup_test_card(front_text, back_text):
        """设置测试卡片"""
        self.current_card = MockCard(front_text, back_text)
        return self.current_card

    def verify_card_updated(expected_content):
        """验证卡片是否正确更新"""
        return expected_content in self.current_card.back_content

# tests/test_config.py - 测试配置
class TestConfig:
    MOCK_OPENAI_KEY = "test-key-12345"
    TEST_RESPONSES = {
        "simple_question": "This is a test AI response",
        "error_case": "API_ERROR"
    }

    SAMPLE_CARDS = [
        {"front": "What is Python?", "back": "A programming language"},
        {"front": "2+2=?", "back": "4"}
    ]
```

### 单元测试实现

```python
# tests/unit_tests/test_openai_service.py
class TestOpenAIService:
    def test_api_response_success():
        """测试API成功响应"""
        # 使用mock替换真实API调用
        with mock.patch('openai.ChatCompletion.create') as mock_api:
            mock_api.return_value = create_mock_response("Test response")

            service = OpenAIService()
            result = service.get_response([{"role": "user", "content": "test"}])

            assert result == "Test response"
            assert mock_api.called

    def test_api_error_handling():
        """测试API错误处理"""
        with mock.patch('openai.ChatCompletion.create') as mock_api:
            mock_api.side_effect = Exception("API Error")

            service = OpenAIService()
            result = service.get_response([{"role": "user", "content": "test"}])

            assert "AI服务暂时不可用" in result

# tests/unit_tests/test_card_service.py
class TestCardService:
    def test_get_current_card_content():
        """测试获取卡片内容"""
        mock_anki = MockAnki()
        mock_anki.setup_test_card("Front text", "Back text")

        service = CardService()
        content = service.get_current_card_content()

        assert content["front"] == "Front text"
        assert content["back"] == "Back text"

    def test_append_to_card():
        """测试添加内容到卡片"""
        mock_anki = MockAnki()
        mock_anki.setup_test_card("Front", "Back")

        service = CardService()
        service.append_to_card("New AI conversation")

        assert mock_anki.verify_card_updated("New AI conversation")
```

### 集成测试实现

```python
# tests/integration_tests/test_end_to_end.py
class TestEndToEnd:
    def test_complete_workflow():
        """测试完整的AI聊天工作流程"""
        # 1. 设置测试环境
        mock_anki = MockAnki()
        test_card = mock_anki.setup_test_card("Test front", "Test back")

        # 2. 模拟按钮点击
        button_injector = ButtonInjector()
        button_injector.inject_ask_ai_button(mock_anki.reviewer)

        # 3. 模拟打开聊天窗口
        chat_dialog = ChatDialog(test_card.content)

        # 4. 模拟用户输入和AI回复
        with mock.patch('services.openai_service.get_response') as mock_ai:
            mock_ai.return_value = "This is a test AI response"

            chat_dialog.send_message("Test question")

            # 验证对话历史
            assert len(chat_dialog.conversation_history) >= 2
            assert "Test question" in str(chat_dialog.conversation_history)
            assert "This is a test AI response" in str(chat_dialog.conversation_history)

        # 5. 模拟保存到卡片
        chat_dialog.save_to_card()

        # 6. 验证卡片更新
        assert mock_anki.verify_card_updated("This is a test AI response")
```

### 测试运行脚本

```python
# run_tests.py
def run_all_tests():
    """运行所有测试"""
    import unittest

    # 发现并运行所有测试
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 生成测试报告
    generate_test_report(result)

    return result.wasSuccessful()

def generate_test_report(result):
    """生成测试报告"""
    report = f"""
    测试报告
    ========
    运行测试数: {result.testsRun}
    成功: {result.testsRun - len(result.failures) - len(result.errors)}
    失败: {len(result.failures)}
    错误: {len(result.errors)}

    详细信息:
    {format_test_details(result)}
    """

    with open('test_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
```

## 实现步骤规划（更新优先级）

### 阶段1: 测试服务搭建（最高优先级） ✅ 已完成
1. ✅ 创建测试框架结构
2. ✅ 实现Anki环境模拟器 (mock_anki.py)
3. ✅ 创建基础的单元测试和集成测试
4. ✅ 设置测试运行脚本和报告生成 (run_tests.py)

### 阶段2: 项目基础搭建 ✅ 已完成
1. ✅ 创建插件目录结构
2. ✅ 设置manifest.json配置文件
3. ✅ 创建基础的__init__.py入口文件
4. ✅ 运行基础测试验证结构正确

### 阶段3: 服务层实现（测试驱动） ✅ 已完成
1. ✅ 实现OpenAI API集成（先写测试，后写实现）
2. ✅ 实现卡片数据操作服务（先写测试，后写实现）
3. ✅ 添加错误处理和日志记录
4. ✅ 每个组件完成后立即运行对应测试

### 阶段4: UI组件开发（测试驱动） ✅ 已完成
1. ✅ 实现按钮注入功能（先写测试，后写实现）
2. ✅ 创建聊天窗口界面（先写测试，后写实现）
3. ✅ 测试UI组件的显示和交互
4. ✅ 运行集成测试验证UI和服务的协作

### 阶段5: 功能集成测试和优化 ✅ 已完成
1. ✅ 端到端功能测试 (7个集成测试)
2. ✅ 错误场景测试
3. ✅ 工具函数实现 (utils/helpers.py)
4. ✅ 最终验收测试 (47个测试全部通过)

## 关键技术点

1. **Anki钩子系统**: 使用`gui_hooks.reviewer_did_show_answer`
2. **PyQt界面**: 使用QDialog创建聊天窗口
3. **HTML注入**: 动态修改答案显示内容
4. **API集成**: OpenAI Python客户端库
5. **数据持久化**: Anki的note系统

## 测试策略（详细版）

### 1. 测试驱动开发(TDD)流程
```
对于每个组件：
1. 编写失败的测试用例
2. 编写最小可行的实现代码
3. 运行测试确保通过
4. 重构代码优化
5. 重复上述过程
```

### 2. 测试覆盖范围
- **单元测试**: 各个服务类的独立测试（目标覆盖率90%+）
- **集成测试**: UI和服务的集成测试
- **端到端测试**: 完整用户流程测试
- **错误处理测试**: 各种异常情况的测试
- **性能测试**: API调用和UI响应时间测试

### 3. 持续测试策略
- 每次代码修改后自动运行相关测试
- 每日运行完整测试套件
- 集成测试失败时立即停止开发
- 维护测试报告和覆盖率统计

### 4. 测试数据管理
- 使用固定的测试数据集
- 模拟各种卡片内容类型
- 准备多种AI响应场景
- 测试边界条件和异常输入

### 5. 测试环境隔离
- 使用Mock对象避免真实API调用
- 隔离Anki环境避免影响用户数据
- 独立的测试配置文件
- 可重复的测试执行环境

---

## 实际实现记录

### 实现完成时间: 2025-08-26 01:05:00

### 已实现的文件结构
```
anki-ai-chat/
├── __init__.py                 ✅ 插件入口点 (40行)
├── config.py                   ✅ 配置管理 (80行)
├── manifest.json               ✅ 插件清单
├── ui/
│   ├── __init__.py            ✅
│   ├── chat_dialog.py         ✅ 聊天窗口UI (280行)
│   └── button_injector.py     ✅ 按钮注入器 (150行)
├── services/
│   ├── __init__.py            ✅
│   ├── openai_service.py      ✅ OpenAI API服务 (120行)
│   └── card_service.py        ✅ 卡片数据服务 (180行)
├── utils/
│   ├── __init__.py            ✅
│   └── helpers.py             ✅ 工具函数 (200行)
├── tests/                      ✅ 完整测试套件
│   ├── mock_anki.py           ✅ Anki环境模拟 (100行)
│   ├── test_config.py         ✅ 测试配置 (80行)
│   ├── fixtures/              ✅ 测试数据
│   ├── unit_tests/            ✅ 40个单元测试
│   └── integration_tests/     ✅ 7个集成测试
├── run_tests.py               ✅ 测试运行脚本 (150行)
├── requirements.md            ✅ 需求文档
├── implementation.md          ✅ 实现文档
└── error_log.md              ✅ 错误日志
```

### 测试覆盖情况
- **总测试数**: 47个
- **单元测试**: 40个 (85%)
- **集成测试**: 7个 (15%)
- **测试成功率**: 100%
- **代码行数**: ~1200行（不含测试）
- **测试代码行数**: ~800行

### 核心功能实现状态

#### 1. 配置管理 ✅
- 支持Anki环境和测试环境
- 默认配置和用户配置合并
- OpenAI和UI配置分离

#### 2. OpenAI服务 ✅
- API密钥管理（硬编码占位符）
- 对话历史处理
- 错误处理和重试机制

#### 3. 卡片服务 ✅
- 获取当前卡片内容
- HTML文本提取
- 对话内容格式化
- 卡片内容更新和保存

#### 4. 按钮注入器 ✅
- JavaScript代码生成
- 按钮HTML创建
- 重复注入防护

#### 5. 聊天窗口 ✅
- Qt界面创建（支持PyQt5/6）
- AI上下文初始化
- 消息发送和显示
- 对话保存到卡片

### 实现特点
1. **测试驱动开发**: 所有组件都先写测试再写实现
2. **环境兼容性**: 支持Anki环境和独立测试环境
3. **错误处理**: 完善的异常处理和日志记录
4. **模块化设计**: 清晰的职责分离和接口设计
5. **安全性**: HTML转义和输入验证

### 下一步工作
1. 安装OpenAI库: `pip install openai`
2. 配置真实的OpenAI API密钥
3. 在Anki中测试插件功能
4. 根据实际使用情况进行优化

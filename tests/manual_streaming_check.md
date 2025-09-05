# 手动验证：打字机式流式显示

目的：确认 UI 在收到流式块时“原位更新同一条消息”，而不是追加多条消息。

步骤：
1. 在 OpenAIService.stream_response 中临时替换为模拟生成器（或注入一个 mock）：

   ```python
   def stream_response(self, conversation_history):
       import time
       for ch in "Hello, streaming works!":
           time.sleep(0.05)
           yield ch
   ```

2. 启动 Anki，打开 Chat 对话框，输入任意文本，点击 Send。

3. 期望结果：
   - 聊天窗口中只出现一条 AI 消息；
   - 这条消息的文本从空逐字增长，最终为 “Hello, streaming works!”；
   - 不应出现多条 AI 重复消息。

4. 恢复 OpenAIService.stream_response 的真实实现后，再次测试真实接口。

如需自动化测试，可在 UI 层为流式消息增加可测试 hook（例如在每次原位更新时发出信号），此处提供的是最小可行的手动确认方案。

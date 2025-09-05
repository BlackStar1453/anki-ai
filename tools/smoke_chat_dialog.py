#!/usr/bin/env python3
"""
快速冒烟测试：验证 ui/chat_dialog.py 的 send_message 流程基本可运行。
- 在无 Anki 环境下运行，使用 Mock UI 组件与服务
- 验证：
  1) 发送消息后不会出现语法错误/异常
  2) 模拟的流式生成器逐字更新同一条消息
"""

import sys
import types
import time
import re


# 将项目根目录加入路径
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 注入一个最小的 Qt Mock 环境
qt_mod = types.ModuleType('aqt.qt')
class Dummy:
    def __init__(self, *a, **kw):
        pass
    def setWindowTitle(self, *a, **kw):
        pass
    def setFixedSize(self, *a, **kw):
        pass
    def setLayout(self, *a, **kw):
        pass
    def close(self, *a, **kw):
        pass
    def addWidget(self, *a, **kw):
        pass
    def addLayout(self, *a, **kw):
        pass
class _Cursor:
    def __init__(self, te):
        self._te = te
        self._pos = 0
        self._anchor = 0
    def position(self):
        return self._pos
    def setPosition(self, pos, mode=0):
        if mode == 0:  # MoveAnchor
            self._pos = pos
            self._anchor = pos
        else:  # KeepAnchor
            self._pos = pos
    def insertHtml(self, html):
        s, e = sorted((self._anchor, self._pos))
        self._te._html = self._te._html[:s] + html + self._te._html[e:]
        self._pos = s + len(html)
        self._anchor = self._pos

class QTextEdit:
    def __init__(self):
        self._html = ""
        self._cursor = _Cursor(self)
    def setReadOnly(self, v):
        pass
    def setStyleSheet(self, s):
        pass
    def append(self, html):
        self._html += html
    def insertHtml(self, html):
        # mimic QTextEdit.insertHtml by inserting at cursor
        self._cursor.insertHtml(html)
    def clear(self):
        self._html = ""
    def verticalScrollBar(self):
        return types.SimpleNamespace(setValue=lambda v: None, maximum=lambda: 0)
    def moveCursor(self, where, *a, **kw):
        if where == 0:  # End
            self._cursor.setPosition(len(self._html), 0)
    def textCursor(self):
        return self._cursor
class Signal:
    def __init__(self):
        self._fn = None
    def connect(self, fn):
        self._fn = fn
    def emit(self):
        if self._fn:
            self._fn()

class QLineEdit(Dummy):
    def __init__(self):
        self._t = ''
        self._sig = Signal()
    def text(self):
        return self._t
    def setText(self, t):
        self._t = t
    def clear(self):
        self._t = ''
    def setPlaceholderText(self, t):
        pass
    @property
    def returnPressed(self):
        return self._sig
class QPushButton(Dummy):
    def __init__(self, text):
        self.text = text
        self._sig = Signal()
    @property
    def clicked(self):
        return self._sig
    def setEnabled(self, v):
        pass
    def setText(self, t):
        self.text = t
class QLabel(Dummy):
    def setStyleSheet(self, s):
        pass
class QMessageBox(Dummy):
    def setWindowTitle(self, t):
        pass
    def setText(self, t):
        pass
    def exec(self):
        pass
class QApplication:
    @staticmethod
    def processEvents():
        pass
class QTimer:
    def __init__(self, *a, **kw):
        self._interval = 0
        self._running = False
        self.timeout = Signal()
    def setInterval(self, ms):
        self._interval = ms
    def start(self):
        self._running = True
    def stop(self):
        self._running = False
class Qt: pass
class QTextCursor:
    End = 0
    MoveAnchor = 0
    KeepAnchor = 1
qt_mod.QDialog = Dummy
qt_mod.QVBoxLayout = Dummy
qt_mod.QHBoxLayout = Dummy
qt_mod.QTextEdit = QTextEdit
qt_mod.QLineEdit = QLineEdit
qt_mod.QPushButton = QPushButton
qt_mod.QLabel = QLabel
qt_mod.QMessageBox = QMessageBox
qt_mod.QApplication = QApplication
qt_mod.QTimer = QTimer
qt_mod.Qt = Qt
qt_mod.QTextCursor = QTextCursor

sys.modules['aqt'] = types.ModuleType('aqt')
sys.modules['aqt.qt'] = qt_mod

# Mock services
from services.openai_service import OpenAIService
real_stream = OpenAIService.stream_response

def mock_stream(self, history):
    for ch in "Hello, streaming works!":
        time.sleep(0.001)
        yield ch

OpenAIService.stream_response = mock_stream

# 导入被测模块
from ui.chat_dialog import ChatDialog

# 构造最小输入
card = {"front": "Q", "back": "A"}
cd = ChatDialog(card)
if not hasattr(cd, 'chat_display'):
    cd.chat_display = qt_mod.QTextEdit()

# 在某些环境下不会自动构建 UI，手动兜底
if not hasattr(cd, 'chat_display'):
    cd.setup_ui()
if not hasattr(cd, 'input_field'):
    cd.input_field = qt_mod.QLineEdit()
if not hasattr(cd, 'send_button'):
    cd.send_button = qt_mod.QPushButton("Send")

cd.input_field.setText("test")
cd.send_message()

# 由于现在使用线程+QTimer 异步刷新，给一点时间让分片累积
for _ in range(200):  # ~200*5ms = 1s
    # 手动触发 QTimer 的 timeout（在 mock 环境里）
    if hasattr(cd, '_stream_timer') and cd._stream_timer and cd._stream_timer._running:
        cd._stream_timer.timeout.emit()
    time.sleep(0.005)

# 校验：仅一条 AI 消息，且包含最终文本
html = getattr(cd.chat_display, '_html', '')
import re as _re
count_ai = len(_re.findall(r"<strong>AI:</strong>", html))
assert count_ai == 1, f"expected 1 AI block, got {count_ai}\nHTML: {html[:200]}..."
assert "Hello, streaming works!" in html, "final text not present"

# 恢复真实方法
OpenAIService.stream_response = real_stream

print("OK: streaming typing effect validated (single block, progressively updated)")


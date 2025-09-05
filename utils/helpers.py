# 工具函数

import re
import logging
import json
from datetime import datetime

def sanitize_html(html_content):
    """清理HTML内容，移除潜在的危险标签"""
    if not html_content:
        return ""
    
    # 移除script标签
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # 移除onclick等事件处理器
    html_content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
    
    # 移除javascript:协议
    html_content = re.sub(r'javascript:', '', html_content, flags=re.IGNORECASE)
    
    return html_content

def format_timestamp(timestamp=None):
    """格式化时间戳"""
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text, max_length=100, suffix="..."):
    """截断文本到指定长度"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def validate_conversation_history(conversation_history):
    """验证对话历史格式"""
    if not isinstance(conversation_history, list):
        return False, "Conversation history must be a list"
    
    for i, message in enumerate(conversation_history):
        if not isinstance(message, dict):
            return False, f"Message {i} must be a dictionary"
        
        if "role" not in message:
            return False, f"Message {i} missing 'role' field"
        
        if "content" not in message:
            return False, f"Message {i} missing 'content' field"
        
        if message["role"] not in ["system", "user", "assistant"]:
            return False, f"Message {i} has invalid role: {message['role']}"
    
    return True, "Valid conversation history"

def escape_javascript_string(text):
    """转义JavaScript字符串中的特殊字符"""
    if not text:
        return ""
    
    # 转义反斜杠
    text = text.replace("\\", "\\\\")
    
    # 转义引号
    text = text.replace("'", "\\'")
    text = text.replace('"', '\\"')
    
    # 转义换行符
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    
    # 转义制表符
    text = text.replace("\t", "\\t")
    
    return text

def parse_card_fields(card_html):
    """解析卡片HTML，提取字段信息"""
    fields = {}
    
    # 尝试提取标题
    title_match = re.search(r'<h[1-6][^>]*>(.*?)</h[1-6]>', card_html, re.IGNORECASE | re.DOTALL)
    if title_match:
        fields['title'] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
    
    # 尝试提取主要内容
    content_patterns = [
        r'<div[^>]*class[^>]*content[^>]*>(.*?)</div>',
        r'<p[^>]*>(.*?)</p>',
        r'<div[^>]*>(.*?)</div>'
    ]
    
    for pattern in content_patterns:
        matches = re.findall(pattern, card_html, re.IGNORECASE | re.DOTALL)
        if matches:
            fields['content'] = [re.sub(r'<[^>]+>', '', match).strip() for match in matches]
            break
    
    return fields

def log_error(error_message, context=None):
    """记录错误日志"""
    timestamp = format_timestamp()
    
    log_entry = {
        "timestamp": timestamp,
        "error": error_message,
        "context": context
    }
    
    # 记录到标准日志
    logging.error(f"[{timestamp}] {error_message}")
    if context:
        logging.error(f"Context: {context}")
    
    return log_entry

def safe_json_loads(json_string, default=None):
    """安全地解析JSON字符串"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        log_error(f"JSON parsing error: {e}", {"json_string": json_string})
        return default

def safe_json_dumps(obj, default=None):
    """安全地序列化为JSON字符串"""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as e:
        log_error(f"JSON serialization error: {e}", {"object": str(obj)})
        return default

def calculate_text_similarity(text1, text2):
    """计算两个文本的相似度（简单实现）"""
    if not text1 or not text2:
        return 0.0
    
    # 转换为小写并分词
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # 计算交集和并集
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    # 返回Jaccard相似度
    return len(intersection) / len(union)

def extract_keywords(text, max_keywords=10):
    """从文本中提取关键词"""
    if not text:
        return []
    
    # 简单的关键词提取：移除常见停用词
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    # 提取单词
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # 过滤停用词
    keywords = [word for word in words if word not in stop_words]
    
    # 计算词频
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # 按频率排序并返回前N个
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_keywords[:max_keywords]]

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def is_valid_url(url):
    """验证URL格式"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

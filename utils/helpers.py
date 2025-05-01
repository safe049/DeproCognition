import time
from datetime import datetime

def current_timestamp() -> int:
    """获取当前时间戳"""
    return int(time.time())

def format_timestamp(timestamp: int) -> str:
    """格式化时间戳"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def validate_config(config: dict) -> bool:
    """验证配置是否有效"""
    required_fields = [
        'api.provider',
        'api.ollama.base_url',
        'api.ollama.model',
        'memory.short_term.window_size',
        'memory.long_term.summary_interval'
    ]
    
    for field in required_fields:
        keys = field.split('.')
        current = config
        for key in keys:
            if key not in current:
                return False
            current = current[key]
    return True
from typing import List, Dict, Any
from .base import BaseMemory
from interfaces.config import ConfigManager

class ShortTermMemory(BaseMemory):
    def __init__(self, config: ConfigManager):
        self.config = config
        self.window_size = self.config.get('memory.short_term.window_size', 10)
        self.memory: List[Dict[str, Any]] = []
        
    def add(self, item: Dict[str, Any]):
        """添加短期记忆项"""
        self.memory.append(item)
        # 保持窗口大小
        if len(self.memory) > self.window_size:
            self.memory = self.memory[-self.window_size:]
    
    def retrieve(self, query: str = None) -> List[Dict[str, Any]]:
        """检索短期记忆"""
        if query is None:
            return self.memory.copy()
        # 简单实现 - 在实际应用中可以实现更复杂的检索
        return [item for item in self.memory if query.lower() in str(item).lower()]
    
    def clear(self):
        """清空短期记忆"""
        self.memory = []
    
    def get_conversation_history(self) -> str:
        """获取对话历史作为字符串"""
        return "\n".join(
            f"{item['role'].capitalize()}: {item['content']}" 
            for item in self.memory
        )
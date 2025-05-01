from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseMemory(ABC):
    @abstractmethod
    def add(self, item: Dict[str, Any]):
        """添加记忆项"""
        pass
    
    @abstractmethod
    def retrieve(self, query: str = None) -> List[Dict[str, Any]]:
        """检索记忆"""
        pass
    
    @abstractmethod
    def clear(self):
        """清空记忆"""
        pass
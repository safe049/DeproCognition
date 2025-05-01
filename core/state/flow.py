from typing import Optional, Dict, Any
import random
from interfaces.config import ConfigManager

class FlowState:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.active = False
        self.flow_level = 0.5  # 0-1表示心流状态
        self.last_activity = None
    
    def update(self, activity_type: str, duration: float):
        """更新心流状态"""
        self.last_activity = activity_type
        
        # 不同类型活动对心流的影响
        flow_impact = {
            'creative': 0.3,
            'analytical': 0.2,
            'social': 0.1,
            'routine': -0.1
        }.get(activity_type, 0)
        
        # 持续时间影响
        duration_factor = min(1.0, duration / 60.0)  # 假设60分钟达到最大影响
        
        self.flow_level += flow_impact * duration_factor
        self.flow_level = max(0, min(1, self.flow_level))
        
        # 根据心流水平决定是否激活
        self.active = self.flow_level > 0.6
    
    def should_respond(self) -> bool:
        """决定是否应该回复"""
        if not self.active:
            return random.random() < 0.3  # 非活跃状态下有30%概率回复
        
        # 心流状态下回复概率更高
        return random.random() < (0.7 + self.flow_level * 0.3)
    
    def should_initiate(self) -> bool:
        """决定是否应该主动发起对话"""
        if not self.active:
            return random.random() < 0.1  # 非活跃状态下有10%概率主动发起
            
        # 心流状态下主动发起概率更高
        return random.random() < (0.3 + self.flow_level * 0.2)
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前心流状态"""
        return {
            'active': self.active,
            'flow_level': self.flow_level,
            'last_activity': self.last_activity
        }
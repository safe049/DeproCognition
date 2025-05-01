from typing import Dict, Any
from interfaces.config import ConfigManager

class PromptManager:
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def render_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """渲染提示词模板"""
        result = template
        for key, value in context.items():
            placeholder = f"<{key}>"
            result = result.replace(placeholder, str(value))
        return result
    
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """获取系统提示词"""
        template = self.config.get('prompts.system', "")
        return self.render_prompt(template, context)
    
    def get_memory_summary_prompt(self, context: Dict[str, Any]) -> str:
        """获取记忆总结提示词"""
        template = self.config.get('prompts.memory_summary', "")
        return self.render_prompt(template, context)
    
    def get_active_prompt(self, context: Dict[str, Any]) -> str:
        """获取主动发言提示词"""
        template = self.config.get('prompts.active_trigger', "")
        return self.render_prompt(template, context)
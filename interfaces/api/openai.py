import openai
from typing import Dict, Any, Optional
from interfaces.config import ConfigManager

class OpenAIAPI:
    def __init__(self, config: ConfigManager):
        self.config = config
        openai.api_key = self.config.get('api.openai.api_key')
        openai.base_url = self.config.get('api.openai.base_url')
        self.model = self.config.get('api.openai.model')
        self.temperature = self.config.get('api.openai.temperature')
        self.top_p = self.config.get('api.openai.top_p')
        
    def chat_completion(self, messages: list, **kwargs) -> str:
        """生成聊天回复"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                top_p=kwargs.get('top_p', self.top_p),
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API请求失败: {str(e)}")
import requests
from typing import Dict, Any, Optional
from interfaces.config import ConfigManager

class OllamaAPI:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.base_url = self.config.get('api.ollama.base_url')
        self.model = self.config.get('api.ollama.model')
        self.temperature = self.config.get('api.ollama.temperature')
        self.top_p = self.config.get('api.ollama.top_p')
        
    def generate(self, prompt: str, **kwargs) -> str:
        """生成回复"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', self.temperature),
                "top_p": kwargs.get('top_p', self.top_p),
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            raise Exception(f"Ollama API请求失败: {str(e)}")
    
    def chat(self, messages: list, **kwargs) -> str:
        """聊天模式"""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', self.temperature),
                "top_p": kwargs.get('top_p', self.top_p),
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()['message']['content']
        except Exception as e:
            raise Exception(f"Ollama聊天API请求失败: {str(e)}")
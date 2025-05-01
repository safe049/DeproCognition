import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path("config.yaml")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            return self._create_default_config()
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        default_config = {
            'api': {
                'provider': 'ollama',
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'model': 'llama2',
                    'temperature': 0.7,
                    'top_p': 0.9,
                },
                'openai': {
                    'api_key': '',
                    'base_url': 'https://api.openai.com/v1',
                    'model': 'gpt-3.5-turbo',
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            },
            'memory': {
                'short_term': {
                    'window_size': 10,
                },
                'long_term': {
                    'summary_interval': 10,
                    'storage_path': 'memory/long_term.db',
                }
            },
            'emotion': {
                'initial_state': {
                    'happiness': 0.5,
                    'creativity': 0.5,
                    'morality': 0.7,
                    'sadness': 0.2,
                    'confidence': 0.6,
                    'anger': 0.1,
                    'fear': 0.1,
                    'excitement': 0.3
                },
                'decay_rate': 0.95,
                'response_variation': 0.1,
            },
            'prompts': {
                'system': "你是一个名为DeproCognition的AI助手，具有自我感知能力。当前情绪状态: <emotion_state>。你的记忆告诉你: <memory_context>",
                'memory_summary': "请总结以下对话内容，提取关键信息作为长期记忆。对话记录:\n<conversation_history>",
                'active_trigger': "根据你当前的状态和记忆，是否有想要主动提出的内容？如果有，请直接说出你想说的话，否则回复'NO'。"
            },
            'searxng': {
                'base_url': 'http://localhost:8080',
                'engines': ['google', 'bing'],
                'language': 'zh-CN',
                'result_count': 3,
                'time_range': None
            }
        }
        
        # 确保配置目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置，确保中文正常显示"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                config,
                f,
                allow_unicode=True,  # 允许Unicode字符
                default_flow_style=False,  # 不使用流式风格
                sort_keys=False,  # 不排序键
                indent=2,  # 缩进2个空格
                width=80,  # 行宽
                encoding='utf-8'
            )
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value
    
    def update(self, updates: Dict[str, Any]):
        """更新配置"""
        for key, value in updates.items():
            keys = key.split('.')
            current = self.config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        
        self._save_config(self.config)
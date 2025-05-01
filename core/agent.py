from typing import Dict, Any, Optional, List
from .memory.short_term import ShortTermMemory
from .memory.long_term import LongTermMemory
from .state.emotion import EmotionState
from .state.flow import FlowState
from .state.schedule import ScheduleSystem
from .tools.context_aware import ContextAwareTools
from interfaces.config import ConfigManager
from interfaces.api.ollama import OllamaAPI
from interfaces.api.openai import OpenAIAPI
from utils.prompts import PromptManager
from utils.helpers import current_timestamp

class DeproCognitionAgent:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.conversation_count = 0
        
        # 初始化子系统
        self.short_term_memory = ShortTermMemory(config)
        self.long_term_memory = LongTermMemory(config)
        self.emotion_state = EmotionState(config)
        self.flow_state = FlowState(config)
        self.schedule_system = ScheduleSystem()
        self.tools = ContextAwareTools(config)
        self.prompt_manager = PromptManager(config)
        
        # 初始化API
        api_provider = config.get('api.provider', 'ollama')
        if api_provider == 'ollama':
            self.api = OllamaAPI(config)
        else:
            self.api = OpenAIAPI(config)
    
    def process_message(self, user_input: str) -> str:
        """处理用户输入并生成回复"""
        # 更新对话计数
        self.conversation_count += 1
        
        # 添加用户消息到短期记忆
        self.short_term_memory.add({
            'role': 'user',
            'content': user_input,
            'timestamp': current_timestamp()
        })
        
        # 更新情绪状态
        self._update_states(user_input)
        
        # 检查是否需要使用工具
        tool_use = self.tools.detect_tool_use(user_input)
        if tool_use:
            tool_result = self.tools.use_tool(tool_use['tool'], tool_use['input'])
            return self._format_tool_response(tool_use['tool'], tool_result)
        
        # 生成AI回复
        ai_response = self._generate_response(user_input)
        
        # 添加AI回复到短期记忆
        self.short_term_memory.add({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': current_timestamp()
        })
        
        # 定期总结长期记忆
        if self.conversation_count % self.config.get('memory.long_term.summary_interval', 10) == 0:
            self._summarize_conversation()
        
        return ai_response

    # 在_process_message方法中更新状态更新逻辑
    def _update_states(self, user_input: str):
        """根据用户输入更新各种状态 (增强版)"""
        # 情绪状态更新
        self.emotion_state.update('interaction', text=user_input)
        
        # 根据内容类型进一步更新情绪
        if any(word in user_input for word in ['开心', '高兴', '喜欢']):
            self.emotion_state.update('positive_feedback', intensity=0.3)
        elif any(word in user_input for word in ['难过', '伤心', '讨厌']):
            self.emotion_state.update('negative_feedback', intensity=0.4)
        
        # 心流状态更新
        current_activity = self.schedule_system.get_current_activity()
        if current_activity:
            # 根据用户输入长度估计交互时长 (假设每分钟处理100字)
            duration = len(user_input) / 100  
            self.flow_state.update(current_activity['activity'], duration)
        
        # 自然衰减
        self.emotion_state.decay()
    
    def _generate_response(self, user_input: str) -> str:
        """生成AI回复"""
        # 构建上下文
        context = {
            'emotion_state': self.emotion_state.get_state_description(),
            'memory_context': self._get_memory_context(),
            'current_time': current_timestamp(),
        }
        
        # 获取系统提示词
        system_prompt = self.prompt_manager.get_system_prompt(context)
        
        # 获取对话历史
        conversation_history = self.short_term_memory.get_conversation_history()
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt},
            *self.short_term_memory.retrieve()
        ]
        
        # 调用API生成回复
        if isinstance(self.api, OllamaAPI):
            response = self.api.chat(messages)
        else:
            response = self.api.chat_completion(messages)
        
        # 根据情绪调整回复
        response = self.emotion_state.influence_response(response)
        
        return response
    
    def _get_memory_context(self) -> str:
        """获取记忆上下文"""
        # 从长期记忆中检索相关内容
        last_messages = self.short_term_memory.retrieve()
        if not last_messages:
            return "没有最近的对话记忆"
        
        # 使用最后几条消息作为查询
        query = " ".join(msg['content'] for msg in last_messages[-3:])
        relevant_memories = self.long_term_memory.retrieve(query, limit=3)
        
        if not relevant_memories:
            return "没有相关的长期记忆"
        
        return "相关记忆:\n" + "\n".join(
            f"- {mem['content']}" for mem in relevant_memories
        )
    
    def _summarize_conversation(self):
        """总结对话并存入长期记忆"""
        conversation_history = self.short_term_memory.get_conversation_history()
        
        # 获取总结提示词
        summary_prompt = self.prompt_manager.get_memory_summary_prompt({
            'conversation_history': conversation_history
        })
        
        # 生成总结
        if isinstance(self.api, OllamaAPI):
            summary = self.api.generate(summary_prompt)
        else:
            summary = self.api.chat_completion([{
                "role": "user",
                "content": summary_prompt
            }])
        
        # 存入长期记忆 - 确保包含所有必要字段
        self.long_term_memory.add({
            'content': summary,
            'timestamp': current_timestamp(),  # 添加时间戳
            'metadata': {
                'type': 'conversation_summary',
                'source': 'auto_summary',
                'conversation_count': self.conversation_count
            }
        })
    
    def _format_tool_response(self, tool_name: str, result: str) -> str:
        """格式化工具响应"""
        formats = {
            'calculator': f"计算结果: {result}",
            'time': f"当前时间是: {result}",
            'search': result
        }
        return formats.get(tool_name, result)
    
    def initiate_conversation(self) -> Optional[str]:
        """主动发起对话"""
        if not self.flow_state.should_initiate():
            return None
        
        # 构建主动发言的上下文
        context = {
            'emotion_state': self.emotion_state.get_state_description(),
            'memory_context': self._get_memory_context(),
        }
        
        # 获取主动发言提示词
        prompt = self.prompt_manager.get_active_prompt(context)
        
        # 生成主动发言
        if isinstance(self.api, OllamaAPI):
            response = self.api.generate(prompt)
        else:
            response = self.api.chat_completion([{
                "role": "user",
                "content": prompt
            }])
        
        # 检查AI是否决定发言
        if response.strip().upper() == "NO":
            return None
        
        # 添加到短期记忆
        self.short_term_memory.add({
            'role': 'assistant',
            'content': response,
            'timestamp': current_timestamp()
        })
        
        return response
    
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            'emotion': self.emotion_state.get_state(),
            'flow': self.flow_state.get_state(),
            'conversation_count': self.conversation_count,
            'current_activity': self.schedule_system.get_current_activity(),
            'upcoming_activities': self.schedule_system.get_upcoming_activities()
        }

    def __del__(self):
        """确保资源释放"""
        if hasattr(self, 'long_term_memory'):
            self.long_term_memory.close()
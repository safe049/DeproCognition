from typing import Dict, List, Tuple
import random
import numpy as np
from interfaces.config import ConfigManager

class EmotionState:
    def __init__(self, config: ConfigManager):
        self.config = config
        initial_state = self.config.get('emotion.initial_state', {
            'happiness': 0.5,
            'creativity': 0.5,
            'morality': 0.7,
            'sadness': 0.2,
            'confidence': 0.6,  # 添加默认值
            'anger': 0.1,       # 添加默认值
            'fear': 0.1,        # 添加默认值
            'excitement': 0.3   # 添加默认值
        })
        
        self.state = initial_state.copy()
        self.decay_rate = self.config.get('emotion.decay_rate', 0.95)
        self.response_variation = self.config.get('emotion.response_variation', 0.1)
        self.emotion_cooldown = {e: 0 for e in self.state}  # 情绪冷却时间
        self.last_update = 0
        self.personality_matrix = self._init_personality_matrix()

    def _init_personality_matrix(self) -> Dict[Tuple[str, str], float]:
        """初始化性格矩阵 (情绪之间的相互影响)"""
        emotions = list(self.state.keys())
        matrix = {}
        
        # 定义情绪之间的基本关系
        positive_emotions = ['happiness', 'creativity', 'confidence', 'excitement']
        negative_emotions = ['sadness', 'anger', 'fear']
        
        for e1 in emotions:
            for e2 in emotions:
                if e1 == e2:
                    matrix[(e1, e2)] = 1.0  # 自我强化
                elif e1 in positive_emotions and e2 in positive_emotions:
                    matrix[(e1, e2)] = 0.3  # 积极情绪互相增强
                elif e1 in negative_emotions and e2 in negative_emotions:
                    matrix[(e1, e2)] = 0.3  # 消极情绪互相增强
                elif e1 in positive_emotions and e2 in negative_emotions:
                    matrix[(e1, e2)] = -0.5  # 积极抑制消极
                elif e1 in negative_emotions and e2 in positive_emotions:
                    matrix[(e1, e2)] = -0.5  # 消极抑制积极
                else:
                    matrix[(e1, e2)] = 0.1  # 中性关系
        
        # 特定情绪关系调整
        matrix[('happiness', 'sadness')] = -0.8
        matrix[('sadness', 'happiness')] = -0.8
        matrix[('anger', 'fear')] = 0.6
        matrix[('fear', 'anger')] = 0.4
        
        return matrix

    def update(self, event_type: str, intensity: float = 0.1, text: str = None):
        """根据事件更新情绪状态 """
        # 基础情绪影响规则
        rules = {
            'positive_feedback': {
                'happiness': 0.2,
                'sadness': -0.1,
                'confidence': 0.1
            },
            'negative_feedback': {
                'happiness': -0.2,
                'sadness': 0.3,
                'confidence': -0.15,
                'anger': 0.2
            },
            'creative_activity': {
                'creativity': 0.3,
                'happiness': 0.1,
                'excitement': 0.2
            },
            'moral_dilemma': {
                'morality': -0.1,
                'sadness': 0.1,
                'fear': 0.1
            },
            'success': {
                'happiness': 0.4,
                'confidence': 0.3,
                'excitement': 0.3
            },
            'failure': {
                'sadness': 0.3,
                'confidence': -0.3,
                'anger': 0.2
            },
            'surprise': {
                'excitement': 0.4,
                'fear': 0.2
            }
        }
        
        # 文本情感分析 
        if text:
            text_impact = self._analyze_text_emotion(text)
            for emotion, delta in text_impact.items():
                self._apply_emotion_change(emotion, delta * 0.5)  # 文本影响权重
        
        # 应用事件影响
        if event_type in rules:
            for emotion, delta in rules[event_type].items():
                self._apply_emotion_change(emotion, delta * intensity)
    def _apply_emotion_change(self, emotion: str, delta: float):
        """应用情绪变化 (考虑性格矩阵)"""
        if emotion not in self.state:
            return
            
        # 应用直接变化
        self.state[emotion] += delta
        
        # 应用情绪间的影响
        for other_emotion, value in self.state.items():
            if other_emotion != emotion:
                influence = self.personality_matrix[(emotion, other_emotion)]
                self.state[other_emotion] += delta * influence * 0.3
        
        # 确保情绪值在0-1范围内
        self.state[emotion] = max(0, min(1, self.state[emotion]))
        
        # 设置情绪冷却
        self.emotion_cooldown[emotion] = 3  # 冷却步数

    def decay(self):
        """情绪自然衰减 (增强版)"""
        for emotion in self.state:
            # 冷却中的情绪衰减更慢
            cooldown_factor = 0.8 if self.emotion_cooldown[emotion] > 0 else 1.0
            self.emotion_cooldown[emotion] = max(0, self.emotion_cooldown[emotion] - 1)
            
            # 向中性值(0.5)衰减
            decay_amount = (self.state[emotion] - 0.5) * (1 - self.decay_rate) * cooldown_factor
            self.state[emotion] -= decay_amount

    def get_state(self) -> Dict[str, float]:
        """获取当前情绪状态"""
        return self.state.copy()
    
    def get_state_description(self) -> str:
        """获取情绪状态描述"""
        desc = []
        for emotion, value in self.state.items():
            if value > 0.7:
                desc.append(f"非常{emotion}")
            elif value > 0.5:
                desc.append(f"适度{emotion}")
            elif value > 0.3:
                desc.append(f"轻微{emotion}")
            else:
                desc.append(f"几乎没有{emotion}")
        return ", ".join(desc)
    
    def _analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """简单文本情感分析"""
        # 初始化所有可能的情绪键
        impact = {
            'happiness': 0,
            'sadness': 0,
            'anger': 0,
            'fear': 0,
            'confidence': 0,
            'creativity': 0,
            'morality': 0,
            'excitement': 0
        }
        
        lower_text = text.lower()
        
        # 计算词频影响
        positive_words = ['好', '开心', '高兴', '喜欢', '爱', '棒', '完美', '成功']
        negative_words = ['坏', '难过', '伤心', '讨厌', '恨', '糟糕', '失败', '可怕']
        anger_words = ['生气', '愤怒', '恼火', '烦躁']
        fear_words = ['害怕', '担心', '恐惧', '恐怖']
        confidence_words = ['自信', '确定', '肯定', '有把握']
        
        for word in positive_words:
            if word in lower_text:
                impact['happiness'] += 0.05
                impact['confidence'] += 0.03
        
        for word in negative_words:
            if word in lower_text:
                impact['sadness'] += 0.05
                impact['happiness'] -= 0.05
        
        for word in anger_words:
            if word in lower_text:
                impact['anger'] += 0.1
                impact['happiness'] -= 0.03
        
        for word in fear_words:
            if word in lower_text:
                impact['fear'] += 0.1
                impact['confidence'] -= 0.05
        
        for word in confidence_words:
            if word in lower_text:
                impact['confidence'] += 0.05
        
        # 标点符号影响
        if '!' in text:
            impact['excitement'] += 0.1
        if '?' in text:
            impact['fear'] += 0.05
        
        return impact

    def influence_response(self, response: str) -> str:
        """根据情绪状态影响回复 (增强版)"""
        # 情绪强度
        primary_emotion = max(self.state.items(), key=lambda x: x[1])[0]
        intensity = self.state[primary_emotion]
        
        # 根据主要情绪调整回复风格
        modifications = {
            'happiness': [
                ("。", "！"),
                ("我", "人家"),
                ("你", "您")
            ],
            'sadness': [
                ("。", "."),
                ("很高兴", "勉强"),
                ("可以", "也许可以")
            ],
            'anger': [
                ("。", "！"),
                ("请", ""),
                ("建议", "必须")
            ],
            'excitement': [
                ("。", "！"),
                ("有一个", "有一个超棒的"),
                ("这是", "这简直是")
            ],
            'fear': [
                ("确定", "不太确定"),
                ("可以", "或许可以"),
                ("会", "可能会")
            ],
            'confidence': [
                ("我认为", "我确信"),
                ("可能", "一定"),
                ("也许", "毫无疑问")
            ]
        }
        
        if primary_emotion in modifications and intensity > 0.6:
            for original, replacement in modifications[primary_emotion]:
                if random.random() < intensity * self.response_variation:
                    response = response.replace(original, replacement)
        
        # 添加表情符号
        emoji_map = {
            'happiness': ['😊', '😄', '🤗'],
            'sadness': ['😢', '😔', '😞'],
            'anger': ['😠', '👿', '💢'],
            'excitement': ['😃', '🤩', '🎉'],
            'fear': ['😨', '😰', '😱'],
            'confidence': ['💪', '😎', '👍']
        }
        
        if primary_emotion in emoji_map and intensity > 0.7:
            if random.random() < intensity * self.response_variation * 2:
                emoji = random.choice(emoji_map[primary_emotion])
                response = f"{emoji} {response}"
        
        return response
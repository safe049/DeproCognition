from typing import Dict, Any, Optional
from interfaces.config import ConfigManager

class ContextAwareTools:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.searxng_config = config.get('searxng', {})
        self.available_tools = self._load_tools()
    
    def _load_tools(self) -> Dict[str, Any]:
        """加载可用工具"""
        return {
            'calculator': self.calculate,
            'time': self.get_time,
            'joke': self.tell_joke,
            'searxng_search': self.searxng_search,
        }
    def tell_joke(self) -> str:
        """讲个笑话"""
        import random
        jokes = [
            "为什么要读书？因为读书可以让你变得更聪明。",
            "为什么要学习编程？因为编程可以让你有更强的逻辑思维能力。",
            "为什么要锻炼身体？因为锻炼身体可以让你有更强的体力。",
        ]
        return random.choice(jokes)
    def searxng_search(self, query: str) -> str:
        """使用Searxng进行网络搜索"""
        base_url = self.searxng_config.get('base_url', 'http://localhost:8080')
        params = {
            'q': query,
            'format': 'json',
            'engines': ','.join(self.searxng_config.get('engines', ['google'])),
            'language': self.searxng_config.get('language', 'zh-CN'),
            'time_range': self.searxng_config.get('time_range', ''),
            'pageno': 1,
        }
        
        try:
            response = requests.get(
                f"{base_url}/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            results = response.json().get('results', [])[:self.searxng_config.get('result_count', 3)]
            
            if not results:
                return "没有找到相关搜索结果"
                
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result.get('title', '无标题')}\n"
                    f"   {result.get('url', '无URL')}\n"
                    f"   {result.get('content', '无描述')}"
                )
            
            return "搜索结果显示如下:\n\n" + "\n\n".join(formatted_results)
        except Exception as e:
            return f"搜索时出错: {str(e)}"
    
    def calculate(self, expression: str) -> str:
        """计算表达式"""
        try:
            return str(eval(expression))
        except:
            return "无法计算该表达式"
    
    def get_time(self, *args) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    def detect_tool_use(self, text: str) -> Optional[Dict]:
        """检测是否需要使用工具 (增强版)"""
        tool_prefixes = {
            '计算': ('calculator', '计算'),
            '算一下': ('calculator', '算一下'),
            '现在几点': ('time', '现在几点'),
            '时间': ('time', '时间'),
            '搜索': ('searxng_search', '搜索'),
            '查找': ('searxng_search', '查找'),
            '查询': ('searxng_search', '查询'),
            '讲个笑话': ('joke', '讲个笑话'),
            '笑话': ('joke', '笑话'),
        }
        
        # 检查精确匹配
        for prefix, (tool_name, _) in tool_prefixes.items():
            if text.startswith(prefix):
                return {
                    'tool': tool_name,
                    'input': text[len(prefix):].strip()
                }
        
        # 检查模糊匹配
        tool_keywords = {
            'searxng_search': ['搜索', '查找', '查询', '什么是', '谁'],
            'calculator': ['计算', '算一下', '加', '减', '乘', '除', '等于', '等于多少', '等于几'],
            'joke': ['笑话', '搞笑', '幽默']
        }
        
        for tool_name, keywords in tool_keywords.items():
            if any(keyword in text for keyword in keywords):
                return {
                    'tool': tool_name,
                    'input': text
                }
        
        return None
    
    def use_tool(self, tool_name: str, input_data: str) -> str:
        """使用工具"""
        if tool_name in self.available_tools:
            return self.available_tools[tool_name](input_data)
        return f"未知工具: {tool_name}"
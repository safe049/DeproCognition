from core.agent import DeproCognitionAgent
from interfaces.config import ConfigManager
import argparse
import threading
import time
import sys
from pathlib import Path
import signal
from colorama import init, Fore, Back, Style
import textwrap
import re

# 初始化彩色输出
init(autoreset=True)

class DeproCognitionApp:
    def __init__(self, config_path):
        # 打印Linux风格启动信息
        self._print_startup_header()
        
        # 初始化配置
        self._print_status("Loading Configuration System", self._load_config, config_path)
        
        # 创建智能体实例
        self._print_status("Initializing Cognitive Modules", self._init_agent, config_path)
        
        # 线程控制
        self._running = False
        self._active_thread = None
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
        
        # 命令映射
        self.commands = {
            '/help': {
                'func': self._cmd_help,
                'desc': '显示所有可用命令'
            },
            '/debug_emotion': {
                'func': self._cmd_debug_emotion,
                'desc': '打印当前情绪状态'
            },
            '/debug_prompt': {
                'func': self._cmd_debug_prompt,
                'desc': '打印当前系统提示词(包含变量)'
            },
            '/debug_memory': {
                'func': self._cmd_debug_memory,
                'desc': '显示记忆系统状态'
            },
            '/sysinfo': {
                'func': self._cmd_sysinfo,
                'desc': '显示系统状态信息'
            },
            '/add_memory': {
                'func': self._cmd_add_memory,
                'desc': '添加长期记忆 - 格式: /add_memory <记忆内容>'
            },
            '/inspect_long_term': {
                'func': self._cmd_inspect_long_term,
                'desc': '检视所有长期记忆'
            },
            '/rm_memory': {
                'func': self._cmd_rm_memory,
                'desc': '删除指定记忆 - 格式: /rm_memory <记忆ID>'
            },
            '/flush_long_term_memory': {
                'func': self._cmd_flush_long_term,
                'desc': '清空所有长期记忆(需确认)'
            }
        }

    def _print_startup_header(self):
        """打印Linux风格启动头"""
        print(Fore.CYAN + r"""
 ____                        ___  ____  
|  _ \  ___ _ __  _ __ ___  / _ \/ ___| 
| | | |/ _ \ '_ \| '__/ _ \| | | \___ \ 
| |_| |  __/ |_) | | | (_) | |_| |___) |
|____/ \___| .__/|_|  \___/ \___/|____/ 
           |_|                          
        """ + Style.RESET_ALL)
        print(Fore.YELLOW + "DeproCognition Cognitive Agent System" + Style.RESET_ALL)
        print(Fore.YELLOW + "="*50 + Style.RESET_ALL)

    def _print_status(self, message, func, *args):
        """打印带状态的启动消息"""
        print(Fore.BLUE + f"[....] {message}", end='\r', flush=True)
        try:
            func(*args)
            print(Fore.GREEN + f"[ OK ] {message}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[FAIL] {message}" + Style.RESET_ALL)
            raise

    def _load_config(self, config_path):
        """加载配置"""
        self.config = ConfigManager(config_path)

    def _init_agent(self, config_path):
        """初始化智能体"""
        self.agent = DeproCognitionAgent(self.config)

    def _handle_interrupt(self, signum, frame):
        """处理中断信号"""
        print(Fore.RED + "\n接收到终止信号，正在关闭..." + Style.RESET_ALL)
        self.stop()
        sys.exit(0)

    def _active_speaking(self):
        """主动发言线程"""
        while self._running:
            try:
                time.sleep(60)
                message = self.agent.initiate_conversation()
                if message:
                    print(Fore.MAGENTA + f"\n[DeproCognition主动发言]: {message}\n" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"主动发言线程出错: {str(e)}" + Style.RESET_ALL)
                break

    # ========== 命令处理函数 ==========
    def _cmd_help(self, _):
        """显示帮助信息"""
        help_text = Fore.CYAN + "可用命令:\n" + Style.RESET_ALL
        for cmd, info in self.commands.items():
            help_text += f"{Fore.GREEN}{cmd.ljust(15)}{Style.RESET_ALL} - {info['desc']}\n"
        print(help_text)

    def _cmd_debug_emotion(self, _):
        """显示情绪状态"""
        state = self.agent.emotion_state.get_state()
        print(Fore.YELLOW + "\n当前情绪状态:" + Style.RESET_ALL)
        for emotion, value in state.items():
            print(f"  {emotion.ljust(12)}: {Fore.CYAN}{value:.2f}{Style.RESET_ALL}")

    def _cmd_debug_prompt(self, _):
        """显示当前提示词"""
        context = {
            'emotion_state': self.agent.emotion_state.get_state_description(),
            'memory_context': "示例记忆内容",
            'current_time': "2023-11-15 12:00:00"
        }
        prompt = self.agent.prompt_manager.get_system_prompt(context)
        
        print(Fore.YELLOW + "\n系统提示词模板:" + Style.RESET_ALL)
        print(Fore.CYAN + prompt + Style.RESET_ALL)
        
        print(Fore.YELLOW + "\n当前变量替换后:" + Style.RESET_ALL)
        colored_prompt = re.sub(
            r'<([^>]+)>', 
            lambda m: Fore.RED + f'<{m.group(1)}>' + Fore.CYAN, 
            prompt
        )
        print(Fore.CYAN + colored_prompt + Style.RESET_ALL)

    def _cmd_debug_memory(self, _):
        """显示记忆状态"""
        print(Fore.YELLOW + "\n记忆系统状态:" + Style.RESET_ALL)
        print(f"  短期记忆数量: {Fore.CYAN}{len(self.agent.short_term_memory.memory)}{Style.RESET_ALL}")
        
        # 获取长期记忆统计
        try:
            with self.agent.long_term_memory._conn as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM memories")
                count = cursor.fetchone()[0]
                print(f"  长期记忆数量: {Fore.CYAN}{count}{Style.RESET_ALL}")
        except Exception as e:
            print(f"  长期记忆查询失败: {Fore.RED}{str(e)}{Style.RESET_ALL}")

    def _cmd_sysinfo(self, _):
        """显示系统信息"""
        state = self.agent.get_current_state()
        
        print(Fore.YELLOW + "\n系统状态信息:" + Style.RESET_ALL)
        print(f"  对话计数: {Fore.CYAN}{state['conversation_count']}{Style.RESET_ALL}")
        print(f"  当前活动: {Fore.CYAN}{state['current_activity']['activity'] if state['current_activity'] else '无'}{Style.RESET_ALL}")
        print(f"  心流状态: {Fore.CYAN}{state['flow']['flow_level']:.2f}{Style.RESET_ALL}")

    def _cmd_add_memory(self, args):
        """添加长期记忆"""
        if not args:
            print(Fore.RED + "错误: 请提供要添加的记忆内容" + Style.RESET_ALL)
            print(Fore.YELLOW + "用法: /add_memory <记忆内容>" + Style.RESET_ALL)
            return
        
        memory_content = args.strip()
        try:
            # 获取当前时间戳
            current_time = int(time.time())
            
            # 添加记忆，包含完整字段
            self.agent.long_term_memory.add({
                'content': memory_content,
                'timestamp': current_time,  # 添加时间戳
                'metadata': {
                    'type': 'manual_entry',
                    'timestamp': current_time
                }
            })
            print(Fore.GREEN + f"已添加记忆: {memory_content}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"添加记忆失败: {str(e)}" + Style.RESET_ALL)

    def _cmd_inspect_long_term(self, _):
        """检视所有长期记忆"""
        try:
            with self.agent.long_term_memory._conn as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, timestamp, content, metadata 
                    FROM memories 
                    ORDER BY timestamp DESC
                """)
                memories = cursor.fetchall()
                
                if not memories:
                    print(Fore.YELLOW + "长期记忆为空" + Style.RESET_ALL)
                    return
                
                print(Fore.YELLOW + "\n长期记忆列表:" + Style.RESET_ALL)
                for mem in memories:
                    mem_id, timestamp, content, metadata = mem
                    print(f"{Fore.CYAN}[ID: {mem_id}] {Fore.WHITE}{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}{Style.RESET_ALL}")
                    print(f"  {Fore.GREEN}内容:{Style.RESET_ALL} {content[:100]}{'...' if len(content) > 100 else ''}")
                    if metadata:
                        print(f"  {Fore.BLUE}元数据:{Style.RESET_ALL} {metadata}")
                    print("-" * 50)
                
                print(f"\n共找到 {Fore.CYAN}{len(memories)}{Style.RESET_ALL} 条记忆")
                
        except Exception as e:
            print(Fore.RED + f"查询长期记忆失败: {str(e)}" + Style.RESET_ALL)

    def _cmd_rm_memory(self, args):
        """删除指定记忆"""
        if not args:
            print(Fore.RED + "错误: 请提供要删除的记忆ID" + Style.RESET_ALL)
            print(Fore.YELLOW + "用法: /rm_memory <记忆ID>" + Style.RESET_ALL)
            return
        
        try:
            mem_id = int(args.strip())
            with self.agent.long_term_memory._conn as conn:
                cursor = conn.cursor()
                # 检查记忆是否存在
                cursor.execute("SELECT id FROM memories WHERE id = ?", (mem_id,))
                if not cursor.fetchone():
                    print(Fore.RED + f"错误: 找不到ID为 {mem_id} 的记忆" + Style.RESET_ALL)
                    return
                
                # 确认删除
                confirm = input(Fore.YELLOW + f"确认删除记忆 {mem_id}? (y/n): " + Style.RESET_ALL).lower()
                if confirm != 'y':
                    print(Fore.BLUE + "取消删除" + Style.RESET_ALL)
                    return
                
                # 执行删除
                cursor.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
                cursor.execute("DELETE FROM memory_embeddings WHERE memory_id = ?", (mem_id,))
                conn.commit()
                print(Fore.GREEN + f"已成功删除记忆 {mem_id}" + Style.RESET_ALL)
                
        except ValueError:
            print(Fore.RED + "错误: 记忆ID必须是数字" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"删除记忆失败: {str(e)}" + Style.RESET_ALL)

    def _cmd_flush_long_term(self, _):
        """清空所有长期记忆"""
        try:
            # 第一次确认
            confirm1 = input(Fore.RED + "警告: 这将删除所有长期记忆! 确认继续? (y/n): " + Style.RESET_ALL).lower()
            if confirm1 != 'y':
                print(Fore.BLUE + "取消操作" + Style.RESET_ALL)
                return
            
            # 第二次确认
            confirm2 = input(Fore.RED + "再次确认要清空所有长期记忆? 此操作不可逆! (输入'CONFIRM'继续): " + Style.RESET_ALL)
            if confirm2 != 'CONFIRM':
                print(Fore.BLUE + "取消操作" + Style.RESET_ALL)
                return
            
            # 执行清空
            with self.agent.long_term_memory._conn as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memories")
                cursor.execute("DELETE FROM memory_embeddings")
                conn.commit()
                print(Fore.GREEN + "已清空所有长期记忆" + Style.RESET_ALL)
                
        except Exception as e:
            print(Fore.RED + f"清空记忆失败: {str(e)}" + Style.RESET_ALL)

    def _process_command(self, user_input):
        """处理用户命令"""
        cmd = user_input.split()[0]
        if cmd in self.commands:
            args = user_input[len(cmd):].strip()
            self.commands[cmd]['func'](args)
            return True
        return False

    def start(self):
        """启动应用"""
        self._running = True
        
        # 启动主动发言线程
        self._active_thread = threading.Thread(
            target=self._active_speaking,
            daemon=True
        )
        self._active_thread.start()
        
        # 主交互循环
        print(Fore.GREEN + "\nDeproCognition 已就绪。输入/help查看命令列表。" + Style.RESET_ALL)
        while self._running:
            try:
                # 彩色输入提示
                user_input = input(Fore.BLUE + "You: " + Style.RESET_ALL).strip()
                if not user_input:
                    continue
                    
                if user_input.lower() in ['退出', 'exit', 'quit']:
                    break
                
                # 检查是否是命令
                if user_input.startswith('/'):
                    self._process_command(user_input)
                    continue
                
                # 处理普通消息
                response = self.agent.process_message(user_input)
                print(Fore.MAGENTA + "DeproCognition: " + Style.RESET_ALL + response)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(Fore.RED + f"处理消息时出错: {str(e)}" + Style.RESET_ALL)

    def stop(self):
        """安全停止应用"""
        self._running = False
        try:
            if hasattr(self, '_active_thread') and self._active_thread.is_alive():
                self._active_thread.join(timeout=2)
            
            if hasattr(self, 'agent'):
                # 确保内存被正确释放
                del self.agent
        except Exception as e:
            print(Fore.RED + f"关闭时出错: {e}" + Style.RESET_ALL)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="DeproCognition 智能体系统")
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.yaml', 
        help='配置文件路径（默认: config.yaml）'
    )
    args = parser.parse_args()
    
    try:
        # 初始化应用
        app = DeproCognitionApp(args.config)
        app.start()
    except Exception as e:
        print(Fore.RED + f"应用启动失败: {str(e)}" + Style.RESET_ALL)
    finally:
        if 'app' in locals():
            app.stop()

if __name__ == "__main__":
    main()
# DeproCognition 智能体系统开发文档

## 1. 系统概述

DeproCognition 是一个具有自我感知能力的智能体应用，基于 Ollama/OpenAI API 构建，具备情绪模拟、记忆管理和工具调用等高级功能。系统采用模块化设计，遵循面向对象编程原则，确保代码的可维护性和可扩展性。

## 2. 系统架构

### 2.1 目录结构

```
deprocognition/
├── core/                        # 核心系统模块
│   ├── agent.py                 # 智能体主类
│   ├── memory/                  # 记忆系统
│   ├── state/                   # 心流与情绪系统
│   └── tools/                   # 工具系统
├── interfaces/                  # 接口模块
│   ├── api/                     # API接口实现
│   └── config.py                # 配置管理
├── utils/                       # 实用工具
└── main.py                      # 主入口文件
```

### 2.12 类函数结构

```
main.py
  ├── Class: DeproCognitionApp
  │   ├── Function: __init__
  │   ├── Function: _handle_interrupt
  │   ├── Function: _active_speaking
  │   ├── Function: start
  │   ├── Function: stop
  ├── Function: main
  ├── Function: __init__
  ├── Function: _handle_interrupt
  ├── Function: _active_speaking
  ├── Function: start
  ├── Function: stop
__init__.py
core/__init__.py
core/agent.py
  ├── Class: DeproCognitionAgent
  │   ├── Function: __init__
  │   ├── Function: process_message
  │   ├── Function: _update_states
  │   ├── Function: _generate_response
  │   ├── Function: _get_memory_context
  │   ├── Function: _summarize_conversation
  │   ├── Function: _format_tool_response
  │   ├── Function: initiate_conversation
  │   ├── Function: get_current_state
  │   ├── Function: __del__
  ├── Function: __init__
  ├── Function: process_message
  ├── Function: _update_states
  ├── Function: _generate_response
  ├── Function: _get_memory_context
  ├── Function: _summarize_conversation
  ├── Function: _format_tool_response
  ├── Function: initiate_conversation
  ├── Function: get_current_state
  ├── Function: __del__
core/memory/__init__.py
core/memory/base.py
  ├── Class: BaseMemory
  │   ├── Function: add
  │   ├── Function: retrieve
  │   ├── Function: clear
  ├── Function: add
  ├── Function: retrieve
  ├── Function: clear
core/memory/long_term.py
  ├── Class: LongTermMemory
  │   ├── Function: __init__
  │   ├── Function: _get_conn
  │   ├── Function: _init_db
  │   ├── Function: _init_importance_model
  │   ├── Function: _calculate_importance
  │   ├── Function: _get_embedding
  │   ├── Function: add
  │   ├── Function: retrieve
  │   ├── Function: _retrieve_by_semantic
  │   ├── Function: _retrieve_by_importance
  │   ├── Function: clear
  │   ├── Function: close
  ├── Function: __init__
  ├── Function: _get_conn
  ├── Function: _init_db
  ├── Function: _init_importance_model
  ├── Function: _calculate_importance
  ├── Function: _get_embedding
  ├── Function: add
  ├── Function: retrieve
  ├── Function: _retrieve_by_semantic
  ├── Function: _retrieve_by_importance
  ├── Function: clear
  ├── Function: close
core/memory/short_term.py
  ├── Class: ShortTermMemory
  │   ├── Function: __init__
  │   ├── Function: add
  │   ├── Function: retrieve
  │   ├── Function: clear
  │   ├── Function: get_conversation_history
  ├── Function: __init__
  ├── Function: add
  ├── Function: retrieve
  ├── Function: clear
  ├── Function: get_conversation_history
core/state/__init__.py
core/state/emotion.py
  ├── Class: EmotionState
  │   ├── Function: __init__
  │   ├── Function: _init_personality_matrix
  │   ├── Function: update
  │   ├── Function: _apply_emotion_change
  │   ├── Function: decay
  │   ├── Function: get_state
  │   ├── Function: get_state_description
  │   ├── Function: _analyze_text_emotion
  │   ├── Function: influence_response
  ├── Function: __init__
  ├── Function: _init_personality_matrix
  ├── Function: update
  ├── Function: _apply_emotion_change
  ├── Function: decay
  ├── Function: get_state
  ├── Function: get_state_description
  ├── Function: _analyze_text_emotion
  ├── Function: influence_response
core/state/flow.py
  ├── Class: FlowState
  │   ├── Function: __init__
  │   ├── Function: update
  │   ├── Function: should_respond
  │   ├── Function: should_initiate
  │   ├── Function: get_state
  ├── Function: __init__
  ├── Function: update
  ├── Function: should_respond
  ├── Function: should_initiate
  ├── Function: get_state
core/state/schedule.py
  ├── Class: ScheduleSystem
  │   ├── Function: __init__
  │   ├── Function: generate_daily_schedule
  │   ├── Function: get_current_activity
  │   ├── Function: complete_activity
  │   ├── Function: get_upcoming_activities
  │   ├── Function: update
  ├── Function: __init__
  ├── Function: generate_daily_schedule
  ├── Function: get_current_activity
  ├── Function: complete_activity
  ├── Function: get_upcoming_activities
  ├── Function: update
core/tools/__init__.py
core/tools/context_aware.py
  ├── Class: ContextAwareTools
  │   ├── Function: __init__
  │   ├── Function: _load_tools
  │   ├── Function: tell_joke
  │   ├── Function: searxng_search
  │   ├── Function: calculate
  │   ├── Function: get_time
  │   ├── Function: detect_tool_use
  │   ├── Function: use_tool
  ├── Function: __init__
  ├── Function: _load_tools
  ├── Function: tell_joke
  ├── Function: searxng_search
  ├── Function: calculate
  ├── Function: get_time
  ├── Function: detect_tool_use
  ├── Function: use_tool
interfaces/__init__.py
interfaces/config.py
  ├── Class: ConfigManager
  │   ├── Function: __init__
  │   ├── Function: _load_config
  │   ├── Function: _create_default_config
  │   ├── Function: _save_config
  │   ├── Function: get
  │   ├── Function: update
  ├── Function: __init__
  ├── Function: _load_config
  ├── Function: _create_default_config
  ├── Function: _save_config
  ├── Function: get
  ├── Function: update
interfaces/api/__init__.py
interfaces/api/ollama.py
  ├── Class: OllamaAPI
  │   ├── Function: __init__
  │   ├── Function: generate
  │   ├── Function: chat
  ├── Function: __init__
  ├── Function: generate
  ├── Function: chat
interfaces/api/openai.py
  ├── Class: OpenAIAPI
  │   ├── Function: __init__
  │   ├── Function: chat_completion
  ├── Function: __init__
  ├── Function: chat_completion
utils/__init__.py
utils/helpers.py
  ├── Function: current_timestamp
  ├── Function: format_timestamp
  ├── Function: validate_config
utils/prompts.py
  ├── Class: PromptManager
  │   ├── Function: __init__
  │   ├── Function: render_prompt
  │   ├── Function: get_system_prompt
  │   ├── Function: get_memory_summary_prompt
  │   ├── Function: get_active_prompt
  ├── Function: __init__
  ├── Function: render_prompt
  ├── Function: get_system_prompt
  ├── Function: get_memory_summary_prompt
  ├── Function: get_active_prompt

```

### 2.2 模块依赖关系

```
main.py → DeproCognitionAgent → [Memory, State, Tools]
                             → [OllamaAPI/OpenAIAPI]
                             → ConfigManager
                             → PromptManager
```

## 3. 核心模块说明

### 3.1 Agent 模块 (core/agent.py)

#### DeproCognitionAgent 类

智能体核心类，协调各子系统工作。

**主要方法**:
- `process_message(user_input: str) -> str`: 处理用户输入并生成回复
- `initiate_conversation() -> Optional[str]`: 主动发起对话
- `get_current_state() -> Dict[str, Any]`: 获取当前系统状态

**内部方法**:
- `_update_states()`: 更新情绪和心流状态
- `_generate_response()`: 生成AI回复
- `_summarize_conversation()`: 总结对话存入长期记忆

### 3.2 Memory 模块 (core/memory/)

#### 3.2.1 BaseMemory 抽象类

定义记忆系统基础接口。

**方法**:
- `add()`: 添加记忆项
- `retrieve()`: 检索记忆
- `clear()`: 清空记忆

#### 3.2.2 ShortTermMemory 类

实现短期记忆功能，保存最近对话。

**特性**:
- 基于窗口的存储机制
- 自动维护记忆长度

#### 3.2.3 LongTermMemory 类

实现长期记忆功能，使用SQLite存储。

**增强功能**:
- 向量搜索 (基于Sentence Transformers)
- 记忆重要性评估
- 语义相似度检索

### 3.3 State 模块 (core/state/)

#### 3.3.1 EmotionState 类

管理智能体情绪状态。

**特性**:
- 多维情绪模型 (8种基础情绪)
- 情绪间相互影响矩阵
- 文本情感分析
- 回复风格影响

#### 3.3.2 FlowState 类

管理心流状态。

**功能**:
- 活动类型影响评估
- 响应概率计算
- 主动发言判断

#### 3.3.3 ScheduleSystem 类

动态日程管理系统。

**功能**:
- 每日日程生成
- 活动状态跟踪
- 即将到来活动提醒

### 3.4 Tools 模块 (core/tools/)

#### ContextAwareTools 类

上下文感知工具系统。

**内置工具**:
- 计算器
- 时间查询
- Searxng搜索
- 讲笑话

**特性**:
- 模糊匹配触发
- 多工具集成

## 4. 接口模块 (interfaces/)

### 4.1 ConfigManager 类

统一配置管理系统。

**功能**:
- YAML配置读写
- 默认配置生成
- 多级配置访问

### 4.2 API 接口

#### OllamaAPI 类
- 支持generate和chat两种模式

#### OpenAIAPI 类
- 支持chat completion接口

## 5. 实用工具 (utils/)

### 5.1 PromptManager 类

提示词模板管理。

**功能**:
- 变量替换
- 多场景提示词支持

### 5.2 Helpers 工具函数

- 时间戳处理
- 配置验证

## 6. 主要工作流程

### 6.1 消息处理流程

1. 接收用户输入
2. 更新短期记忆
3. 分析情绪影响
4. 检查工具使用
5. 生成上下文感知回复
6. 更新对话计数
7. 定期总结长期记忆

### 6.2 主动发言流程

1. 每分钟检查一次
2. 评估心流状态
3. 生成主动发言提示
4. 决定是否发言
5. 更新记忆

## 7. 配置说明

系统通过`config.yaml`进行配置，主要配置项包括:

```yaml
api:
  provider: ollama  # ollama或openai
  ollama:
    base_url: http://localhost:11434
    model: llama2
  openai:
    api_key: ""
    model: gpt-3.5-turbo

memory:
  short_term:
    window_size: 10
  long_term:
    summary_interval: 10

emotion:
  initial_state:  # 初始情绪值
    happiness: 0.5
    sadness: 0.2
  decay_rate: 0.95  # 情绪衰减率

searxng:
  base_url: http://localhost:8080
  engines: [google, bing]
  result_count: 3
```

## 8. 扩展开发指南

### 8.1 添加新工具

1. 在`ContextAwareTools`类中添加工具方法
2. 更新`_load_tools()`方法注册新工具
3. 在`detect_tool_use()`中添加触发逻辑

### 8.2 自定义情绪规则

1. 修改`EmotionState`类中的`_init_personality_matrix()`
2. 添加新的情绪更新规则
3. 调整`influence_response()`中的风格影响

### 8.3 集成新API

1. 在`interfaces/api/`下创建新API类
2. 实现与现有API相同的接口
3. 更新`ConfigManager`支持新配置

## 9. 部署说明

### 9.1 依赖安装

```bash
pip install -r requirements.txt
```

### 9.2 初始化配置

首次运行会自动生成默认配置文件`config.yaml`

### 9.3 运行系统

```bash
python main.py
```

## 10. 性能考虑

1. 长期记忆使用SQLite优化查询
2. 向量嵌入使用轻量级模型
3. 情绪计算采用矩阵运算优化
4. 记忆总结异步执行

## 11. 已知限制

1. 中文情感分析精度有限
2. 向量搜索性能随记忆量增长下降
3. 情绪模型基于简化规则

## 12. 未来改进方向

1. 实现记忆分级存储
2. 添加多模态能力
3. 增强情感分析模型
4. 支持插件式工具扩展

---

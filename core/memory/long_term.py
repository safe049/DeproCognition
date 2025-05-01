import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer
from .base import BaseMemory
from interfaces.config import ConfigManager
from utils.helpers import current_timestamp
import threading

class LongTermMemory(BaseMemory):
    def __init__(self, config: ConfigManager):
        self.config = config
        storage_path = self.config.get('memory.long_term.storage_path', 'memory/long_term.db')
        Path(storage_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 使用线程局部存储
        self._local = threading.local()
        self._storage_path = storage_path
        self._init_db()
        
        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
        self.embedding_size = 384
        # 初始化重要性评估模型
        self.importance_model = None
        self._init_importance_model()
    
    @property
    def _conn(self):
        """线程安全的数据库连接属性"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                self._storage_path,
                check_same_thread=False,
                timeout=30  # 增加超时时间
            )
            # 启用WAL模式提高并发性能
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
        return self._local.conn

    def _init_db(self):
        """初始化数据库表结构"""
        with self._conn as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                importance REAL DEFAULT 0.5,
                metadata TEXT
            )""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_embeddings (
                memory_id INTEGER PRIMARY KEY,
                embedding BLOB,
                FOREIGN KEY(memory_id) REFERENCES memories(id)
            )""")
            conn.commit()

    
    def _init_importance_model(self):
        """初始化重要性评估模型"""
        # 实际应用中可以使用更复杂的模型
        # 这里使用简单的基于规则的评估
        pass
    
    def _calculate_importance(self, content: str) -> float:
        """计算记忆重要性 (0-1)"""
        # 简单规则: 包含特定关键词的记忆更重要
        important_keywords = ['重要', '记住', '关键', '必须', '紧急']
        if any(keyword in content for keyword in important_keywords):
            return min(1.0, 0.7 + random.random() * 0.3)
        return max(0.1, random.random() * 0.6)
    
    def _get_embedding(self, text: str) -> bytes:
        """获取文本的嵌入向量"""
        embedding = self.embedding_model.encode(text)
        return embedding.tobytes()
    

    def add(self, item: Dict[str, Any]):
        """添加记忆项"""
        with self._conn as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (timestamp, content, importance, metadata) VALUES (?, ?, ?, ?)",
                (item.get('timestamp'), item.get('content'), item.get('importance', 0.5), str(item.get('metadata', {})))
            )
            memory_id = cursor.lastrowid
            
            # 生成并存储嵌入向量
            if 'content' in item:
                embedding = self.embedding_model.encode(item['content'])
                cursor.execute(
                    "INSERT INTO memory_embeddings (memory_id, embedding) VALUES (?, ?)",
                    (memory_id, sqlite3.Binary(embedding.tobytes()))
                )
            conn.commit()
    
    def retrieve(self, query: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """检索长期记忆 (增强版)"""
        if not query:
            return self._retrieve_by_importance(limit)
        
        # 向量相似度搜索
        return self._retrieve_by_semantic(query, limit)
    
    def _retrieve_by_semantic(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """基于语义相似度的记忆检索"""
        # 获取查询的嵌入向量
        with self._conn as conn:
            query_embedding = self.embedding_model.encode(query)
            query_blob = sqlite3.Binary(query_embedding.tobytes())
            
            # 执行相似度搜索 (使用余弦相似度)
            cursor = conn.cursor()
            cursor.execute("""
            SELECT m.id, m.timestamp, m.content, m.importance, m.metadata
            FROM memories m
            JOIN memory_embeddings e ON m.id = e.memory_id
            ORDER BY (
                SELECT SUM(v1.value * v2.value)
                FROM (
                    SELECT rowid, value FROM json_each(
                        json_array(hex(e.embedding))
                    ) WHERE json_valid(hex(e.embedding))
                ) v1
                JOIN (
                    SELECT rowid, value FROM json_each(
                        json_array(?)
                    ) WHERE json_valid(?)
                ) v2 ON v1.rowid = v2.rowid
            ) DESC
            LIMIT ?
            """, (query_blob, query_blob, limit))
            
            rows = cursor.fetchall()
            return [{
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'importance': row[3],
                'metadata': eval(row[4]) if row[4] else {}
            } for row in rows]
    
    def _retrieve_by_importance(self, limit: int) -> List[Dict[str, Any]]:
        """基于重要性的记忆检索"""
        with self._conn as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, timestamp, content, importance, metadata FROM memories
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [{
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'importance': row[3],
                'metadata': eval(row[4]) if row[4] else {}
            } for row in rows]

    def clear(self):
  
        with self._conn as conn:
            conn.execute("DELETE FROM memories")
            conn.execute("DELETE FROM memory_embeddings")
            conn.commit()

    def close(self):
        """安全关闭连接"""
        if hasattr(self._local, 'conn'):
            try:
                self._local.conn.close()
            except:
                pass
            finally:
                del self._local.conn

    def __del__(self):
        """析构时自动关闭"""
        self.close()
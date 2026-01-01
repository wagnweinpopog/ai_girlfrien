#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 记忆系统模块（修正版）
负责长期记忆的存储、检索和管理
线程安全的SQLite连接
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import pickle
import threading

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logging.warning("ChromaDB未安装，将使用简化记忆系统")

class MemorySystem:
    """记忆系统 - 管理长期和短期记忆（线程安全版）"""
    
    def __init__(self, config_manager):
        """
        初始化记忆系统
        
        参数:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger("MemorySystem")
        self.config = config_manager
        
        # 获取数据路径
        data_path = Path(self.config.get('env.system.data_path', './data'))
        self.memory_path = data_path / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径（不立即连接）
        self.db_path = self.memory_path / "memories.db"
        
        # 线程本地存储
        self.local = threading.local()
        
        # 初始化向量数据库（如果可用）
        self.vector_db = None
        if CHROMA_AVAILABLE:
            self._init_vector_database()
        else:
            self.logger.warning("使用简化记忆检索（安装chromadb可获得更好效果）")
        
        # 内存缓存
        self.short_term_cache = []
        self.cache_size = 20
        
        # 初始化数据库表
        self._init_database()
        
        # 加载现有记忆
        self.load_existing_memories()
        
        self.logger.info(f"记忆系统初始化完成，数据库: {self.db_path}")
    
    def _get_db_connection(self):
        """获取线程安全的数据库连接"""
        if not hasattr(self.local, 'conn'):
            # 为当前线程创建新连接
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.cursor = self.local.conn.cursor()
            self._create_tables(self.local.cursor)
            self.local.conn.commit()
        
        return self.local.conn, self.local.cursor
    
    def _create_tables(self, cursor):
        """创建数据库表"""
        # 创建记忆表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            importance INTEGER DEFAULT 50,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            accessed_count INTEGER DEFAULT 0,
            last_accessed DATETIME,
            expiration_date DATETIME,
            tags TEXT
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON memories(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)')
        
        # 创建关系表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_relations (
            memory_id INTEGER,
            related_id INTEGER,
            relation_type TEXT,
            strength REAL DEFAULT 1.0,
            FOREIGN KEY (memory_id) REFERENCES memories (id),
            FOREIGN KEY (related_id) REFERENCES memories (id)
        )
        ''')
    
    def _init_database(self):
        """初始化数据库（只创建文件）"""
        # 确保数据库文件存在
        if not self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            self._create_tables(cursor)
            conn.commit()
            conn.close()
    
    def _init_vector_database(self):
        """初始化向量数据库（用于语义搜索）"""
        try:
            vector_db_path = self.memory_path / "vector_db"
            vector_db_path.mkdir(exist_ok=True)
            
            self.vector_client = chromadb.PersistentClient(
                path=str(vector_db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 获取或创建集合
            self.vector_collection = self.vector_client.get_or_create_collection(
                name="memory_embeddings",
                metadata={"hnsw:space": "cosine"}
            )
            
            self.logger.info("向量数据库初始化完成")
            
        except Exception as e:
            self.logger.error(f"向量数据库初始化失败: {e}")
            self.vector_collection = None
    
    def load_existing_memories(self):
        """加载现有记忆到缓存"""
        try:
            conn, cursor = self._get_db_connection()
            
            # 加载最近的重要记忆
            cursor.execute('''
                SELECT id, memory_type, content, metadata, importance, timestamp 
                FROM memories 
                WHERE importance >= 70 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (self.cache_size,))
            
            rows = cursor.fetchall()
            for row in rows:
                memory = {
                    'id': row[0],
                    'type': row[1],
                    'content': json.loads(row[2]),
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'importance': row[4],
                    'timestamp': datetime.fromisoformat(row[5])
                }
                self.short_term_cache.append(memory)
            
            self.logger.info(f"加载了 {len(rows)} 条重要记忆到缓存")
            
        except Exception as e:
            self.logger.error(f"加载记忆失败: {e}")
    
    def record_conversation(self, user_message: str, ai_response: str, 
                           context: Dict[str, Any]):
        """
        记录对话
        
        参数:
            user_message: 用户消息
            ai_response: AI回复
            context: 上下文信息
        """
        try:
            conn, cursor = self._get_db_connection()
            
            # 构建记忆内容
            memory_content = {
                'user': user_message,
                'ai': ai_response,
                'context': {
                    'emotion': context.get('emotion', {}),
                    'timestamp': datetime.now().isoformat(),
                    'message_type': context.get('message_type', 'text')
                }
            }
            
            # 计算重要性
            importance = self._calculate_conversation_importance(user_message, ai_response, context)
            
            # 提取关键词
            keywords = self._extract_keywords(user_message + " " + ai_response)
            
            # 保存到数据库
            cursor.execute('''
                INSERT INTO memories 
                (memory_type, content, metadata, importance, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'conversation',
                json.dumps(memory_content, ensure_ascii=False),
                json.dumps({
                    'user_id': context.get('user_id', 'unknown'),
                    'length': len(user_message) + len(ai_response),
                    'emotion_at_time': context.get('emotion', {})
                }, ensure_ascii=False),
                importance,
                ','.join(keywords[:5]) if keywords else ''
            ))
            
            memory_id = cursor.lastrowid
            
            # 添加到向量数据库（如果可用）
            if hasattr(self, 'vector_collection') and self.vector_collection:
                self._add_to_vector_db(memory_id, f"{user_message} {ai_response}")
            
            # 更新缓存
            memory_entry = {
                'id': memory_id,
                'type': 'conversation',
                'content': memory_content,
                'importance': importance,
                'timestamp': datetime.now()
            }
            
            self._add_to_cache(memory_entry)
            
            # 建立关系
            self._establish_relations(memory_id, keywords)
            
            conn.commit()
            
            self.logger.debug(f"记录对话记忆 ID: {memory_id}, 重要性: {importance}")
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"记录对话失败: {e}")
            return None
    
    def record_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        记录事件
        
        参数:
            event_type: 事件类型
            event_data: 事件数据
        """
        try:
            conn, cursor = self._get_db_connection()
            
            importance = event_data.get('importance', 50)
            
            cursor.execute('''
                INSERT INTO memories 
                (memory_type, content, metadata, importance)
                VALUES (?, ?, ?, ?)
            ''', (
                'event',
                json.dumps(event_data, ensure_ascii=False),
                json.dumps({
                    'event_type': event_type,
                    'recorded_at': datetime.now().isoformat()
                }, ensure_ascii=False),
                importance
            ))
            
            memory_id = cursor.lastrowid
            conn.commit()
            
            self.logger.info(f"记录事件: {event_type}, ID: {memory_id}")
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"记录事件失败: {e}")
            return None

    def record_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """记录交互（接收/发送消息）"""
        return self.record_event(f'interaction_{interaction_type}', data)
    
    def _calculate_conversation_importance(self, user_message: str, 
                                         ai_response: str, 
                                         context: Dict) -> int:
        """计算对话重要性"""
        importance = 50  # 基础值
        
        # 基于长度
        total_length = len(user_message) + len(ai_response)
        if total_length > 500:
            importance += 10
        elif total_length < 50:
            importance -= 10
        
        # 基于情感强度
        emotion = context.get('emotion', {})
        if emotion:
            intensity = abs(emotion.get('happiness', 50) - 50) / 50.0
            importance += int(intensity * 20)
        
        # 包含关键词
        important_keywords = ['爱', '喜欢', '重要', '永远', '承诺', '生日', '纪念日']
        if any(keyword in user_message for keyword in important_keywords):
            importance += 15
        
        # 限制在1-100范围内
        return max(1, min(100, importance))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化版）"""
        # 中文停用词
        stopwords = {'的', '了', '和', '是', '在', '我', '你', '他', '她', '它', 
                    '这', '那', '有', '就', '都', '也', '还', '但', '而', '吗'}
        
        # 简单分词
        words = []
        current_word = ""
        
        for char in text:
            if char.isalnum() or '\u4e00' <= char <= '\u9fff':
                current_word += char
            else:
                if current_word and len(current_word) > 1 and current_word not in stopwords:
                    words.append(current_word)
                current_word = ""
        
        if current_word and len(current_word) > 1 and current_word not in stopwords:
            words.append(current_word)
        
        # 去重并返回前10个
        return list(dict.fromkeys(words))[:10]
    
    def _add_to_vector_db(self, memory_id: int, text: str):
        """添加到向量数据库"""
        if not hasattr(self, 'vector_collection') or not self.vector_collection:
            return
        
        try:
            # 这里应该有文本向量化，但简化处理
            self.vector_collection.add(
                documents=[text],
                metadatas=[{"memory_id": memory_id, "type": "conversation"}],
                ids=[f"memory_{memory_id}"]
            )
        except Exception as e:
            self.logger.warning(f"添加到向量数据库失败: {e}")
    
    def _add_to_cache(self, memory: Dict):
        """添加到缓存"""
        self.short_term_cache.insert(0, memory)
        
        # 保持缓存大小
        if len(self.short_term_cache) > self.cache_size:
            self.short_term_cache = self.short_term_cache[:self.cache_size]
    
    def _establish_relations(self, new_memory_id: int, keywords: List[str]):
        """建立记忆关系"""
        if not keywords:
            return
        
        try:
            conn, cursor = self._get_db_connection()
            
            # 查找相关记忆
            tag_conditions = []
            params = []
            
            for kw in keywords[:3]:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{kw}%")
            
            if tag_conditions:
                query = f'''
                    SELECT id FROM memories 
                    WHERE id != ? AND ({' OR '.join(tag_conditions)})
                    ORDER BY importance DESC, timestamp DESC 
                    LIMIT 3
                '''
                
                params.insert(0, new_memory_id)
                
                cursor.execute(query, params)
                
                related_ids = [row[0] for row in cursor.fetchall()]
                
                # 建立关系
                for related_id in related_ids:
                    cursor.execute('''
                        INSERT INTO memory_relations (memory_id, related_id, relation_type)
                        VALUES (?, ?, ?)
                    ''', (new_memory_id, related_id, 'semantic'))
                
                conn.commit()
                
        except Exception as e:
            self.logger.warning(f"建立关系失败: {e}")
    
    def retrieve_related_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """检索相关记忆"""
        memories = []
        
        try:
            conn, cursor = self._get_db_connection()
            
            # 先尝试向量搜索（如果可用）
            if hasattr(self, 'vector_collection') and self.vector_collection and len(query) > 2:
                try:
                    results = self.vector_collection.query(
                        query_texts=[query],
                        n_results=min(limit, 10)
                    )
                    
                    if results['ids'][0]:
                        # 从数据库获取完整记忆
                        placeholders = ','.join(['?'] * len(results['ids'][0]))
                        cursor.execute(f'''
                            SELECT id, memory_type, content, metadata, importance, timestamp
                            FROM memories 
                            WHERE id IN ({placeholders})
                            ORDER BY importance DESC
                        ''', results['ids'][0])
                        
                        for row in cursor.fetchall():
                            memories.append({
                                'id': row[0],
                                'type': row[1],
                                'content': json.loads(row[2]),
                                'metadata': json.loads(row[3]) if row[3] else {},
                                'importance': row[4],
                                'timestamp': datetime.fromisoformat(row[5]),
                                'source': 'vector_search'
                            })
                except Exception as e:
                    self.logger.warning(f"向量搜索失败: {e}")
            
            # 如果向量搜索结果不足，使用关键词搜索
            if len(memories) < limit:
                keywords = self._extract_keywords(query)
                if keywords:
                    tag_conditions = []
                    params = []
                    
                    for kw in keywords[:3]:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{kw}%")
                    
                    if tag_conditions:
                        keyword_query = '''
                            SELECT id, memory_type, content, metadata, importance, timestamp
                            FROM memories 
                            WHERE ''' + ' OR '.join(tag_conditions) + '''
                            ORDER BY importance DESC, timestamp DESC 
                            LIMIT ?
                        '''
                        
                        params.append(limit - len(memories))
                        
                        cursor.execute(keyword_query, params)
                        
                        for row in cursor.fetchall():
                            # 避免重复
                            if not any(m['id'] == row[0] for m in memories):
                                memories.append({
                                    'id': row[0],
                                    'type': row[1],
                                    'content': json.loads(row[2]),
                                    'metadata': json.loads(row[3]) if row[3] else {},
                                    'importance': row[4],
                                    'timestamp': datetime.fromisoformat(row[5]),
                                    'source': 'keyword_search'
                                })
            
            # 更新访问计数
            for memory in memories:
                cursor.execute('''
                    UPDATE memories 
                    SET accessed_count = accessed_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (memory['id'],))
            
            conn.commit()
            
            return memories
            
        except Exception as e:
            self.logger.error(f"检索记忆失败: {e}")
            return []
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """获取最近的记忆"""
        try:
            conn, cursor = self._get_db_connection()
            
            cursor.execute('''
                SELECT id, memory_type, content, metadata, importance, timestamp
                FROM memories 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            memories = []
            for row in cursor.fetchall():
                memories.append({
                    'id': row[0],
                    'type': row[1],
                    'content': json.loads(row[2]),
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'importance': row[4],
                    'timestamp': datetime.fromisoformat(row[5])
                })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"获取最近记忆失败: {e}")
            return []
    
    def get_last_interaction_time(self):
        """获取最后互动时间"""
        try:
            conn, cursor = self._get_db_connection()
            
            cursor.execute('''
                SELECT timestamp FROM memories 
                WHERE memory_type LIKE 'interaction_%' 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                return datetime.fromisoformat(row[0])
            return None
            
        except Exception as e:
            self.logger.error(f"获取最后互动时间失败: {e}")
            return None
    
def consolidate_memories(self):
    """整理记忆（清理、归档、提升重要性等）- 兼容SQLite版本"""
    try:
        conn, cursor = self._get_db_connection()
        
        # 1. 清理过期记忆
        cursor.execute('''
            DELETE FROM memories 
            WHERE expiration_date IS NOT NULL 
            AND expiration_date < CURRENT_TIMESTAMP
        ''')
        
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            self.logger.info(f"清理了 {deleted_count} 条过期记忆")
        
        # 2. 提升频繁访问记忆的重要性（使用CASE替代LEAST）
        cursor.execute('''
            UPDATE memories 
            SET importance = CASE 
                WHEN importance + 5 > 100 THEN 100 
                ELSE importance + 5 
            END
            WHERE accessed_count >= 10 
            AND importance < 90
        ''')
        
        updated_count = cursor.rowcount
        if updated_count > 0:
            self.logger.info(f"提升了 {updated_count} 条记忆的重要性")
        
        # 3. 降低长期未访问记忆的重要性（使用CASE替代GREATEST）
        cursor.execute('''
            UPDATE memories 
            SET importance = CASE 
                WHEN importance - 2 < 1 THEN 1 
                ELSE importance - 2 
            END
            WHERE last_accessed IS NOT NULL 
            AND julianday('now') - julianday(last_accessed) > 30 
            AND importance > 20
        ''')
        
        conn.commit()
        
        # 4. 重新加载缓存
        self.load_existing_memories()
        
        self.logger.info("记忆整理完成")
        
    except Exception as e:
        self.logger.error(f"记忆整理失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            conn, cursor = self._get_db_connection()
            
            stats = {}
            
            # 记忆总数
            cursor.execute('SELECT COUNT(*) FROM memories')
            stats['total_memories'] = cursor.fetchone()[0]
            
            # 按类型统计
            cursor.execute('''
                SELECT memory_type, COUNT(*) 
                FROM memories 
                GROUP BY memory_type
            ''')
            
            stats['by_type'] = dict(cursor.fetchall())
            
            # 平均重要性
            cursor.execute('SELECT AVG(importance) FROM memories')
            avg_importance = cursor.fetchone()[0]
            stats['avg_importance'] = round(avg_importance or 0, 2)
            
            # 缓存大小
            stats['cache_size'] = len(self.short_term_cache)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取统计失败: {e}")
            return {}
    
    def save_state(self):
        """保存状态"""
        # 数据库已经自动保存，这里只需记录日志
        self.logger.info("记忆系统状态已保存")
    
    def close_connections(self):
        """关闭所有数据库连接"""
        try:
            if hasattr(self.local, 'conn'):
                self.local.conn.close()
                del self.local.conn
                del self.local.cursor
        except:
            pass
    
    def __del__(self):
        """清理资源"""
        self.close_connections()
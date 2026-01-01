#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 状态管理器模块
管理系统状态、数据持久化和状态恢复
参考：Flask/Django的状态管理机制
"""

import json
import pickle
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import sqlite3

class StateManager:
    """状态管理器 - 管理系统状态和数据持久化"""
    
    def __init__(self, config_manager):
        """
        初始化状态管理器
        
        参数:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger("StateManager")
        self.config = config_manager
        
        # 获取数据路径
        self.data_path = Path(self.config.get('env.system.data_path', './data'))
        self.state_dir = self.data_path / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态字典
        self.system_state = self._initialize_system_state()
        
        # 状态锁（线程安全）
        self.state_lock = threading.RLock()
        
        # 自动保存间隔（秒）
        self.auto_save_interval = 300  # 5分钟
        self.last_auto_save = datetime.now()
        
        # 初始化数据库
        self._init_database()
        
        # 加载保存的状态
        self.load_all_states()
        
        self.logger.info("状态管理器初始化完成")
    
    def _initialize_system_state(self) -> Dict[str, Any]:
        """初始化系统状态"""
        return {
            'system': {
                'startup_time': datetime.now().isoformat(),
                'version': '1.0.0',
                'runtime': 0,  # 运行时间（秒）
                'last_backup': None,
                'backup_count': 0
            },
            'interactions': {
                'total_count': 0,
                'today_count': 0,
                'last_interaction': None,
                'user_stats': {},  # 用户统计
                'message_types': {}  # 消息类型统计
            },
            'performance': {
                'avg_response_time': 0,
                'success_rate': 100,
                'error_count': 0,
                'last_error': None
            },
            'resources': {
                'memory_usage': 0,
                'disk_usage': 0,
                'api_calls_today': 0,
                'last_resource_check': None
            },
            'relationships': {
                'active_users': 0,
                'total_users': 0,
                'avg_closeness': 50,
                'avg_trust': 50
            }
        }
    
    def _init_database(self):
        """初始化SQLite数据库"""
        db_path = self.state_dir / "state.db"
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # 创建状态表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            data_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建交互记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS interaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message_type TEXT,
            message_length INTEGER,
            response_time REAL,
            success BOOLEAN,
            error_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
        ''')
        
        # 创建用户统计表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id TEXT PRIMARY KEY,
            interaction_count INTEGER DEFAULT 0,
            last_interaction DATETIME,
            total_message_length INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_user ON interaction_logs(user_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_time ON interaction_logs(timestamp)')
        
        self.conn.commit()
    
    def load_all_states(self):
        """加载所有保存的状态"""
        with self.state_lock:
            try:
                # 从数据库加载系统状态
                self._load_from_database()
                
                # 从文件加载其他状态
                self._load_from_files()
                
                self.logger.info("所有状态已加载")
                
            except Exception as e:
                self.logger.error(f"加载状态失败: {e}")
    
    def _load_from_database(self):
        """从数据库加载状态"""
        try:
            # 加载系统状态
            self.cursor.execute('SELECT key, value, data_type FROM system_state')
            rows = self.cursor.fetchall()
            
            for key, value, data_type in rows:
                if data_type == 'json':
                    parsed_value = json.loads(value)
                elif data_type == 'int':
                    parsed_value = int(value)
                elif data_type == 'float':
                    parsed_value = float(value)
                elif data_type == 'bool':
                    parsed_value = value.lower() == 'true'
                else:
                    parsed_value = value
                
                # 更新系统状态
                self._set_nested_state(key, parsed_value)
            
            self.logger.debug(f"从数据库加载了 {len(rows)} 条状态记录")
            
        except Exception as e:
            self.logger.error(f"从数据库加载失败: {e}")
    
    def _load_from_files(self):
        """从文件加载状态"""
        try:
            # 检查状态文件
            state_files = ['interactions', 'performance', 'relationships']
            
            for file_name in state_files:
                file_path = self.state_dir / f"{file_name}.json"
                
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.system_state[file_name].update(data)
                    self.logger.debug(f"从文件加载: {file_name}")
            
        except Exception as e:
            self.logger.error(f"从文件加载失败: {e}")
    
    def _set_nested_state(self, key: str, value: Any):
        """设置嵌套状态值"""
        keys = key.split('.')
        current = self.system_state
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def save_state(self, category: str, data: Dict[str, Any]):
        """保存状态"""
        with self.state_lock:
            try:
                if category in self.system_state:
                    self.system_state[category].update(data)
                else:
                    self.system_state[category] = data
                
                # 保存到数据库
                self._save_to_database(category, data)
                
                # 定期保存到文件
                self._check_auto_save()
                
                self.logger.debug(f"状态已保存: {category}")
                
            except Exception as e:
                self.logger.error(f"保存状态失败: {e}")
    
    def _save_to_database(self, category: str, data: Dict[str, Any]):
        """保存到数据库"""
        try:
            # 将数据转换为JSON
            json_data = json.dumps(data, ensure_ascii=False)
            
            # 检查是否已存在
            self.cursor.execute(
                'SELECT key FROM system_state WHERE key = ?',
                (category,)
            )
            
            if self.cursor.fetchone():
                # 更新现有记录
                self.cursor.execute('''
                    UPDATE system_state 
                    SET value = ?, data_type = 'json', updated_at = CURRENT_TIMESTAMP
                    WHERE key = ?
                ''', (json_data, category))
            else:
                # 插入新记录
                self.cursor.execute('''
                    INSERT INTO system_state (key, value, data_type)
                    VALUES (?, ?, 'json')
                ''', (category, json_data))
            
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"保存到数据库失败: {e}")
            self.conn.rollback()
    
    def _check_auto_save(self):
        """检查是否需要自动保存"""
        current_time = datetime.now()
        
        if (current_time - self.last_auto_save).total_seconds() >= self.auto_save_interval:
            self._auto_save_to_files()
            self.last_auto_save = current_time
    
    def _auto_save_to_files(self):
        """自动保存到文件"""
        try:
            # 保存主要状态类别到文件
            for category in ['interactions', 'performance', 'relationships']:
                if category in self.system_state:
                    file_path = self.state_dir / f"{category}.json"
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.system_state[category], f, ensure_ascii=False, indent=2)
            
            self.logger.debug("状态已自动保存到文件")
            
        except Exception as e:
            self.logger.error(f"自动保存到文件失败: {e}")
    
    def load_state(self, category: str) -> Optional[Dict[str, Any]]:
        """加载状态"""
        with self.state_lock:
            return self.system_state.get(category, {}).copy()
    
    def update_interaction_count(self):
        """更新交互计数"""
        with self.state_lock:
            interactions = self.system_state['interactions']
            
            interactions['total_count'] += 1
            interactions['today_count'] += 1
            
            # 检查是否是新的一天
            current_date = datetime.now().date()
            last_interaction = interactions.get('last_interaction')
            
            if last_interaction:
                last_date = datetime.fromisoformat(last_interaction).date()
                if last_date != current_date:
                    interactions['today_count'] = 1
            
            interactions['last_interaction'] = datetime.now().isoformat()
    
    def log_interaction(self, user_id: str, message_type: str, 
                       message_length: int, response_time: float,
                       success: bool = True, error_message: str = None,
                       metadata: Dict[str, Any] = None):
        """记录交互日志"""
        with self.state_lock:
            try:
                # 插入交互记录
                self.cursor.execute('''
                    INSERT INTO interaction_logs 
                    (user_id, message_type, message_length, response_time, 
                     success, error_message, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    message_type,
                    message_length,
                    response_time,
                    success,
                    error_message,
                    json.dumps(metadata) if metadata else None
                ))
                
                # 更新用户统计
                self._update_user_stats(user_id, message_length, response_time, success)
                
                # 更新性能统计
                self._update_performance_stats(response_time, success)
                # 更新消息类型统计
                self._update_message_type_stats(message_type)
                
                self.conn.commit()
                
            except Exception as e:
                self.logger.error(f"记录交互日志失败: {e}")
                self.conn.rollback()
    
    def _update_user_stats(self, user_id: str, message_length: int, 
                          response_time: float, success: bool):
        """更新用户统计"""
        # 检查用户是否存在
        self.cursor.execute(
            'SELECT interaction_count, total_message_length, avg_response_time FROM user_stats WHERE user_id = ?',
            (user_id,)
        )
        
        row = self.cursor.fetchone()
        
        current_time = datetime.now().isoformat()
        
        if row:
            # 更新现有用户
            interaction_count, total_length, avg_response = row
            
            new_count = interaction_count + 1
            new_length = total_length + message_length
            
            # 计算新的平均响应时间
            if success:
                new_avg = (avg_response * interaction_count + response_time) / new_count
            else:
                new_avg = avg_response
            
            self.cursor.execute('''
                UPDATE user_stats 
                SET interaction_count = ?, 
                    total_message_length = ?,
                    avg_response_time = ?,
                    last_interaction = ?,
                    updated_at = ?
                WHERE user_id = ?
            ''', (new_count, new_length, new_avg, current_time, current_time, user_id))
        else:
            # 插入新用户
            self.cursor.execute('''
                INSERT INTO user_stats 
                (user_id, interaction_count, total_message_length, 
                 avg_response_time, last_interaction)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, 1, message_length, response_time if success else 0, current_time))
        
        # 更新系统状态中的用户统计
        interactions = self.system_state['interactions']
        
        if user_id not in interactions['user_stats']:
            interactions['user_stats'][user_id] = {
                'interaction_count': 0,
                'last_interaction': None
            }
            interactions['active_users'] = len(interactions['user_stats'])
        
        interactions['user_stats'][user_id]['interaction_count'] += 1
        interactions['user_stats'][user_id]['last_interaction'] = current_time
    
    def _update_performance_stats(self, response_time: float, success: bool):
        """更新性能统计"""
        performance = self.system_state['performance']
        
        # 更新平均响应时间
        total_requests = performance.get('total_requests', 0) + 1
        
        current_avg = performance.get('avg_response_time', 0)
        new_avg = (current_avg * (total_requests - 1) + response_time) / total_requests
        
        performance['avg_response_time'] = new_avg
        performance['total_requests'] = total_requests
        
        if not success:
            performance['error_count'] = performance.get('error_count', 0) + 1
            performance['last_error'] = datetime.now().isoformat()
        
        # 计算成功率
        if total_requests > 0:
            error_count = performance.get('error_count', 0)
            performance['success_rate'] = ((total_requests - error_count) / total_requests) * 100
    
    def _update_message_type_stats(self, message_type: str):
        """更新消息类型统计"""
        interactions = self.system_state['interactions']
        
        if 'message_types' not in interactions:
            interactions['message_types'] = {}
        
        if message_type not in interactions['message_types']:
            interactions['message_types'][message_type] = 0
        
        interactions['message_types'][message_type] += 1
    
    def get_interaction_count(self) -> int:
        """获取交互计数"""
        with self.state_lock:
            return self.system_state['interactions']['total_count']
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户统计"""
        with self.state_lock:
            try:
                self.cursor.execute('''
                    SELECT interaction_count, total_message_length, 
                           avg_response_time, last_interaction, created_at
                    FROM user_stats 
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = self.cursor.fetchone()
                
                if row:
                    return {
                        'interaction_count': row[0],
                        'total_message_length': row[1],
                        'avg_response_time': row[2],
                        'last_interaction': row[3],
                        'created_at': row[4]
                    }
                
                return None
                
            except Exception as e:
                self.logger.error(f"获取用户统计失败: {e}")
                return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        with self.state_lock:
            stats = {}
            
            # 基本统计
            stats['system'] = {
                'runtime': self._calculate_runtime(),
                'version': self.system_state['system']['version'],
                'startup_time': self.system_state['system']['startup_time']
            }
            
            # 交互统计
            interactions = self.system_state['interactions']
            stats['interactions'] = {
                'total': interactions['total_count'],
                'today': interactions['today_count'],
                'active_users': interactions.get('active_users', 0),
                'total_users': interactions.get('total_users', 0)
            }
            
            # 性能统计
            performance = self.system_state['performance']
            stats['performance'] = {
                'avg_response_time': performance.get('avg_response_time', 0),
                'success_rate': performance.get('success_rate', 100),
                'error_count': performance.get('error_count', 0)
            }
            
            # 资源使用
            stats['resources'] = self._calculate_resource_usage()
            
            return stats
    
    def _calculate_runtime(self) -> str:
        """计算运行时间"""
        try:
            startup_time = datetime.fromisoformat(self.system_state['system']['startup_time'])
            runtime_seconds = (datetime.now() - startup_time).total_seconds()
            
            # 转换为易读格式
            days = int(runtime_seconds // 86400)
            hours = int((runtime_seconds % 86400) // 3600)
            minutes = int((runtime_seconds % 3600) // 60)
            seconds = int(runtime_seconds % 60)
            
            if days > 0:
                return f"{days}天{hours}小时"
            elif hours > 0:
                return f"{hours}小时{minutes}分钟"
            elif minutes > 0:
                return f"{minutes}分钟{seconds}秒"
            else:
                return f"{seconds}秒"
                
        except:
            return "未知"
    
    def _calculate_resource_usage(self) -> Dict[str, Any]:
        """计算资源使用情况"""
        try:
            import psutil
            import os
            
            # 内存使用
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # 磁盘使用
            data_dir = self.data_path
            if data_dir.exists():
                disk_usage = sum(f.stat().st_size for f in data_dir.rglob('*')) / 1024 / 1024
            else:
                disk_usage = 0
            
            # API调用（从系统状态获取）
            api_calls = self.system_state['resources'].get('api_calls_today', 0)
            
            return {
                'memory_mb': round(memory_mb, 2),
                'disk_mb': round(disk_usage, 2),
                'api_calls_today': api_calls,
                'last_check': datetime.now().isoformat()
            }
            
        except ImportError:
            # psutil未安装
            return {
                'memory_mb': 0,
                'disk_mb': 0,
                'api_calls_today': 0,
                'last_check': datetime.now().isoformat(),
                'note': '安装psutil以获取详细资源信息'
            }
        except Exception as e:
            self.logger.error(f"计算资源使用失败: {e}")
            return {
                'memory_mb': 0,
                'disk_mb': 0,
                'api_calls_today': 0,
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def create_backup(self, backup_name: str = None) -> str:
        """创建备份"""
        with self.state_lock:
            try:
                if not backup_name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"backup_{timestamp}"
                
                backup_dir = self.data_path / "backups" / backup_name
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                # 备份数据库
                db_source = self.state_dir / "state.db"
                if db_source.exists():
                    import shutil
                    shutil.copy2(db_source, backup_dir / "state.db")
                
                # 备份状态文件
                state_files = ['interactions', 'performance', 'relationships']
                for file_name in state_files:
                    file_path = self.state_dir / f"{file_name}.json"
                    if file_path.exists():
                        shutil.copy2(file_path, backup_dir / f"{file_name}.json")
                
                # 更新系统状态
                self.system_state['system']['last_backup'] = datetime.now().isoformat()
                self.system_state['system']['backup_count'] += 1
                
                self.logger.info(f"备份创建成功: {backup_name}")
                
                return str(backup_dir)
                
            except Exception as e:
                self.logger.error(f"创建备份失败: {e}")
                raise
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """清理旧数据"""
        with self.state_lock:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
                
                # 删除旧交互记录
                self.cursor.execute(
                    'DELETE FROM interaction_logs WHERE timestamp < ?',
                    (cutoff_str,)
                )
                
                deleted_count = self.cursor.rowcount
                
                # 清理不活跃用户（30天无互动）
                self.cursor.execute('''
                    DELETE FROM user_stats 
                    WHERE last_interaction < ? 
                    AND interaction_count < 5
                ''', (cutoff_str,))
                
                deleted_users = self.cursor.rowcount
                
                self.conn.commit()
                
                self.logger.info(f"数据清理完成: 删除 {deleted_count} 条记录，{deleted_users} 个用户")
                
                return {
                    'deleted_records': deleted_count,
                    'deleted_users': deleted_users,
                    'cutoff_date': cutoff_str
                }
                
            except Exception as e:
                self.logger.error(f"清理数据失败: {e}")
                self.conn.rollback()
                raise
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态管理器状态"""
        with self.state_lock:
            return {
                'database': {
                    'path': str(self.state_dir / "state.db"),
                    'interaction_count': self._get_table_count('interaction_logs'),
                    'user_count': self._get_table_count('user_stats')
                },
                'files': {
                    'state_dir': str(self.state_dir),
                    'backup_count': self.system_state['system']['backup_count']
                },
                'auto_save': {
                    'enabled': True,
                    'interval_seconds': self.auto_save_interval,
                    'next_save': (self.last_auto_save + 
                                 timedelta(seconds=self.auto_save_interval)).isoformat()
                }
            }
    
    def _get_table_count(self, table_name: str) -> int:
        """获取表记录数"""
        try:
            self.cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            return self.cursor.fetchone()[0]
        except:
            return 0
    
    def close(self):
        """关闭资源"""
        with self.state_lock:
            try:
                # 保存所有状态
                self._auto_save_to_files()
                
                # 关闭数据库连接
                if hasattr(self, 'conn'):
                    self.conn.close()
                
                self.logger.info("状态管理器已关闭")
                
            except Exception as e:
                self.logger.error(f"关闭状态管理器失败: {e}")
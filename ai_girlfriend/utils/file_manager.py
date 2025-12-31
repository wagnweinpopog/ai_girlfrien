#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理工具
处理文件操作、目录管理和数据存储
"""

import os
import shutil
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class FileManager:
    """文件管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("FileManager")
        
    def initialize_data_structure(self, base_path: str = "./data"):
        """初始化数据目录结构"""
        data_path = Path(base_path)
        
        directories = [
            "memory/long_term",
            "memory/short_term", 
            "memory/episodic",
            "personality",
            "relationship",
            "logs",
            "backups",
            "state",
            "communication",
            "emotion",
            "life",
            "downloads",
            "cache"
        ]
        
        for directory in directories:
            dir_path = data_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"创建目录: {dir_path}")
        
        # 创建必要的空文件
        required_files = [
            "personality/personality_state.json",
            "relationship/relationship_status.json",
            "state/system_state.json"
        ]
        
        for file_path in required_files:
            full_path = data_path / file_path
            if not full_path.exists():
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False)
        
        self.logger.info(f"数据目录结构初始化完成: {data_path}")
        return str(data_path)
    
    def save_json(self, data: Dict, file_path: str, indent: int = 2) -> bool:
        """保存JSON数据"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            self.logger.debug(f"JSON数据保存成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存JSON数据失败 {file_path}: {e}")
            return False
    
    def load_json(self, file_path: str, default: Dict = None) -> Dict:
        """加载JSON数据"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.warning(f"JSON文件不存在: {file_path}")
                return default or {}
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"JSON数据加载成功: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"加载JSON数据失败 {file_path}: {e}")
            return default or {}
    
    def save_pickle(self, data: Any, file_path: str) -> bool:
        """保存Pickle数据"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.debug(f"Pickle数据保存成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存Pickle数据失败 {file_path}: {e}")
            return False
    
    def load_pickle(self, file_path: str, default: Any = None) -> Any:
        """加载Pickle数据"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.warning(f"Pickle文件不存在: {file_path}")
                return default
            
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            self.logger.debug(f"Pickle数据加载成功: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"加载Pickle数据失败 {file_path}: {e}")
            return default
    
    def create_backup(self, source_dir: str, backup_name: str = None) -> str:
        """创建备份"""
        try:
            source_path = Path(source_dir)
            
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            # 确定备份目录
            if source_path.name == "data":
                # 如果是data目录，备份到data/backups
                backup_dir = source_path.parent / "backups" / backup_name
            else:
                backup_dir = source_path.parent / "backups" / backup_name
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            for item in source_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(source_path)
                    target_path = backup_dir / rel_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)
            
            # 创建备份元数据
            metadata = {
                "source": str(source_path),
                "backup_time": datetime.now().isoformat(),
                "file_count": len(list(source_path.rglob("*"))),
                "backup_name": backup_name
            }
            
            metadata_file = backup_dir / "backup_metadata.json"
            self.save_json(metadata, str(metadata_file))
            
            self.logger.info(f"备份创建成功: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            raise
    
    def cleanup_old_files(self, directory: str, days_old: int = 30) -> int:
        """清理旧文件"""
        try:
            dir_path = Path(directory)
            cutoff_time = datetime.now().timestamp() - (days_old * 86400)
            
            deleted_count = 0
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            self.logger.warning(f"删除文件失败 {file_path}: {e}")
            
            self.logger.info(f"清理了 {deleted_count} 个旧文件")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理文件失败: {e}")
            return 0
    
    def get_directory_size(self, directory: str) -> int:
        """获取目录大小（字节）"""
        try:
            dir_path = Path(directory)
            total_size = 0
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
            
        except Exception as e:
            self.logger.error(f"获取目录大小失败: {e}")
            return 0
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """列出文件"""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return []
            
            files = []
            for file_path in dir_path.rglob(pattern):
                if file_path.is_file():
                    files.append(str(file_path))
            
            return sorted(files)
            
        except Exception as e:
            self.logger.error(f"列出文件失败: {e}")
            return []
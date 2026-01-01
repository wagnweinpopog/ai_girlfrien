#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 配置管理器
负责加载和管理所有配置文件
参考：https://github.com/django/django/blob/main/django/conf/__init__.py
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.configs = {}
        self.loaded = False
        
    def load_all_configs(self):
        """加载所有配置文件"""
        try:
            # 1. 加载环境变量
            self._load_environment()
            
            # 2. 加载角色配置文件
            self._load_yaml_configs()
            
            # 3. 验证配置
            self._validate_configs()
            
            self.loaded = True
            return self.configs
            
        except Exception as e:
            raise Exception(f"配置加载失败: {str(e)}")
    
    def _load_environment(self):
        """加载环境变量"""
        env_path = self.project_root / ".env"
        
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # 创建示例环境文件
            self._create_example_env()
            raise FileNotFoundError(f"请配置 {env_path} 文件")
        
        # 收集所有环境变量
        self.configs['env'] = {
            'telegram': {
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
                'admin_id': os.getenv('TELEGRAM_ADMIN_ID')
            },
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'base_url': os.getenv('DEEPSEEK_BASE_URL'),
                'model': os.getenv('DEEPSEEK_MODEL')
            },
            'zhipu': {
                'api_key': os.getenv('ZHIPU_API_KEY'),
                'base_url': os.getenv('ZHIPU_BASE_URL'),
                'model': os.getenv('ZHIPU_MODEL')
            },
            'system': {
                'name': os.getenv('SYSTEM_NAME', '星黎级AI女友'),
                'data_path': os.getenv('DATA_PATH', './data'),
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'language': os.getenv('LANGUAGE', 'zh-CN'),
                'timezone': os.getenv('TIMEZONE', 'Asia/Shanghai')
            }
        }
    
    def _load_yaml_configs(self):
        """加载YAML配置文件"""
        config_dir = self.project_root / "config"
        
        config_files = {
            'character': 'character_profile.yaml',
            'emotion': 'emotion_config.yaml',
            'memory': 'memory_rules.yaml',
            'system': 'system_config.yaml'
        }
        
        for key, filename in config_files.items():
            filepath = config_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.configs[key] = yaml.safe_load(f)
            else:
                self.logger.warning(f"配置文件缺失: {filename}")
                self.configs[key] = {}
    
    def _validate_configs(self):
        """验证配置完整性"""
        env = self.configs['env']
        
        # 检查必要配置
        required_configs = [
            ('TELEGRAM_BOT_TOKEN', env['telegram']['bot_token']),
            ('DEEPSEEK_API_KEY', env['deepseek']['api_key']),
            ('ZHIPU_API_KEY', env['zhipu']['api_key'])
        ]
        
        missing = []
        for name, value in required_configs:
            if not value or value.startswith('你的_'):
                missing.append(name)
        
        if missing:
            raise ValueError(f"缺少必要配置: {', '.join(missing)}")
    
    def _create_example_env(self):
        """创建示例环境文件"""
        example_content = """# 星黎级AI女友 - 环境配置示例
# 复制此文件为 .env 并填入真实值

TELEGRAM_BOT_TOKEN=你的_Telegram_Bot_Token
TELEGRAM_ADMIN_ID=你的_Telegram用户ID

DEEPSEEK_API_KEY=你的_DeepSeek_API密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

ZHIPU_API_KEY=你的_智谱AI_API密钥
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPU_MODEL=glm-4v
"""
        
        example_path = self.project_root / ".env.example"
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_content)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.configs
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def save_config(self, key: str, value: Any, filename: str = None):
        """保存配置到文件"""
        # 待实现
        pass
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 主启动文件
项目地址：https://github.com/yourusername/ai_girlfriend
启动命令：python launch.py
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.consciousness import ConsciousnessCore
from interfaces.telegram_client import TelegramClient
from utils.file_manager import FileManager
from config_manager import ConfigManager

class AIGirlfriendLauncher:
    """AI女友启动器"""
    
    def __init__(self):
        self.setup_logging()
        self.config = ConfigManager()
        self.file_manager = FileManager()
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = project_root / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"girlfriend_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("AIGirlfriend")
        self.logger.info("=" * 50)
        self.logger.info("星黎级AI女友系统启动中...")
        self.logger.info(f"项目根目录: {project_root}")
        self.logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    def initialize_system(self):
        """初始化系统组件"""
        try:
            self.logger.info("步骤1/4: 加载配置文件...")
            self.config.load_all_configs()
            
            self.logger.info("步骤2/4: 初始化文件系统...")
            self.file_manager.initialize_data_structure()
            
            self.logger.info("步骤3/4: 启动意识核心...")
            self.consciousness = ConsciousnessCore(self.config)
            
            self.logger.info("步骤4/4: 启动通信接口...")
            self.telegram_client = TelegramClient(
                self.config,
                self.consciousness
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}", exc_info=True)
            return False
    
    def run(self):
        """运行主循环"""
        if not self.initialize_system():
            self.logger.error("系统初始化失败，请检查配置和日志")
            return
        
        self.logger.info("🎉 系统初始化完成！")
        self.logger.info("🤖 AI女友已激活")
        self.logger.info("💕 开始等待用户互动...")
        self.logger.info("=" * 50)
        
        try:
            # 启动Telegram机器人
            self.telegram_client.run()
            
        except KeyboardInterrupt:
            self.logger.info("收到关闭信号，正在优雅退出...")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"运行时错误: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self):
        """关闭系统"""
        self.logger.info("保存所有状态...")
        if hasattr(self, 'consciousness'):
            self.consciousness.save_all_states()
        self.logger.info("系统已安全关闭")
        sys.exit(0)

if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 运行启动器
    launcher = AIGirlfriendLauncher()
    launcher.run()
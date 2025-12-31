#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 启动脚本
简化启动方式，便于使用
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from launch import AIGirlfriendLauncher

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 星黎级AI女友启动中...")
    print("=" * 50)
    
    try:
        launcher = AIGirlfriendLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 收到关闭信号，再见~")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
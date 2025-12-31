#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本，检查基本功能
"""

import sys
import os
from pathlib import Path

def test_basic():
    """基本测试"""
    print("🤖 星黎级AI女友 - 简单测试")
    print("=" * 50)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查必要模块
    required_modules = [
        'telegram', 'requests', 'yaml', 'aiohttp', 'dotenv'
    ]
    
    print("\n检查依赖模块:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - 未安装")
    
    # 检查配置文件
    print("\n检查配置文件:")
    if Path(".env").exists():
        print("✅ .env 文件存在")
    else:
        print("❌ .env 文件不存在")
        if Path(".env.example").exists():
            print("⚠️  请复制 .env.example 为 .env")
    
    # 检查核心目录
    print("\n检查目录结构:")
    required_dirs = ['core', 'config', 'data']
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - 目录不存在")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("如果所有检查都通过✅，可以运行: python start.py")

if __name__ == "__main__":
    test_basic()
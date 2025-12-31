#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接测试脚本
检查API连接是否正常
"""

import requests
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

def test_telegram_connection(token):
    """测试Telegram连接"""
    print("🔗 测试Telegram连接...")
    
    # Telegram Bot API测试
    test_url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"✅ Telegram连接成功！")
                print(f"   机器人: @{bot_info.get('username')}")
                print(f"   名称: {bot_info.get('first_name')}")
                return True
        else:
            print(f"❌ Telegram连接失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:100]}")
            
    except requests.exceptions.Timeout:
        print("❌ Telegram连接超时，请检查网络")
    except requests.exceptions.ConnectionError:
        print("❌ Telegram连接错误，可能网络不通")
    except Exception as e:
        print(f"❌ Telegram连接异常: {e}")
    
    return False

def test_deepseek_connection(api_key):
    """测试DeepSeek连接"""
    print("\n🧠 测试DeepSeek连接...")
    
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            print("✅ DeepSeek连接成功！")
            return True
        elif response.status_code == 401:
            print("❌ DeepSeek API密钥无效")
        elif response.status_code == 429:
            print("❌ DeepSeek API请求超限")
        else:
            print(f"❌ DeepSeek连接失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ DeepSeek连接超时")
    except Exception as e:
        print(f"❌ DeepSeek连接异常: {e}")
    
    return False

def test_zhipu_connection(api_key):
    """测试智谱AI连接"""
    print("\n👁️ 测试智谱AI连接...")
    
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "glm-4v",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            print("✅ 智谱AI连接成功！")
            return True
        elif response.status_code == 401:
            print("❌ 智谱AI API密钥无效")
        else:
            print(f"❌ 智谱AI连接失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ 智谱AI连接超时")
    except Exception as e:
        print(f"❌ 智谱AI连接异常: {e}")
    
    return False

def test_network():
    """测试网络连接"""
    print("🌐 测试基础网络连接...")
    
    test_sites = [
        ("Telegram API", "https://api.telegram.org"),
        ("DeepSeek API", "https://api.deepseek.com"),
        ("智谱AI API", "https://open.bigmodel.cn")
    ]
    
    all_ok = True
    for name, url in test_sites:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {name}: 可访问")
        except Exception as e:
            print(f"❌ {name}: 无法访问 - {str(e)[:50]}")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("=" * 50)
    print("🔧 AI女友 - 连接测试工具")
    print("=" * 50)
    
    # 加载环境变量
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print("❌ 未找到 .env 文件")
        return
    
    # 获取API密钥
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    zhipu_key = os.getenv("ZHIPU_API_KEY")
    
    print(f"📋 找到 {sum(1 for x in [telegram_token, deepseek_key, zhipu_key] if x and not x.startswith('你的_'))}/3 个API密钥")
    
    # 测试网络
    if not test_network():
        print("\n⚠️  网络连接有问题，请检查网络设置")
    
    # 测试API连接
    success_count = 0
    
    if telegram_token and not telegram_token.startswith('你的_'):
        if test_telegram_connection(telegram_token):
            success_count += 1
    else:
        print("\n⚠️  Telegram Bot Token未配置")
    
    if deepseek_key and not deepseek_key.startswith('你的_'):
        if test_deepseek_connection(deepseek_key):
            success_count += 1
    else:
        print("\n⚠️  DeepSeek API密钥未配置")
    
    if zhipu_key and not zhipu_key.startswith('你的_'):
        if test_zhipu_connection(zhipu_key):
            success_count += 1
    else:
        print("\n⚠️  智谱AI API密钥未配置")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/3 个服务连接成功")
    
    if success_count >= 2:
        print("✅ 连接测试通过，可以启动AI女友！")
        print("   运行: python start.py")
    else:
        print("❌ 连接测试失败，请检查API密钥和网络")

if __name__ == "__main__":
    main()
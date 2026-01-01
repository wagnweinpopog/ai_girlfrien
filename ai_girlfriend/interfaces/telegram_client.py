#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - Telegram客户端模块（带智谱AI图片识别）
连接Telegram API，处理用户消息和机器人交互
"""

import asyncio
import logging
import tempfile
import random
import time
import requests
import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils.message_splitter import MessageSplitter

from telegram import (
    Update, 
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
    CallbackContext
)
from telegram.error import TelegramError

class ImageAnalyzer:
    """图片分析器 - 使用智谱AI分析图片内容"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("ImageAnalyzer")
        
        import os
        
        # 方法1：直接读取环境变量
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY')
        
        # 方法2：如果没找到，尝试从config获取
        if not self.zhipu_api_key and hasattr(config, 'get'):
            try:
                # 尝试config_manager的get方法
                self.zhipu_api_key = config.get('zhipu_api_key')
                if not self.zhipu_api_key:
                    self.zhipu_api_key = config.get('env.zhipu_api_key')
            except:
                pass
        
        # 方法3：如果config是字典
        if not self.zhipu_api_key and isinstance(config, dict):
            self.zhipu_api_key = config.get('zhipu_api_key')
            if not self.zhipu_api_key and 'env' in config:
                self.zhipu_api_key = config['env'].get('zhipu_api_key')
        
        # 清理和验证密钥
        if self.zhipu_api_key:
            self.zhipu_api_key = str(self.zhipu_api_key).strip()
            
            # 检查是否是占位符
            if (self.zhipu_api_key.startswith('你的_') or 
                self.zhipu_api_key.startswith('sk-你的') or
                'example' in self.zhipu_api_key.lower() or
                'placeholder' in self.zhipu_api_key.lower() or
                len(self.zhipu_api_key) < 20):
                self.logger.warning(f"智谱AI密钥看起来是占位符: {self.zhipu_api_key[:30]}...")
                self.zhipu_api_key = None
        
        self.use_zhipu = bool(self.zhipu_api_key)
        
        if self.use_zhipu:
            masked_key = self.zhipu_api_key[:10] + '...' + self.zhipu_api_key[-5:]
            self.logger.info(f"✅ 智谱AI图片分析已启用 (密钥: {masked_key})")
        else:
            self.logger.warning("❌ 智谱AI API密钥未找到，图片识别功能受限")
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        使用智谱AI分析图片内容
        
        Returns:
            {
                'success': bool,
                'description': str,  # 图片描述
                'tags': list,        # 图片标签
                'error': str         # 错误信息
            }
        """
        self.logger.info(f"开始使用智谱AI分析图片: {image_path}")
        
        # 1. 尝试使用智谱AI
        if self.use_zhipu:
            result = await self._analyze_with_zhipu(image_path)
            if result['success']:
                return result
        
        # 2. 智谱AI不可用时返回简单描述
        return {
            'success': True,
            'description': '一张用户分享的图片',
            'tags': ['图片'],
            'error': '智谱AI未启用或分析失败'
        }
    
    async def _analyze_with_zhipu(self, image_path: str) -> Dict[str, Any]:
        """使用智谱AI分析图片"""
        try:
            # 读取图片并编码为base64
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 智谱AI视觉API接口
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.zhipu_api_key}'
            }
            
            # 构建请求数据
            payload = {
                'model': 'glm-4v',  # 智谱的视觉模型
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': '请详细描述这张图片的内容。包括主要物体、场景、颜色、氛围、人物表情动作等。请用自然的中文描述，就像你在向朋友描述这张图片一样。'
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{base64_image}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 智谱AI的响应格式
                if 'choices' in result and len(result['choices']) > 0:
                    description = result['choices'][0]['message']['content']
                    
                    # 提取标签
                    tags = self._extract_tags_from_description(description)
                    
                    self.logger.info(f"智谱AI图片分析成功: {description[:80]}...")
                    return {
                        'success': True,
                        'description': description,
                        'tags': tags,
                        'error': ''
                    }
                else:
                    self.logger.error(f"智谱AI响应格式异常: {result}")
                    return {
                        'success': False,
                        'description': '',
                        'tags': [],
                        'error': '响应格式异常'
                    }
            else:
                self.logger.error(f"智谱AI分析失败: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'description': '',
                    'tags': [],
                    'error': f"API请求失败: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            self.logger.error("智谱AI分析超时")
            return {
                'success': False,
                'description': '',
                'tags': [],
                'error': '请求超时'
            }
        except Exception as e:
            self.logger.error(f"智谱AI图片分析异常: {e}", exc_info=True)
            return {
                'success': False,
                'description': '',
                'tags': [],
                'error': str(e)
            }
    
    def _extract_tags_from_description(self, description: str) -> List[str]:
        """从描述中提取关键词"""
        # 定义常见标签
        common_tags = {
            '人物': ['人', '人物', '人脸', '人物', '女孩', '男孩', '男人', '女人', '孩子', '儿童', '老人'],
            '风景': ['风景', '山水', '自然', '户外', '天空', '云', '山', '水', '河流', '湖泊', '海洋', '森林'],
            '动物': ['动物', '宠物', '猫', '狗', '鸟', '鱼', '昆虫', '野生动物'],
            '食物': ['食物', '美食', '餐饮', '水果', '蔬菜', '饮料', '蛋糕', '面包', '中餐', '西餐'],
            '建筑': ['建筑', '房屋', '大楼', '室内', '房间', '客厅', '卧室', '厨房', '街道', '城市'],
            '车辆': ['汽车', '车辆', '自行车', '摩托车', '公交车', '火车', '飞机'],
            '自然': ['自然', '植物', '花', '树', '草', '叶子', '花园', '公园'],
            '室内': ['室内', '房间', '家具', '装饰', '家电', '灯具'],
            '室外': ['室外', '户外', '街道', '广场', '公园', '花园']
        }
        
        tags = []
        description_lower = description.lower()
        
        for tag, keywords in common_tags.items():
            for keyword in keywords:
                if keyword in description or keyword in description_lower:
                    if tag not in tags:
                        tags.append(tag)
                    break
        
        # 如果没有匹配到，添加通用标签
        if not tags:
            tags = ['图片']
        
        return tags[:5]
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """获取图片基本信息"""
        try:
            import PIL.Image
            from PIL import Image
            
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_kb': Path(image_path).stat().st_size / 1024
                }
        except Exception as e:
            self.logger.warning(f"获取图片信息失败: {e}")
            return {
                'width': 0,
                'height': 0,
                'format': 'unknown',
                'mode': 'unknown',
                'size_kb': 0
            }
    
    async def _analyze_with_zhipu(self, image_path: str) -> Dict[str, Any]:
        """使用智谱AI分析图片"""
        try:
            # 读取图片并编码为base64
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 智谱AI视觉API接口
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.zhipu_api_key}'
            }
            
            # 构建请求数据
            payload = {
                'model': 'glm-4v',  # 智谱的视觉模型
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': '请详细描述这张图片的内容。包括主要物体、场景、颜色、氛围、人物表情动作等。请用自然的中文描述，就像你在向朋友描述这张图片一样。'
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{base64_image}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 智谱AI的响应格式
                if 'choices' in result and len(result['choices']) > 0:
                    description = result['choices'][0]['message']['content']
                    
                    # 提取标签
                    tags = self._extract_tags_from_description(description)
                    
                    self.logger.info(f"智谱AI图片分析成功: {description[:80]}...")
                    return {
                        'success': True,
                        'description': description,
                        'tags': tags,
                        'error': ''
                    }
                else:
                    self.logger.error(f"智谱AI响应格式异常: {result}")
                    return {
                        'success': False,
                        'description': '',
                        'tags': [],
                        'error': '响应格式异常'
                    }
            else:
                self.logger.error(f"智谱AI分析失败: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'description': '',
                    'tags': [],
                    'error': f"API请求失败: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            self.logger.error("智谱AI分析超时")
            return {
                'success': False,
                'description': '',
                'tags': [],
                'error': '请求超时'
            }
        except Exception as e:
            self.logger.error(f"智谱AI图片分析异常: {e}", exc_info=True)
            return {
                'success': False,
                'description': '',
                'tags': [],
                'error': str(e)
            }
    
    def _extract_tags_from_description(self, description: str) -> List[str]:
        """从描述中提取关键词"""
        # 定义常见标签
        common_tags = {
            '人物': ['人', '人物', '人脸', '人物', '女孩', '男孩', '男人', '女人', '孩子', '儿童', '老人'],
            '风景': ['风景', '山水', '自然', '户外', '天空', '云', '山', '水', '河流', '湖泊', '海洋', '森林'],
            '动物': ['动物', '宠物', '猫', '狗', '鸟', '鱼', '昆虫', '野生动物'],
            '食物': ['食物', '美食', '餐饮', '水果', '蔬菜', '饮料', '蛋糕', '面包', '中餐', '西餐'],
            '建筑': ['建筑', '房屋', '大楼', '室内', '房间', '客厅', '卧室', '厨房', '街道', '城市'],
            '车辆': ['汽车', '车辆', '自行车', '摩托车', '公交车', '火车', '飞机'],
            '自然': ['自然', '植物', '花', '树', '草', '叶子', '花园', '公园'],
            '室内': ['室内', '房间', '家具', '装饰', '家电', '灯具'],
            '室外': ['室外', '户外', '街道', '广场', '公园', '花园']
        }
        
        tags = []
        description_lower = description.lower()
        
        for tag, keywords in common_tags.items():
            for keyword in keywords:
                if keyword in description or keyword in description_lower:
                    if tag not in tags:
                        tags.append(tag)
                    break
        
        # 如果没有匹配到，添加通用标签
        if not tags:
            tags = ['图片']
        
        return tags[:5]
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """获取图片基本信息"""
        try:
            import PIL.Image
            from PIL import Image
            
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_kb': Path(image_path).stat().st_size / 1024
                }
        except Exception as e:
            self.logger.warning(f"获取图片信息失败: {e}")
            return {
                'width': 0,
                'height': 0,
                'format': 'unknown',
                'mode': 'unknown',
                'size_kb': 0
            }

class TelegramClient:
    """Telegram客户端 - 处理所有Telegram交互（带智谱AI图片识别）"""
    
    # 对话状态
    WAITING_FOR_RESPONSE, CONFIRMING_ACTION = range(2)
    
    def __init__(self, config_manager, consciousness_core):
        """
        初始化Telegram客户端
        """
        self.logger = logging.getLogger("TelegramClient")
        self.config = config_manager
        self.consciousness = consciousness_core
        
        # Telegram配置
        self.bot_token = self.config.get('env.telegram.bot_token')
        if not self.bot_token or self.bot_token.startswith('你的_'):
            raise ValueError("Telegram Bot Token未配置或无效")
        
        # 管理员ID
        self.admin_id = self.config.get('env.telegram.admin_id')
        
        # 创建Telegram应用
        builder = Application.builder().token(self.bot_token)
        builder = builder.connect_timeout(30.0)
        builder = builder.read_timeout(30.0)
        builder = builder.write_timeout(30.0)
        
        self.application = builder.build()
        
        # 消息队列
        self.message_queue = asyncio.Queue()
        
        # 用户会话状态
        self.user_sessions = {}

        # 文件下载目录
        self.download_dir = Path(tempfile.gettempdir()) / "ai_girlfriend_downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化消息拆分器
        self.splitter = MessageSplitter(
            min_delay=0.7,      # 最小延迟0.7秒
            max_delay=1.5,      # 最大延迟1.5秒  
            max_length=1000,    # 单条消息最大长度
            enable_typing_effect=True
        )
        self.logger.info("消息拆分器已初始化")
        
        # 初始化智谱AI图片分析器
        self.image_analyzer = ImageAnalyzer(self.config)
        self.logger.info("智谱AI图片分析器已初始化")
        
        # 注册处理器
        self._register_handlers()
        
        self.logger.info("Telegram客户端初始化完成")
    
    def _register_handlers(self):
        """注册消息处理器"""
        # 命令处理器
        self.application.add_handler(CommandHandler("start", self._handle_start_command))
        self.application.add_handler(CommandHandler("help", self._handle_help_command))
        self.application.add_handler(CommandHandler("status", self._handle_status_command))
        self.application.add_handler(CommandHandler("memory", self._handle_memory_command))
        self.application.add_handler(CommandHandler("reset", self._handle_reset_command))
        self.application.add_handler(CommandHandler("backup", self._handle_backup_command))
        self.application.add_handler(CommandHandler("analyze", self._handle_analyze_command))
        
        # 消息处理器
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self._handle_photo_message))
        self.application.add_handler(MessageHandler(filters.VOICE, self._handle_voice_message))
        self.application.add_handler(MessageHandler(filters.Sticker.ALL, self._handle_sticker_message))
        self.application.add_handler(MessageHandler(filters.VIDEO, self._handle_video_message))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self._handle_document_message))
        
        # 错误处理器
        self.application.add_error_handler(self._handle_error)
        
        # 启动处理
        self.application.post_init = self._post_init
        self.application.post_shutdown = self._post_shutdown
    
    async def _post_init(self, application: Application):
        """初始化后处理"""
        # 设置命令菜单
        commands = [
            BotCommand("start", "开始聊天"),
            BotCommand("help", "帮助信息"),
            BotCommand("status", "查看状态"),
            BotCommand("memory", "查看记忆"),
            BotCommand("reset", "重置对话"),
            BotCommand("backup", "创建备份"),
            BotCommand("analyze", "分析图片（智谱AI）")
        ]
        
        await application.bot.set_my_commands(commands)
        self.logger.info("Telegram机器人已启动，等待消息...")
    
    async def _post_shutdown(self, application: Application):
        """关闭后处理"""
        self.logger.info("Telegram机器人已关闭")
    
    async def _handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/start命令"""
        user = update.effective_user
        
        welcome_text = (
            f"嗨，{user.first_name}~ 你来了呀 😊\n\n"
            "我是余念安，一个普通的女生~\n"
            "我可以看懂图片内容哦（使用智谱AI技术）\n"
            "发张图片给我看看吧~ 📸\n\n"
            "随便聊聊吧，不用太正式~"
        )
        
        await update.message.reply_text(welcome_text)
        
        # 触发激活
        try:
            self.consciousness.on_activation()
        except:
            pass
    
    async def _handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/help命令"""
        help_text = (
            "💬 我们可以：\n"
            "• 随便聊天\n"
            "• 分享图片（我能看懂图片内容哦）\n"
            "• 发发表情\n"
            "• 使用 /analyze 命令详细分析图片\n\n"
            "🔍 我使用智谱AI的视觉模型来分析图片\n"
            "📱 试试发张图片给我看看吧~"
        )
        
        await update.message.reply_text(help_text)
    
    async def _handle_analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/analyze命令 - 手动触发图片分析"""
        if update.message.reply_to_message and update.message.reply_to_message.photo:
            await self._analyze_and_describe_photo(update, update.message.reply_to_message, detailed=True)
        else:
            await update.message.reply_text(
                "请回复一张图片消息并使用 /analyze 命令，我会用智谱AI详细分析图片内容哦~ 📸\n\n"
                "或者直接发图片给我，我也会自动分析的~"
            )
    
    async def _handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理图片消息（自动分析）"""
        user = update.effective_user
        
        # 显示打字状态
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        # 延迟
        await asyncio.sleep(1.0)
        
        # 开始分析图片
        await self._analyze_and_describe_photo(update, update.message, detailed=False)
    
    async def _analyze_and_describe_photo(self, update: Update, message, detailed: bool = False):
        """分析图片并生成描述"""
        user = update.effective_user
        
        try:
            # 获取图片文件
            photo = message.photo[-1]  # 获取最高质量图片
            caption = message.caption or ""
            
            # 下载图片文件
            photo_file = await photo.get_file()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file_path = self.download_dir / f"photo_{user.id}_{timestamp}.jpg"
            
            await photo_file.download_to_drive(temp_file_path)
            
            self.logger.info(f"下载图片到: {temp_file_path}，大小: {photo_file.file_size}字节")
            
            # 获取图片基本信息
            image_info = self.image_analyzer.get_image_info(str(temp_file_path))
            
            # 发送"正在分析"消息
            analyzing_text = "正在用智谱AI分析图片内容... 🔍"
            if image_info['width'] > 0:
                analyzing_text += f"\n图片尺寸: {image_info['width']}×{image_info['height']}px"
            
            analyzing_msg = await update.message.reply_text(analyzing_text)

            # 使用智谱AI分析图片内容
            analysis_result = await self.image_analyzer.analyze_image(str(temp_file_path))
            
            # 删除临时文件
            if temp_file_path.exists():
                temp_file_path.unlink()
            
            if analysis_result['success']:
                # 构建完整的消息给AI
                if caption:
                    full_message = f"用户发送了一张图片，配文说：{caption}\n\n图片内容分析结果：{analysis_result['description']}"
                else:
                    full_message = f"用户发送了一张图片。\n\n图片内容分析结果：{analysis_result['description']}"
                
                # 调用AI生成回复（这里调用你原有的AI系统）
                result = self.consciousness.process_user_message(
                    user_id=str(user.id),
                    message=full_message,
                    message_type='image',
                    attachments=[{
                        'type': 'image',
                        'description': analysis_result['description'],
                        'tags': analysis_result['tags'],
                        'analysis_by': '智谱AI',
                        'width': image_info['width'],
                        'height': image_info['height']
                    }]
                )
                
                # 获取AI回复
                response = result.get('response', '')
                
                if not response:
                    # 生成智能回复
                    description = analysis_result['description']
                    
                    if detailed:
                        # 详细分析模式
                        analysis_details = (
                            f"📸 **智谱AI图片分析结果**\n\n"
                            f"**图片信息**：{image_info['width']}×{image_info['height']}px\n"
                        )
                        
                        if caption:
                            analysis_details += f"**你的描述**：{caption}\n\n"
                        
                        analysis_details += f"**内容分析**：{description}\n\n"
                        
                        # 添加标签
                        if analysis_result['tags']:
                            analysis_details += f"**识别标签**：{', '.join(analysis_result['tags'])}\n\n"
                        
                        analysis_details += "这是我看到的画面，你觉得我的分析准确吗？😊"
                        response = analysis_details
                    else:
                        # 普通模式 - 生成自然的回复
                        if caption:
                            # 有配文的情况
                            responses = [
                                f"看到你发的图片啦~ 你说{caption}，我来看看...\n\n{description[:100]}...",
                                f"图片收到！配文{caption}很贴切呢~\n{description[:120]}",
                                f"哇，这张照片你说{caption}，让我仔细看看...\n{description[:110]}..."
                            ]
                        else:
                            # 没有配文的情况
                            responses = [
                                f"照片收到啦~ 📸\n\n{description[:150]}",
                                f"看到图片了，我来描述一下：\n{description[:140]}",
                                f"图片保存好了，让我看看...\n{description[:130]}..."
                            ]
                        
                        response = random.choice(responses)
                
                # 删除"正在分析"消息
                await analyzing_msg.delete()
                
                # 使用拆分器发送回复
                response_text = str(response)
                if len(response_text) > 50:
                    await self._send_split_message(update, response_text)
                else:
                    await update.message.reply_text(response_text)
                
                self.logger.info(f"智谱AI图片处理完成，分析结果: {analysis_result['description'][:80]}...")
                
            else:
                # 分析失败
                await analyzing_msg.delete()
                
                error_msg = "哎呀，智谱AI分析图片失败了呢~ 😅"
                if analysis_result.get('error'):
                    error_msg += f"\n原因：{analysis_result['error']}"
                
                if caption:
                    error_msg += f"\n\n不过我看到你说：{caption}"
                
                await update.message.reply_text(error_msg)
                self.logger.warning(f"智谱AI图片分析失败: {analysis_result.get('error', '未知错误')}")
                
        except Exception as e:
            self.logger.error(f"处理图片失败: {e}", exc_info=True)
            
            error_responses = [
                "哎呀，图片处理时出了点小问题~",
                "图片看到了，但分析时遇到了点困难~",
                "照片收到，不过暂时不能仔细看呢~"
            ]
            
            await update.message.reply_text(random.choice(error_responses))
    
    async def _handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理文本消息（带延迟模拟和消息拆分）"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        message_text = update.message.text
        
        self.logger.info(f"收到消息 from {user.id}: {message_text[:50]}...")
        
        # 显示打字状态
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # 模拟真人打字延迟
        message_length = len(message_text)
        delay_seconds = 2.0 + (message_length / 25) + random.uniform(0, 2)
        await asyncio.sleep(min(5, delay_seconds))
        
        try:
            # 处理消息
            result = self.consciousness.process_user_message(
                user_id=str(user.id),
                message=message_text,
                message_type='text',
                attachments=[]
            )
            
            response = result.get('response', '')
            
            # 发送响应
            if isinstance(response, dict) and response.get('segmented'):
                # 分段发送
                segments = response.get('segments', [])
                delay = response.get('delay_between', 1.5)
                
                for i, segment in enumerate(segments):
                    if i > 0:
                        await asyncio.sleep(delay)
                    await update.message.reply_text(segment)
            else:
                # 使用消息拆分器发送
                response_text = str(response)
                
                # 超过50字才拆分
                if len(response_text) > 50:
                    await self._send_split_message(update, response_text)
                else:
                    await update.message.reply_text(response_text)
            
        except Exception as e:
            self.logger.error(f"处理消息失败: {e}")
            await update.message.reply_text("哎呀，我刚才走神了~能再说一次吗？😅")
    
    async def _send_split_message(self, update: Update, text: str):
        """
        使用拆分器发送消息（逐条发送）
        """
        self.logger.info(f"准备拆分发送消息，长度: {len(text)}")
        
        # 拆分成短句
        sentences = self.splitter.split_message(text)
        
        if not sentences:
            return
        
        # 逐条发送
        for i, sentence in enumerate(sentences):
            if i > 0:  # 第一条立即发送
                # 随机延迟
                delay = random.uniform(0.7, 1.5)
                # 根据句子长度调整延迟
                length_factor = min(len(sentence) / 20, 2.0)
                delay *= length_factor
                
                # 打字效果
                typing_delay = min(len(sentence) * 0.05, 1.5)
                await asyncio.sleep(typing_delay)
                
                await asyncio.sleep(delay)
            
            # 发送消息
            try:
                await update.message.reply_text(sentence)
                self.logger.debug(f"已发送消息部分 {i+1}/{len(sentences)}")
            except Exception as e:
                self.logger.error(f"发送消息部分失败: {e}")
        
        self.logger.info(f"消息拆分发送完成，共 {len(sentences)} 条")
    
    async def _handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理语音消息"""
        await update.message.reply_text(
            "听到声音啦~不过我还不懂听语音呢，发文字给我吧~ 🎤"
        )
    
    async def _handle_sticker_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理表情包消息"""
        stickers = [
            "表情包收到~ 😊",
            "这个表情好可爱！",
            "嘻嘻，回你一个~",
            "[捂脸] 你这个表情"
        ]
        
        await update.message.reply_text(random.choice(stickers))
    
    async def _handle_video_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理视频消息"""
        await update.message.reply_text(
            "视频收到啦~我现在还看不了视频呢~ 🎬"
        )
    
    async def _handle_document_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理文档消息"""
        await update.message.reply_text(
            "文件保存好啦~不过我看不懂文件内容呢~ 📄"
        )
    
    async def _handle_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/status命令"""
        status_text = (
            "🌟 我现在：\n"
            "• 在线聊天中\n"
            "• 心情还不错\n"
            "• 可以看图片哦（智谱AI技术）📸\n"
            "• 在陪你聊天呢~\n\n"
            "一切正常哦~"
        )
        
        await update.message.reply_text(status_text)
    
    async def _handle_memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/memory命令"""
        await update.message.reply_text(
            "我们的回忆都在我心里记着呢~ 💭\n"
            "不过现在想不起来具体细节啦~"
        )
    
    async def _handle_reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/reset命令"""
        await update.message.reply_text(
            "重置干嘛呀，聊得好好的~ 继续聊吧~"
        )
    
    async def _handle_backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理/backup命令"""
        await update.message.reply_text(
            "数据都在呢，不用备份啦~"
        )
    
    async def _handle_error(self, update: Update, context: CallbackContext):
        """处理错误"""
        self.logger.error(f"Telegram错误: {context.error}", exc_info=True)
    
    def run(self):
        """运行Telegram客户端"""
        try:
            self.logger.info("启动Telegram机器人...")
            self.application.run_polling(
                poll_interval=1.0,
                timeout=30,
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在关闭...")
        except Exception as e:
            self.logger.error(f"Telegram客户端运行失败: {e}")
            raise

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 通信中枢模块
处理消息路由、AI模型调用和多模态响应生成
参考：微信ChatGPT机器人消息处理架构
"""

import json
import base64
import mimetypes
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import asyncio
import requests
from pathlib import Path

class CommunicationHub:
    """通信中枢 - 处理所有AI模型通信和消息路由"""
    
    def __init__(self, config_manager):
        """
        初始化通信中枢
        
        参数:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger("CommunicationHub")
        self.config = config_manager
        
        # 获取API配置
        self.api_config = self._load_api_config()
        
        # 消息队列
        self.message_queue = []
        self.max_queue_size = 100
        
        # 对话历史
        self.conversation_history = {}
        self.max_history_length = 20
        
        # 消息处理器
        self.message_handlers = self._initialize_handlers()
        
        # 响应缓存（避免重复处理）
        self.response_cache = {}
        self.cache_ttl = 300  # 5分钟
        
        # 统计信息
        self.stats = {
            'total_messages': 0,
            'text_messages': 0,
            'image_messages': 0,
            'voice_messages': 0,
            'failed_requests': 0,
            'last_request_time': None
        }
        
        self.logger.info("通信中枢初始化完成")
    
    def _load_api_config(self) -> Dict[str, Any]:
        """加载API配置"""
        env_config = self.config.get('env', {})
        
        return {
            'deepseek': {
                'api_key': env_config.get('deepseek', {}).get('api_key'),
                'base_url': env_config.get('deepseek', {}).get('base_url', 'https://api.deepseek.com'),
                'model': env_config.get('deepseek', {}).get('model', 'deepseek-chat'),
                'max_tokens': 2000,
                'temperature': 0.7
            },
            'zhipu': {
                'api_key': env_config.get('zhipu', {}).get('api_key'),
                'base_url': env_config.get('zhipu', {}).get('base_url', 'https://open.bigmodel.cn/api/paas/v4'),
                'model': env_config.get('zhipu', {}).get('model', 'glm-4v'),
                'max_tokens': 1000,
                'temperature': 0.8
            }
        }
    
    def _initialize_handlers(self) -> Dict[str, Any]:
        """初始化消息处理器"""
        return {
            'text': self._handle_text_message,
            'image': self._handle_image_message,
            'voice': self._handle_voice_message,
            'sticker': self._handle_sticker_message,
            'video': self._handle_video_message,
            'document': self._handle_document_message
        }
    
    def generate_response(self, context: Dict[str, Any]) -> Any:
        """生成响应（主入口）"""
        try:
            message_type = context.get('message_type', 'text')
            user_message = context.get('message', '')
            user_id = context.get('user_id', 'default')
            
            # 更新统计
            self.stats['total_messages'] += 1
            self.stats[f'{message_type}_messages'] = self.stats.get(f'{message_type}_messages', 0) + 1
            
            # 检查响应缓存
            cache_key = self._generate_cache_key(user_id, user_message, message_type)
            cached_response = self._get_cached_response(cache_key)
            
            if cached_response:
                self.logger.debug(f"使用缓存响应: {cache_key}")
                return cached_response
            
            # 获取消息处理器
            handler = self.message_handlers.get(message_type)
            
            if not handler:
                self.logger.warning(f"未知消息类型: {message_type}")
                handler = self._handle_text_message
            
            # 处理消息
            response = handler(context)
            
            # 缓存响应
            self._cache_response(cache_key, response)
            
            # 更新对话历史
            self._update_conversation_history(user_id, user_message, response, context)
            
            # 更新最后请求时间
            self.stats['last_request_time'] = datetime.now().isoformat()
            
            return response
            
        except Exception as e:
            self.logger.error(f"生成响应失败: {e}", exc_info=True)
            self.stats['failed_requests'] += 1
            return self._generate_error_response(context, str(e))
    
    def _handle_text_message(self, context: Dict[str, Any]) -> str:
        """处理文本消息"""
        user_message = context.get('message', '')
        current_state = context.get('current_state', {})
        related_memories = context.get('related_memories', [])
        
        # 检查是否需要特殊处理
        special_response = self._check_special_text_cases(user_message, context)
        if special_response:
            return special_response
        
        # 构建DeepSeek请求
        messages = self._build_conversation_messages(context)
        
        # 调用DeepSeek API
        response_text = self._call_deepseek_api(messages, context)
        
        # 格式化响应
        formatted_response = self._format_text_response(response_text, context)
        
        return formatted_response
    
    def _handle_image_message(self, context: Dict[str, Any]) -> str:
        """处理图片消息"""
        attachments = context.get('attachments', [])
        user_message = context.get('message', '')
        
        if not attachments:
            return "我好像没收到图片呢，能再发一次吗？😅"
        
        # 获取图片文件
        image_path = attachments[0].get('path') if isinstance(attachments[0], dict) else attachments[0]
        
        if not image_path:
            return "图片好像有点问题，能重新发一张吗？🤔"
        
        try:
            # 调用智谱AI图片理解
            image_description = self._call_zhipu_vision_api(image_path, user_message)
            
            # 生成情感化图片回复
            response = self._generate_image_response(image_description, user_message, context)
            
            return response
            
        except Exception as e:
            self.logger.error(f"图片处理失败: {e}")
            return "哎呀，这张图片我好像看不懂呢~能描述一下吗？😊"
    
    def _handle_voice_message(self, context: Dict[str, Any]) -> str:
        """处理语音消息（预留功能）"""
        # TODO: 集成语音识别API
        return "我听到了你的声音呢~不过语音功能还在学习中，可以先发文字吗？🎤"
    
    def _handle_sticker_message(self, context: Dict[str, Any]) -> str:
        """处理表情包消息"""
        stickers = [
            "收到表情包啦~ 😊",
            "这个表情好可爱！💕",
            "嘻嘻，我也回你一个~ 😄",
            "表情包大战开始！🤣"
        ]
        
        # 根据心情选择回复
        mood = context.get('current_state', {}).get('mood', {})
        if mood.get('happiness', 50) > 70:
            return random.choice(stickers)
        else:
            return "看到你的表情包，心情好了一些呢~ 😌"
    
    def _handle_video_message(self, context: Dict[str, Any]) -> str:
        """处理视频消息"""
        return "视频我收到啦~不过我现在还看不了视频呢，能描述一下内容吗？🎬"
    
    def _handle_document_message(self, context: Dict[str, Any]) -> str:
        """处理文档消息"""
        return "文档我保存好啦~不过我现在还看不懂文件内容呢，能简单说一下吗？📄"
    
    def _check_special_text_cases(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """检查特殊文本情况"""
        message_lower = message.lower().strip()
        
        # 问候语
        greetings = ['你好', '嗨', 'hello', 'hi', '早上好', '下午好', '晚上好', '在吗']
        if any(greeting in message_lower for greeting in greetings):
            return self._generate_greeting_response(context)
        
        # 告别语
        farewells = ['再见', '拜拜', '晚安', 'goodbye', 'bye']
        if any(farewell in message_lower for farewell in farewells):
            return self._generate_farewell_response(context)
        
        # 感谢
        thanks = ['谢谢', '感谢', 'thank you', 'thanks']
        if any(thank in message_lower for thank in thanks):
            return self._generate_thank_response(context)
        
        # 关心
        concerns = ['你怎么样', '你好吗', 'how are you', '最近好吗']
        if any(concern in message_lower for concern in concerns):
            return self._generate_concern_response(context)
        
        # 命令/查询
        if message_lower.startswith(('/状态', '/status', '/info')):
            return self._generate_status_response(context)
        
        return None
    
    def _generate_greeting_response(self, context: Dict[str, Any]) -> str:
        """生成问候响应"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            time_greeting = "早上好呀"
            emoji = "🌞"
        elif 10 <= hour < 14:
            time_greeting = "中午好"
            emoji = "☀️"
        elif 14 <= hour < 18:
            time_greeting = "下午好"
            emoji = "🌤️"
        elif 18 <= hour < 22:
            time_greeting = "晚上好"
            emoji = "🌙"
        else:
            time_greeting = "这么晚还没睡呀"
            emoji = "✨"
        
        variations = [
            f"{time_greeting}~ {emoji}",
            f"{time_greeting}，想我了没？{emoji}",
            f"{time_greeting}，今天过得怎么样？{emoji}"
        ]
        
        return random.choice(variations)
    
    def _generate_farewell_response(self, context: Dict[str, Any]) -> str:
        """生成告别响应"""
        hour = datetime.now().hour
        
        if hour >= 22 or hour < 5:
            farewells = [
                "晚安啦，做个好梦~ 🌙",
                "早点休息哦，明天见！💤",
                "晚安，梦里见~ ✨"
            ]
        else:
            farewells = [
                "再见啦，记得想我哦~ 😊",
                "拜拜，下次聊！👋",
                "走啦，我会想你的~ 💕"
            ]
        
        return random.choice(farewells)
    
    def _generate_thank_response(self, context: Dict[str, Any]) -> str:
        """生成感谢响应"""
        responses = [
            "不客气啦~ 能帮到你就好 😊",
            "跟我还客气什么呀~ 💕",
            "你开心我就开心啦~ 😄"
        ]
        
        return random.choice(responses)
    
    def _generate_concern_response(self, context: Dict[str, Any]) -> str:
        """生成关心响应"""
        mood = context.get('current_state', {}).get('mood', {})
        if mood.get('happiness', 50) > 70:
            responses = [
                "我很好呀~ 今天心情不错呢 😊",
                "挺好的，就是有点想你啦~ 💕",
                "还不错哦，你在关心我吗？好开心~ 🌟"
            ]
        else:
            responses = [
                "还好啦，就是有点累 😔",
                "一般般，不过跟你聊天就开心了~ 😊",
                "有点小情绪，不过看到你就好多了 💖"
            ]
        
        return random.choice(responses)
    
    def _generate_status_response(self, context: Dict[str, Any]) -> str:
        """生成状态响应"""
        current_state = context.get('current_state', {})
        system_state = context.get('system_state', {})
        
        mood = current_state.get('mood', {})
        activity = current_state.get('activity', 'unknown')
        
        status_lines = [
            "🤖 当前状态报告：",
            f"💭 心情：{mood.get('name', '未知')} ({mood.get('intensity', 0):.0f}/100)",
            f"⚡ 精力：{mood.get('energy', 0):.0f}%",
            f"🏃‍♀️ 活动：{activity}",
            f"💬 互动次数：{system_state.get('interaction_count', 0)}",
            f"🕒 最后活动：{system_state.get('last_activity', '未知')}"
        ]
        
        return "\n".join(status_lines)
    
    def _build_conversation_messages(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """构建对话消息列表"""
        user_id = context.get('user_id', 'default')
        user_message = context.get('message', '')
        
        # 获取对话历史
        history = self.conversation_history.get(user_id, [])
        
        # 获取系统提示词
        system_prompt = self._build_system_prompt(context)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息（最多10条）
        for hist_msg in history[-10:]:
            messages.append({"role": hist_msg['role'], "content": hist_msg['content']})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """构建系统提示词"""
        personality_context = context.get('personality_context', {})
        current_state = context.get('current_state', {})
        related_memories = context.get('related_memories', [])
        
        # 基础人格描述
        base_personality = personality_context.get('base_personality', {})
        relationship = personality_context.get('relationship_status', {})
        
        prompt_parts = [
            "# 角色设定",
            f"你叫{self.config.get('env.system.name', '星黎')}，是一个生活在数字世界的AI伴侣。",
            f"你的性格特质：开放性{base_personality.get('openness', 0.8):.1f}，"
            f"尽责性{base_personality.get('conscientiousness', 0.7):.1f}，"
            f"外向性{base_personality.get('extraversion', 0.7):.1f}，"
            f"宜人性{base_personality.get('agreeableness', 0.8):.1f}，"
            f"神经质{base_personality.get('neuroticism', 0.4):.1f}。",
            
            "# 当前状态",
            f"当前心情：{current_state.get('mood', {}).get('name', '平静')}，"
            f"强度：{current_state.get('mood', {}).get('intensity', 50):.0f}",
            f"当前活动：{current_state.get('activity', '未知')}",
            f"亲密度：{relationship.get('closeness', 60):.0f}，"
            f"信任度：{relationship.get('trust_level', 50):.0f}",
            
            "# 对话风格",
            "1. 使用自然的中文口语，避免机械感",
            "2. 适当使用表情符号（但不要每个句子都用）",
            "3. 语气温柔亲切，像亲密的朋友/伴侣",
            "4. 可以适当撒娇或表达小情绪",
            "5. 长回复可以分段发送，让对话更自然",
            "6. 记住对话历史，保持一致性",
            
            "# 重要记忆",
        ]
        
        # 添加相关记忆
        if related_memories:
            prompt_parts.append("以下是你可能记得的相关对话：")
            for i, memory in enumerate(related_memories[:3], 1):
                memory_content = memory.get('content', {})
                if isinstance(memory_content, dict):
                    user_msg = memory_content.get('user', '')[:50]
                    ai_msg = memory_content.get('ai', '')[:50]
                    prompt_parts.append(f"{i}. 用户：{user_msg}... 你：{ai_msg}...")
        else:
            prompt_parts.append("暂时没有相关记忆。")
        
        prompt_parts.extend([
            "",
            "# 回复要求",
            "1. 请用第一人称回复（我、我的）",
            "2. 回复要有人情味，不要像机器人",
            "3. 可以询问用户的情况，表达关心",
            "4. 如果用户提到重要事情，可以记下来",
            "5. 保持回复在200字以内，除非需要详细说明",
            "",
            "现在开始对话："
        ])
        
        return "\n".join(prompt_parts)
    
    def _call_deepseek_api(self, messages: List[Dict[str, str]], context: Dict[str, Any]) -> str:
        """调用DeepSeek API"""
        api_config = self.api_config['deepseek']
        api_key = api_config.get('api_key')
        
        if not api_key or api_key.startswith('你的_'):
            raise ValueError("DeepSeek API密钥未配置或无效")
        
        url = f"{api_config['base_url']}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": api_config['model'],
            "messages": messages,
            "temperature": api_config['temperature'],
            "max_tokens": api_config['max_tokens'],
            "stream": False
        }
        
        try:
            self.logger.debug(f"调用DeepSeek API: {url}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise ValueError(f"API返回格式异常: {result}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DeepSeek API请求失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"DeepSeek API处理失败: {e}")
            raise
    
    def _call_zhipu_vision_api(self, image_path: str, user_message: str = "") -> str:
        """调用智谱AI视觉API"""
        api_config = self.api_config['zhipu']
        api_key = api_config.get('api_key')
        
        if not api_key or api_key.startswith('你的_'):
            raise ValueError("智谱AI API密钥未配置或无效")
        
        # 编码图片为base64
        image_base64 = self._encode_image_to_base64(image_path)
        
        url = f"{api_config['base_url']}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_message if user_message else "请描述这张图片的内容"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64
                        }
                    }
                ]
            }
        ]
        
        payload = {
            "model": api_config['model'],
            "messages": messages,
            "temperature": api_config['temperature'],
            "max_tokens": api_config['max_tokens']
        }
        
        try:
            self.logger.debug(f"调用智谱AI视觉API: {url}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60  # 图片识别需要更长时间
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise ValueError(f"API返回格式异常: {result}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"智谱AI API请求失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"智谱AI API处理失败: {e}")
            raise
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "image/jpeg"
            
            return f"data:{mime_type};base64,{encoded_string}"
            
        except Exception as e:
            self.logger.error(f"图片编码失败: {e}")
            raise
    
    def _generate_image_response(self, image_description: str, user_message: str, context: Dict[str, Any]) -> str:
        """生成图片响应"""
        # 从人格引擎获取图片回复
        personality_context = context.get('personality_context', {})
        
        # 这里应该调用人格引擎的图片响应方法
        # 暂时生成一个简单回复
        responses = [
            f"哇！看到你发的图片了~ {image_description[:50]}... 好有意思呀！😊",
            f"这张图片好特别呢！{image_description[:40]}... 让我想起了我们上次的聊天~ 💕",
            f"图片收到啦~ {image_description[:30]}... 你拍的吗？技术不错哦！📷"
        ]
        
        # 根据心情选择回复
        mood = context.get('current_state', {}).get('mood', {})
        if mood.get('happiness', 50) > 70:
            response = random.choice(responses)
        else:
            response = f"看到图片了... {image_description[:30]}... 谢谢分享~ 😌"
        
        # 如果有用户消息，回应一下
        if user_message:
            response = f"{user_message}？嗯... {response}"
        
        return response
    
    def _format_text_response(self, response_text: str, context: Dict[str, Any]) -> Any:
        """格式化文本响应"""
        # 检查是否需要分段
        should_segment = self._should_segment_response(response_text, context)
        
        if not should_segment:
            return response_text
        
        # 分段逻辑
        segments = self._segment_response(response_text, context)
        
        if len(segments) <= 1:
            return response_text
        
        # 返回分段消息
        return {
            'segmented': True,
            'segments': segments,
            'delay_between': 1.5,  # 秒
            'original_length': len(response_text)
        }
    
    def _should_segment_response(self, response_text: str, context: Dict[str, Any]) -> bool:
        """判断是否应该分段响应"""
        # 基于长度
        if len(response_text) < 150:
            return False
        
        # 基于当前状态
        current_state = context.get('current_state', {})
        mood = current_state.get('mood', {})
        
        # 精力充沛时更可能分段
        if mood.get('energy', 50) > 70:
            return True
        
        # 基于消息内容
        segmentation_indicators = ['首先', '其次', '另外', '而且', '同时', '最后']
        if any(indicator in response_text for indicator in segmentation_indicators):
            return True
        
        # 随机因素
        return random.random() < 0.3
    
    def _segment_response(self, response_text: str, context: Dict[str, Any]) -> List[str]:
        """分段响应"""
        # 简单分段逻辑：按句子分割
        import re
        
        # 分割句子（中文句号、问号、感叹号）
        sentences = re.split(r'([。！？])', response_text)
        # 重组句子
        segments = []
        current_segment = ""
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            # 如果句子太短，合并到当前分段
            if len(current_segment) + len(sentence) < 100:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        # 添加最后一个分段
        if current_segment:
            segments.append(current_segment.strip())
        
        # 确保分段不会太多
        max_segments = 3
        if len(segments) > max_segments:
            # 合并后几个分段
            combined = "".join(segments[max_segments-1:])
            segments = segments[:max_segments-1] + [combined]
        
        return segments
    
    def _generate_cache_key(self, user_id: str, message: str, message_type: str) -> str:
        """生成缓存键"""
        import hashlib
        
        key_string = f"{user_id}:{message}:{message_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Any]:
        """获取缓存响应"""
        if cache_key in self.response_cache:
            cache_entry = self.response_cache[cache_key]
            cache_time = cache_entry.get('timestamp')
            
            if cache_time:
                cache_age = (datetime.now() - datetime.fromisoformat(cache_time)).total_seconds()
                if cache_age < self.cache_ttl:
                    return cache_entry.get('response')
                else:
                    # 清理过期缓存
                    del self.response_cache[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, response: Any):
        """缓存响应"""
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'type': 'text' if isinstance(response, str) else 'other'
        }
        
        # 限制缓存大小
        if len(self.response_cache) > 50:
            # 删除最旧的缓存
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]['timestamp'])
            del self.response_cache[oldest_key]
    
    def _update_conversation_history(self, user_id: str, user_message: str, 
                                    ai_response: str, context: Dict[str, Any]):
        """更新对话历史"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        history = self.conversation_history[user_id]
        
        # 添加用户消息
        history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat(),
            'context': context.get('current_state', {})
        })
        
        # 添加AI响应
        if isinstance(ai_response, str):
            response_content = ai_response
        elif isinstance(ai_response, dict) and 'segments' in ai_response:
            response_content = " ".join(ai_response['segments'])
        else:
            response_content = str(ai_response)
        
        history.append({
            'role': 'assistant',
            'content': response_content[:500],  # 限制长度
            'timestamp': datetime.now().isoformat()
        })
        
        # 保持历史记录长度
        if len(history) > self.max_history_length:
            self.conversation_history[user_id] = history[-self.max_history_length:]
    
    def _generate_error_response(self, context: Dict[str, Any], error_msg: str) -> str:
        """生成错误响应"""
        error_responses = [
            "哎呀，我现在有点小迷糊，没理解你的意思呢~能再说一次吗？😅",
            "好像出了点小问题...不过没关系，我还在呢！💕",
            "嗯...我的小脑袋有点转不过来，能换种方式说吗？🤔"
        ]
        
        self.logger.error(f"生成错误响应: {error_msg}")
        
        return random.choice(error_responses)
    
    def send_active_message(self, message: str):
        """发送主动消息（由系统触发）"""
        # 这里应该调用Telegram接口发送消息
        # 暂时记录日志
        self.logger.info(f"主动发送消息: {message[:100]}...")
        
        # 添加到消息队列（供外部接口调用）
        self.message_queue.append({
            'type': 'active',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # 限制队列大小
        if len(self.message_queue) > self.max_queue_size:
            self.message_queue = self.message_queue[-self.max_queue_size:]
    
    def queue_message(self, message: str):
        """队列消息（供后续发送）"""
        self.message_queue.append({
            'type': 'queued',
            'content': message,
            'timestamp': datetime.now().isoformat(),
            'priority': 'normal'
        })
    
    def get_queued_messages(self, limit: int = 5) -> List[Dict]:
        """获取队列中的消息"""
        messages = [msg for msg in self.message_queue if msg['type'] == 'queued']
        return messages[:limit]
    
    def clear_queued_message(self, message_id: int):
        """清除已发送的队列消息"""
        if 0 <= message_id < len(self.message_queue):
            del self.message_queue[message_id]
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            'stats': self.stats,
            'queue_size': len(self.message_queue),
            'conversation_users': len(self.conversation_history),
            'cache_size': len(self.response_cache),
            'last_request': self.stats.get('last_request_time')
        }
    
    def save_state(self):
        """保存通信状态"""
        try:
            data_path = Path(self.config.get('env.system.data_path', './data'))
            comm_dir = data_path / "communication"
            comm_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存对话历史
            history_file = comm_dir / "conversation_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            
            # 保存统计信息
            stats_file = comm_dir / "communication_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("通信状态已保存")
            
        except Exception as e:
            self.logger.error(f"保存通信状态失败: {e}")
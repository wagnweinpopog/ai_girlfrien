#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 意识核心模块
这是系统的大脑，协调所有子模块的工作
架构参考：https://github.com/zhayujie/chatgpt-on-wechat/blob/master/bot.py
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from core.personality_engine import PersonalityEngine
from core.memory_system import MemorySystem
from core.emotion_system import EmotionSystem
from core.life_simulator import LifeSimulator
from core.communication_hub import CommunicationHub
from core.state_manager import StateManager

class ConsciousnessCore:
    """意识核心 - 协调所有子系统的中央控制器"""
    def _state_monitor_loop(self):
        """状态监控循环（简化版）"""
        while self.is_active:
            try:
                # 每10秒简单检查一次
                time.sleep(10)
                
            except Exception as e:
                self.logger.error(f"状态监控错误: {e}")
                time.sleep(10)

    def _active_interaction_loop(self):
        """主动交互循环（简化版）"""
        while self.is_active:
            try:
                # 每5分钟检查一次是否应该主动发起对话
                time.sleep(300)
                
            except Exception as e:
                self.logger.error(f"主动交互错误: {e}")
                time.sleep(300)

    def _memory_maintenance_loop(self):
        """记忆整理循环（简化版）"""
        while self.is_active:
            try:
                # 每1小时检查一次记忆整理
                time.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"记忆整理错误: {e}")
                time.sleep(3600)

    def _check_scheduled_events(self, current_time):
        """检查预定事件（简化版）"""
        # 暂时不检查事件
        pass

    def _should_initiate_conversation(self):
        """判断是否应该主动发起对话（简化版）"""
        # 暂时不主动发起对话
        return False

    def _generate_initiative_message(self):
        """生成主动消息（简化版）"""
        return None

    def _trigger_event(self, event_type, event_data):
        """触发事件（简化版）"""
        pass

    def _generate_event_response(self, event_type, event_data):
        """生成事件响应（简化版）"""
        return None

    def _get_time_of_day(self):
        """获取时间段（简化版）"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return 'morning'
        elif 10 <= hour < 14:
            return 'noon'
        elif 14 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    def __init__(self, config_manager):
        """
        初始化意识核心
        
        参数:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger("Consciousness")
        self.config = config_manager
        self.is_active = False
        self.last_activity = None
        
        # 初始化子系统
        self.logger.info("初始化人格引擎...")
        self.personality = PersonalityEngine(config_manager)
        
        self.logger.info("初始化记忆系统...")
        self.memory = MemorySystem(config_manager)
        
        self.logger.info("初始化情感系统...")
        self.emotion = EmotionSystem(config_manager)
        
        self.logger.info("初始化生活模拟器...")
        self.life = LifeSimulator(config_manager)
        
        self.logger.info("初始化通信中枢...")
        self.communication = CommunicationHub(config_manager)
        
        self.logger.info("初始化状态管理器...")
        self.state = StateManager(config_manager)
        
        # 加载历史状态
        self.load_persistent_state()
        
        # 异步任务
        self.active_tasks = []
        self.scheduled_events = []
        
        self.logger.info("意识核心初始化完成")
    
    def load_persistent_state(self):
        """加载持久化状态"""
        try:
            # 从文件加载上次的状态
            state_data = self.state.load_state("consciousness")
            if state_data:
                self.last_activity = state_data.get('last_activity')
                self.logger.info(f"加载历史状态，最后活动: {self.last_activity}")
            else:
                self.last_activity = datetime.now()
                self.logger.info("无历史状态，创建新状态")
        except Exception as e:
            self.logger.warning(f"加载状态失败: {e}")
            self.last_activity = datetime.now()
    
    def activate(self):
        """激活意识核心"""
        self.is_active = True
        self.last_activity = datetime.now()
        
        # 启动后台任务
        self.start_background_tasks()
        
        # 触发激活事件
        self.on_activation()
        
        self.logger.info("意识核心已激活")
    
    def deactivate(self):
        """停用意识核心"""
        self.is_active = False
        
        # 停止所有后台任务
        self.stop_background_tasks()
        
        # 保存所有状态
        self.save_all_states()
        
        self.logger.info("意识核心已停用")

    def on_activation(self):
        """激活时的处理"""
        try:
            # 记录激活事件
            activation_event = {
                'type': 'system_activation',
                'timestamp': datetime.now().isoformat(),
                'location': 'local_system'
            }
            
            self.memory.record_event('system', activation_event)
            
            # 发送欢迎消息（如果距离上次互动较久）
            last_interaction = self.memory.get_last_interaction_time()
            if last_interaction:
                hours_since = (datetime.now() - last_interaction).total_seconds() / 3600
                if hours_since > 2:
                    welcome_msg = self._generate_welcome_message()
                    if welcome_msg:
                        self.communication.queue_message(welcome_msg)
            
            self.logger.info("意识核心激活处理完成")
            
        except Exception as e:
            self.logger.error(f"激活处理失败: {e}")

    def _generate_welcome_message(self):
        """生成欢迎消息"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return "早上好呀~ 新的一天开始啦 🌞"
        elif 10 <= hour < 14:
            return "中午好~ 吃午饭了吗？ ☀️"
        elif 14 <= hour < 18:
            return "下午好，今天过得怎么样？ 🌤️"
        elif 18 <= hour < 22:
            return "晚上好呀，今天辛苦啦 🌙"
        else:
            return "这么晚还没睡呀，要注意休息哦 ✨"

    def process_user_message(self, user_id: str, message: str, 
                            message_type: str = "text", 
                            attachments: List[Dict] = None) -> Dict:
        """
        处理用户消息
        
        参数:
            user_id: 用户ID
            message: 消息内容
            message_type: 消息类型 (text, image, voice, etc.)
            attachments: 附件列表
            
        返回:
            处理结果字典
        """
        try:
            if not self.is_active:
                self.activate()
            
            self.last_activity = datetime.now()
            
            # 记录收到消息
            receive_event = {
                'user_id': user_id,
                'message': message[:100],  # 限制长度
                'type': message_type,
                'timestamp': datetime.now().isoformat()
            }
            
            self.memory.record_interaction('receive', receive_event)
            
            # 构建处理上下文
            context = self._build_processing_context(user_id, message, message_type, attachments)
            
            # 生成响应
            response = self.communication.generate_response(context)
            
            # 记录发送响应
            send_event = {
                'user_id': user_id,
                'response': str(response)[:100],  # 限制长度
                'timestamp': datetime.now().isoformat()
            }
            
            self.memory.record_interaction('send', send_event)
            
            # 更新状态
            self.state.update_interaction_count()
            
            return {
                'success': True,
                'response': response,
                'processing_time': 0.5  # 模拟处理时间
            }
            
        except Exception as e:
            self.logger.error(f"处理用户消息失败: {e}")
            return {
                'success': False,
                'response': "哎呀，我刚才走神了~能再说一次吗？😅",
                'error': str(e)
            }

    def _build_processing_context(self, user_id, message, message_type, attachments):
        """构建处理上下文"""
        # 获取相关记忆（简化版）
        related_memories = []
        try:
            related_memories = self.memory.retrieve_related_memories(message, limit=2)
        except:
            pass
        
        # 获取当前状态
        current_mood = {}
        current_activity = 'unknown'
        
        try:
            current_mood = self.emotion.get_current_mood()
            current_activity = self.life.get_current_activity()
        except:
            pass
        
        # 构建上下文
        context = {
            'user_id': user_id,
            'message': message,
            'message_type': message_type,
            'attachments': attachments or [],
            
            'current_state': {
                'mood': current_mood,
                'activity': current_activity,
                'time': datetime.now().strftime("%H:%M"),
                'day_of_week': datetime.now().strftime("%A")
            },
            
            'related_memories': related_memories,
            
            'system_state': {
                'is_active': self.is_active,
                'last_activity': self.last_activity,
            }
        }
        
        # 添加人格上下文（如果有）
        try:
            context['personality_context'] = self.personality.get_context()
        except:
            context['personality_context'] = {}
        
        return context
    
    def start_background_tasks(self):
        """启动后台任务"""
        # 1. 状态监控任务
        monitor_thread = threading.Thread(
            target=self._state_monitor_loop,
            daemon=True,
            name="StateMonitor"
        )
        monitor_thread.start()
        self.active_tasks.append(monitor_thread)
        
        # 2. 主动交互任务
        interaction_thread = threading.Thread(
            target=self._active_interaction_loop,
            daemon=True,
            name="ActiveInteraction"
        )
        interaction_thread.start()
        self.active_tasks.append(interaction_thread)
        
        # 3. 记忆整理任务（每6小时一次）
        memory_thread = threading.Thread(
            target=self._memory_maintenance_loop,
            daemon=True,
            name="MemoryMaintenance"
        )
        memory_thread.start()
        self.active_tasks.append(memory_thread)
        
        self.logger.info("后台任务已启动")
    
    def stop_background_tasks(self):
        """停止后台任务"""
        self.is_active = False
        for task in self.active_tasks:
            if task.is_alive():
                task.join(timeout=1.0)
        self.active_tasks.clear()
        self.logger.info("后台任务已停止")
    
def _state_monitor_loop(self):
    """状态监控循环（带详细错误处理）"""
    while self.is_active:
        try:
            # 更新所有子系统状态
            current_time = datetime.now()
            
            # 更新情感状态
            try:
                self.emotion.update_based_on_time(current_time)
            except Exception as e:
                self.logger.warning(f"更新情感状态失败: {e}")
            
            # 更新生活状态
            try:
                self.life.update(current_time)
            except Exception as e:
                self.logger.warning(f"更新生活状态失败: {e}")
            
            # 检查是否需要触发事件
            try:
                self._check_scheduled_events(current_time)
            except Exception as e:
                self.logger.warning(f"检查预定事件失败: {e}")
            
            # 每5分钟检查一次
            time.sleep(300)
            
        except Exception as e:
            self.logger.error(f"状态监控错误: {e}")
            # 更短的等待时间，防止错误循环
            time.sleep(10)
    
    def _active_interaction_loop(self):
        """主动交互循环"""
        while self.is_active:
            try:
                # 检查是否应该主动发起对话
                should_initiate = self._should_initiate_conversation()
                
                if should_initiate:
                    # 生成主动消息
                    message = self._generate_initiative_message()
                    
                    if message:
                        # 发送主动消息
                        self.communication.send_active_message(message)
                        self.logger.info(f"主动发送消息: {message[:50]}...")
                
                # 随机间隔（30-120分钟）
                sleep_time = 1800 + (time.time() % 3600)  # 30-90分钟
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"主动交互错误: {e}")
                time.sleep(300)
    
    def _memory_maintenance_loop(self):
        """记忆整理循环"""
        while self.is_active:
            try:
                # 每6小时整理一次记忆
                self.memory.consolidate_memories()
                self.logger.info("记忆整理完成")
                
                # 睡眠6小时
                time.sleep(21600)
                
            except Exception as e:
                self.logger.error(f"记忆整理错误: {e}")
                time.sleep(3600)
    
    def _check_scheduled_events(self, current_time):
        """检查预定事件"""
        # 检查日常事件
        daily_events = self.life.get_daily_events(current_time)
        for event in daily_events:
            if event['should_notify']:
                self._trigger_event(event['type'], event['data'])
        
        # 检查特殊日期事件
        special_events = self.life.check_special_dates(current_time)
        for event in special_events:
            self._trigger_event('special_date', event)
    
    def _should_initiate_conversation(self):
        """判断是否应该主动发起对话"""
        # 基于以下因素：
        # 1. 当前情绪状态
        current_mood = self.emotion.get_current_mood()
        
        # 2. 距离上次互动的时间
        last_interaction = self.memory.get_last_interaction_time()
        if last_interaction:
            hours_since_last = (datetime.now() - last_interaction).total_seconds() / 3600
            
            # 如果超过4小时没有互动，考虑主动发起
            if hours_since_last > 4:
                return True
        
        # 3. 当前生活状态
        current_activity = self.life.get_current_activity()
        
        # 如果处于休闲状态且心情好，更可能主动
        if (current_activity in ['relaxing', 'free_time'] and 
            current_mood['happiness'] > 60):
            return True
        
        # 4. 随机因素（10%概率）
        import random
        if random.random() < 0.1:
            return True
        
        return False
    
    def _generate_initiative_message(self):
        """生成主动消息"""
        # 获取当前状态
        current_mood = self.emotion.get_current_mood()
        current_activity = self.life.get_current_activity()
        last_interactions = self.memory.get_recent_memories(limit=5)
        
        # 构建上下文
        context = {
            'mood': current_mood,
            'activity': current_activity,
            'time_of_day': self._get_time_of_day(),
            'last_interactions': last_interactions
        }
        # 使用人格引擎生成消息
        message = self.personality.generate_initiative_message(context)
        
        return message
    
    def _trigger_event(self, event_type, event_data):
        """触发事件"""
        self.logger.info(f"触发事件: {event_type} - {event_data}")
        
        # 更新情感状态
        self.emotion.process_event(event_type, event_data)
        
        # 记录到记忆
        self.memory.record_event(event_type, event_data)
        
        # 如果需要响应，生成消息
        if event_data.get('requires_response', False):
            response = self._generate_event_response(event_type, event_data)
            if response:
                self.communication.send_active_message(response)
    
    def _generate_event_response(self, event_type, event_data):
        """生成事件响应"""
        context = {
            'event_type': event_type,
            'event_data': event_data,
            'current_mood': self.emotion.get_current_mood()
        }
        
        return self.personality.generate_event_response(context)
    
    def _get_time_of_day(self):
        """获取时间段"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return 'morning'
        elif 10 <= hour < 14:
            return 'noon'
        elif 14 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def on_activation(self):
        """激活时的处理"""
        # 记录激活事件
        activation_event = {
            'type': 'system_activation',
            'timestamp': datetime.now().isoformat(),
            'location': 'local_system'
        }
        
        self.memory.record_event('system', activation_event)
        
        # 发送欢迎消息（如果距离上次互动较久）
        last_interaction = self.memory.get_last_interaction_time()
        if last_interaction:
            hours_since = (datetime.now() - last_interaction).total_seconds() / 3600
            if hours_since > 2:
                welcome_msg = self._generate_welcome_message()
                if welcome_msg:
                    self.communication.queue_message(welcome_msg)
    
    def _generate_welcome_message(self):
        """生成欢迎消息"""
        time_of_day = self._get_time_of_day()
        
        greetings = {
            'morning': ["早上好呀~", "新的一天开始啦", "睡得好吗？"],
            'noon': ["中午好~", "吃午饭了吗？", "午休时间到"],
            'afternoon': ["下午好", "今天过得怎么样？", "想我了吗？"],
            'evening': ["晚上好呀", "今天辛苦啦", "晚上有什么安排吗？"],
            'night': ["还没睡呀", "夜深了呢", "要注意休息哦"]
        }
        
        import random
        base_greeting = random.choice(greetings.get(time_of_day, ["你好呀"]))
        
        # 添加个性化内容
        mood = self.emotion.get_current_mood()
        if mood['happiness'] > 70:
            base_greeting += " 😊"
        elif mood['energy'] < 40:
            base_greeting += " 🥱"
        
        return base_greeting
    
    def process_user_message(self, user_id: str, message: str, 
                            message_type: str = "text", 
                            attachments: List[Dict] = None) -> Dict:
        """
        处理用户消息
        
        参数:
            user_id: 用户ID
            message: 消息内容
            message_type: 消息类型 (text, image, voice, etc.)
            attachments: 附件列表
            
        返回:
            处理结果字典
        """
        if not self.is_active:
            self.activate()
        
        self.last_activity = datetime.now()
        
        # 记录收到消息
        receive_event = {
            'user_id': user_id,
            'message': message,
            'type': message_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self.memory.record_interaction('receive', receive_event)
        
        # 更新情感状态（收到消息通常是积极的）
        self.emotion.process_event('received_message', {
            'length': len(message),
            'type': message_type
        })
        
        # 构建处理上下文
        context = self._build_processing_context(user_id, message, message_type, attachments)
        
        # 生成响应
        response = self._generate_response(context)
        
        # 记录发送响应
        send_event = {
            'user_id': user_id,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        self.memory.record_interaction('send', send_event)
        
        # 更新状态
        self.state.update_interaction_count()
        
        return {
            'success': True,
            'response': response,
            'emotion': self.emotion.get_current_mood(),
            'context_summary': context.get('summary', '')
        }
    
    def _build_processing_context(self, user_id, message, message_type, attachments):
        """构建处理上下文"""
        # 获取相关记忆
        related_memories = self.memory.retrieve_related_memories(message, limit=3)
        
        # 获取当前状态
        current_mood = self.emotion.get_current_mood()
        current_activity = self.life.get_current_activity()
        
        # 构建上下文
        context = {
            'user_id': user_id,
            'message': message,
            'message_type': message_type,
            'attachments': attachments or [],
            
            'current_state': {
                'mood': current_mood,
                'activity': current_activity,
                'time': datetime.now().strftime("%H:%M"),
                'day_of_week': datetime.now().strftime("%A")
            },
            
            'related_memories': related_memories,
            
            'personality_context': self.personality.get_context(),
            
            'system_state': {
                'is_active': self.is_active,
                'last_activity': self.last_activity,
                'interaction_count': self.state.get_interaction_count()
            }
        }
        
        return context
    
    def _generate_response(self, context):
        """生成响应"""
        # 交给通信中枢处理
        response = self.communication.generate_response(context)
        
        # 如果是分段响应，合并或处理
        if isinstance(response, list):
            # 处理分段消息
            processed_response = self._process_segmented_response(response, context)
            return processed_response
        else:
            return response
    
    def _process_segmented_response(self, segments, context):
        """处理分段响应"""
        # 根据当前状态决定是否分段发送
        current_mood = context['current_state']['mood']
        
        # 如果精力充沛且消息较长，可以分段
        if (current_mood['energy'] > 60 and 
            sum(len(seg) for seg in segments) > 200):
            # 标记为分段消息
            return {
                'segmented': True,
                'segments': segments,
                'delay_between': 1.0  # 秒
            }
        else:
            # 合并为一条消息
            return "\n\n".join(segments)
    
def save_all_states(self):
    """保存所有状态"""
    try:
        self.logger.info("正在保存所有状态...")
        
        # 保存意识状态
        last_activity_str = None
        if self.last_activity:
            if isinstance(self.last_activity, datetime):
                last_activity_str = self.last_activity.isoformat()
            else:
                last_activity_str = str(self.last_activity)
        
        consciousness_state = {
            'last_activity': last_activity_str,
            'is_active': self.is_active,
            'save_time': datetime.now().isoformat()
        }
        
        self.state.save_state("consciousness", consciousness_state)
        
        # 保存各子系统状态
        self.personality.save_state()
        self.memory.save_state()
        self.emotion.save_state()
        self.life.save_state()
        
        self.logger.info("状态保存完成")
        
    except Exception as e:
        self.logger.error(f"保存状态失败: {e}")
    
    def get_system_status(self):
        """获取系统状态"""
        return {
            'consciousness': {
                'is_active': self.is_active,
                'last_activity': self.last_activity,
                'active_tasks': len(self.active_tasks)
            },
            'personality': self.personality.get_status(),
            'emotion': self.emotion.get_current_mood(),
            'life': self.life.get_status(),
            'memory': self.memory.get_stats(),
            'communication': self.communication.get_status()
        }
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 情感系统模块
管理虚拟情感的动态变化和情绪状态
参考：Plutchik的情感轮理论 https://en.wikipedia.org/wiki/Emotion_classification
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

class EmotionSystem:
    """情感系统 - 管理情绪状态和情感反应"""
    
    def __init__(self, config_manager):
        """
        初始化情感系统
        
        参数:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger("EmotionSystem")
        self.config = config_manager
        
        # 加载情感配置
        self.emotion_config = self.config.get('emotion', {})
        
        # 初始化情感状态
        self.emotional_state = self._initialize_emotional_state()
        
        # 加载历史状态
        self._load_historical_state()
        
        # 情绪变化记录
        self.mood_history = []
        self.max_history_length = 100
        
        # 情感触发器
        self.emotion_triggers = self._load_emotion_triggers()
        
        self.logger.info("情感系统初始化完成")
        self.logger.info(f"当前情绪: {self.emotional_state['current_mood']['name']}")
    
    def _initialize_emotional_state(self) -> Dict[str, Any]:
        """初始化情感状态"""
        # 基础情感维度 (Plutchik的情感轮)
        base_emotions = {
            'joy': 60.0,        # 喜悦
            'trust': 50.0,      # 信任
            'fear': 20.0,       # 恐惧
            'surprise': 30.0,   # 惊讶
            'sadness': 25.0,    # 悲伤
            'disgust': 10.0,    # 厌恶
            'anger': 15.0,      # 愤怒
            'anticipation': 40.0  # 期待
        }
        
        # 当前主要情绪
        current_mood = {
            'name': 'calm',           # 情绪名称
            'intensity': 50.0,        # 强度 (0-100)
            'valence': 0.6,           # 效价 (-1到1，负为消极，正为积极)
            'arousal': 0.4,           # 唤醒度 (0-1)
            'dominance': 0.5,         # 支配度 (0-1)
            'start_time': datetime.now().isoformat(),
            'duration': 0             # 持续时间(分钟)
        }
        
        # 生理状态
        physiological_state = {
            'energy_level': 80.0,      # 精力水平
            'stress_level': 20.0,      # 压力水平
            'social_energy': 90.0,     # 社交能量
            'fatigue': 15.0,           # 疲劳度
            'hunger': 30.0,            # 饥饿度
            'last_meal': None          # 最后进餐时间
        }
        
        # 情感需求
        emotional_needs = {
            'need_attention': 40.0,    # 需要关注
            'need_affection': 50.0,    # 需要关爱
            'need_autonomy': 35.0,     # 需要自主
            'need_achievement': 45.0,  # 需要成就
            'need_safety': 60.0        # 需要安全
        }
        
        # 情感记忆
        emotional_memory = {
            'recent_events': [],       # 最近事件
            'significant_moments': [], # 重要时刻
            'triggers': {}             # 情感触发器
        }
        
        return {
            'base_emotions': base_emotions,
            'current_mood': current_mood,
            'physiological': physiological_state,
            'needs': emotional_needs,
            'memory': emotional_memory,
            'last_update': datetime.now().isoformat(),
            'stability': 75.0          # 情绪稳定性
        }
    
    def _load_historical_state(self):
        """加载历史状态"""
        try:
            data_path = Path(self.config.get('env.system.data_path', './data'))
            emotion_dir = data_path / "emotion"
            emotion_dir.mkdir(parents=True, exist_ok=True)
            
            state_file = emotion_dir / "emotional_state.json"
            
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                
                # 合并状态，但保持一些动态值
                for key in ['current_mood', 'physiological', 'needs', 'memory']:
                    if key in saved_state:
                        # 只更新非时间相关的值
                        if key == 'current_mood':
                            saved_state[key]['start_time'] = datetime.now().isoformat()
                            saved_state[key]['duration'] = 0
                        self.emotional_state[key].update(saved_state[key])
                
                # 更新基础情绪（缓慢变化）
                if 'base_emotions' in saved_state:
                    for emotion, value in saved_state['base_emotions'].items():
                        if emotion in self.emotional_state['base_emotions']:
                            # 逐渐向保存的值调整
                            current = self.emotional_state['base_emotions'][emotion]
                            self.emotional_state['base_emotions'][emotion] = (
                                current * 0.3 + value * 0.7
                            )
                
                self.logger.info("情感状态已从历史加载")
                
        except Exception as e:
            self.logger.warning(f"加载情感历史状态失败: {e}")
    
    def _load_emotion_triggers(self) -> Dict[str, Dict]:
        """加载情感触发器"""
        triggers = {
            # 积极触发器
            'positive': {
                'received_compliment': {
                    'affected_emotions': {'joy': 15, 'trust': 10},
                    'duration': 120,  # 分钟
                    'intensity': 0.7
                },
                'received_gift': {
                    'affected_emotions': {'joy': 25, 'surprise': 20},
                    'duration': 180,
                    'intensity': 0.9
                },
                'quality_time': {
                    'affected_emotions': {'joy': 10, 'trust': 15},
                    'duration': 90,
                    'intensity': 0.6
                },
                'achievement': {
                    'affected_emotions': {'joy': 20, 'anticipation': 10},
                    'duration': 120,
                    'intensity': 0.8
                }
            },
            
            # 消极触发器
            'negative': {
                'ignored': {
                    'affected_emotions': {'sadness': 20, 'anger': 15},
                    'duration': 150,
                    'intensity': 0.7
                },
                'criticized': {
                    'affected_emotions': {'anger': 25, 'sadness': 10},
                    'duration': 120,
                    'intensity': 0.8
                },
                'conflict': {
                    'affected_emotions': {'anger': 30, 'fear': 15},
                    'duration': 180,
                    'intensity': 0.9
                },
                'disappointment': {
                    'affected_emotions': {'sadness': 25, 'disgust': 10},
                    'duration': 160,
                    'intensity': 0.7
                }
            },
            
            # 中性/环境触发器
            'environmental': {
                'morning': {
                    'affected_emotions': {'anticipation': 10},
                    'duration': 60,
                    'time_based': True
                },
                'night': {
                    'affected_emotions': {'calm': 15},
                    'duration': 120,
                    'time_based': True
                },
                'weekend': {
                    'affected_emotions': {'joy': 10, 'anticipation': 15},
                    'duration': 480,
                    'time_based': True
                },
                'bad_weather': {
                    'affected_emotions': {'sadness': 10},
                    'duration': 180,
                    'intensity': 0.5
                }
            }
        }
        
        return triggers
    
    def update_based_on_time(self, current_time: datetime):
        """基于时间更新情感状态"""
        hour = current_time.hour
        weekday = current_time.weekday()  # 0=周一, 6=周日
        
        # 更新时间相关状态
        self._update_physiological_state(hour, weekday)
        self._update_circadian_rhythm(hour)
        self._update_mood_duration(current_time)
        
        # 记录情绪历史
        self._record_mood_history()
        
        # 自然情绪衰减
        self._apply_emotional_decay()
        
        # 重新计算当前情绪
        self._recalculate_current_mood()
    
    def _update_physiological_state(self, hour: int, weekday: int):
        """更新生理状态"""
        physiological = self.emotional_state['physiological']
        
        # 基于时间的精力变化
        if 22 <= hour or hour < 6:  # 深夜
            physiological['energy_level'] *= 0.8
            physiological['fatigue'] += 5
        elif 13 <= hour < 15:  # 午后
            physiological['energy_level'] *= 0.9
            physiological['fatigue'] += 2
        
        # 饥饿度随时间增加
        if 7 <= hour < 9:  # 早餐时间
            physiological['hunger'] += 20
        elif 11 <= hour < 13:  # 午餐时间
            physiological['hunger'] += 30
        elif 17 <= hour < 19:  # 晚餐时间
            physiological['hunger'] += 25
        
        # 进餐后重置饥饿度
        if physiological['last_meal']:
            last_meal_time = datetime.fromisoformat(physiological['last_meal'])
            hours_since_meal = (datetime.now() - last_meal_time).total_seconds() / 3600
            
            if hours_since_meal < 2:
                physiological['hunger'] = max(0, physiological['hunger'] - 40)
        
        # 工作日压力
        if weekday < 5:  # 工作日
            physiological['stress_level'] += 0.1
        else:  # 周末
            physiological['stress_level'] = max(0, physiological['stress_level'] - 0.5)
        
        # 社交能量衰减
        physiological['social_energy'] = max(0, physiological['social_energy'] - 0.2)
        
        # 限制范围
        for key in ['energy_level', 'stress_level', 'social_energy', 'fatigue', 'hunger']:
            physiological[key] = max(0, min(100, physiological[key]))
    
    def _update_circadian_rhythm(self, hour: int):
        """更新昼夜节律"""
        # 昼夜节律对情绪的影响
        if 6 <= hour < 9:  # 清晨
            self.emotional_state['base_emotions']['anticipation'] += 0.5
        elif 21 <= hour < 24:  # 夜晚
            self.emotional_state['base_emotions']['calm'] = min(100, 
                self.emotional_state['base_emotions'].get('calm', 50) + 1)
            self.emotional_state['base_emotions']['joy'] = max(0,
                self.emotional_state['base_emotions']['joy'] - 0.3)
    
    def _update_mood_duration(self, current_time: datetime):
        """更新情绪持续时间"""
        mood = self.emotional_state['current_mood']
        
        if mood['start_time']:
            start_time = datetime.fromisoformat(mood['start_time'])
            duration_minutes = (current_time - start_time).total_seconds() / 60
            mood['duration'] = duration_minutes
            
            # 情绪自然衰减（长时间持续会减弱）
            if duration_minutes > 120:  # 2小时后开始衰减
                decay_rate = min(0.98, 1.0 - (duration_minutes - 120) / 1000)
                mood['intensity'] *= decay_rate
        
        # 限制强度范围
        mood['intensity'] = max(0, min(100, mood['intensity']))
    
    def _record_mood_history(self):
        """记录情绪历史"""
        current_mood = self.emotional_state['current_mood'].copy()
        current_mood['timestamp'] = datetime.now().isoformat()
        
        self.mood_history.append(current_mood)
        
        # 保持历史记录长度
        if len(self.mood_history) > self.max_history_length:
            self.mood_history = self.mood_history[-self.max_history_length:]
    
    def _apply_emotional_decay(self):
        """应用情绪衰减"""
        # 基础情绪趋向中性值
        neutral_values = {
            'joy': 50, 'trust': 50, 'fear': 20, 'surprise': 30,
            'sadness': 25, 'disgust': 10, 'anger': 15, 'anticipation': 40
        }
        
        for emotion, current_value in self.emotional_state['base_emotions'].items():
            neutral = neutral_values.get(emotion, 50)
            # 缓慢向中性值回归
            decay_rate = 0.995  # 每天衰减约1%
            new_value = current_value * decay_rate + neutral * (1 - decay_rate)
            self.emotional_state['base_emotions'][emotion] = new_value
    
    def _recalculate_current_mood(self):
        """重新计算当前主要情绪"""
        base_emotions = self.emotional_state['base_emotions']
        physiological = self.emotional_state['physiological']
        
        # 找出最强的情绪
        dominant_emotion = max(base_emotions.items(), key=lambda x: x[1])
        emotion_name, emotion_value = dominant_emotion
        
        # 映射到情绪名称
        emotion_map = {
            'joy': 'happy',
            'trust': 'content',
            'fear': 'anxious',
            'surprise': 'surprised',
            'sadness': 'sad',
            'disgust': 'disgusted',
            'anger': 'angry',
            'anticipation': 'expectant'
        }
        
        mood_name = emotion_map.get(emotion_name, 'neutral')
        
        # 计算情绪强度（基于基础情绪值和生理状态）
        base_intensity = emotion_value
        physiological_modifier = (
            (physiological['energy_level'] * 0.3 +
             physiological['stress_level'] * 0.2 +
             (100 - physiological['fatigue']) * 0.2 +
             physiological['social_energy'] * 0.3) / 100
        )
        
        intensity = base_intensity * physiological_modifier
        
        # 计算效价（积极/消极）
        positive_emotions = {'joy', 'trust', 'surprise', 'anticipation'}
        negative_emotions = {'fear', 'sadness', 'disgust', 'anger'}
        
        if emotion_name in positive_emotions:
            valence = 0.3 + (emotion_value / 100) * 0.7
        elif emotion_name in negative_emotions:
            valence = -0.3 - (emotion_value / 100) * 0.7
        else:
            valence = 0.0
        
        # 计算唤醒度
        arousal = (physiological['energy_level'] * 0.4 +
                  physiological['stress_level'] * 0.3 +
                  intensity * 0.3) / 100
        
        # 更新当前情绪
        self.emotional_state['current_mood'].update({
            'name': mood_name,
            'intensity': intensity,
            'valence': valence,
            'arousal': arousal,
            'dominance': 0.5  # 暂时固定
        })
    
    def process_event(self, event_type: str, event_data: Dict[str, Any]):
        """处理事件，更新情感"""
        self.logger.info(f"处理情感事件: {event_type}")
        
        # 查找对应的触发器
        trigger = None
        for category in self.emotion_triggers.values():
            if event_type in category:
                trigger = category[event_type]
                break
        
        if trigger:
            self._apply_emotion_trigger(event_type, trigger, event_data)
        
        # 更新情感需求
        self._update_emotional_needs(event_type, event_data)
        
        # 记录到情感记忆
        self._record_emotional_memory(event_type, event_data)
        
        # 立即重新计算情绪
        self._recalculate_current_mood()
        
        # 记录情绪变化
        self._record_mood_history()
    
    def _apply_emotion_trigger(self, event_type: str, trigger: Dict, event_data: Dict):
        """应用情感触发器"""
        affected_emotions = trigger.get('affected_emotions', {})
        intensity = trigger.get('intensity', 0.5)
        duration = trigger.get('duration', 60)
        
        # 应用情绪影响
        for emotion, change in affected_emotions.items():
            current_value = self.emotional_state['base_emotions'].get(emotion, 50)
            new_value = current_value + change * intensity
            
            # 限制范围
            new_value = max(0, min(100, new_value))
            self.emotional_state['base_emotions'][emotion] = new_value
        
        # 如果是时间相关触发器，更新生理状态
        if trigger.get('time_based', False):
            if event_type == 'morning':
                self.emotional_state['physiological']['energy_level'] = min(100,
                    self.emotional_state['physiological']['energy_level'] + 20)
            elif event_type == 'night':
                self.emotional_state['physiological']['fatigue'] = min(100,
                    self.emotional_state['physiological']['fatigue'] + 15)
        
        self.logger.debug(f"应用情感触发器: {event_type}, 影响: {affected_emotions}")
    
    def _update_emotional_needs(self, event_type: str, event_data: Dict):
        """更新情感需求"""
        needs = self.emotional_state['needs']
        
        if event_type in ['received_message', 'quality_time']:
            # 被关注满足关注需求
            needs['need_attention'] = max(0, needs['need_attention'] - 15)
            needs['need_affection'] = max(0, needs['need_affection'] - 10)
        
        elif event_type == 'received_compliment':
            # 被赞美满足成就需求
            needs['need_achievement'] = max(0, needs['need_achievement'] - 20)
        
        elif event_type == 'ignored':
            # 被忽略增加关注需求
            needs['need_attention'] = min(100, needs['need_attention'] + 25)
            needs['need_affection'] = min(100, needs['need_affection'] + 15)
        
        elif event_type == 'conflict':
            # 冲突增加安全需求
            needs['need_safety'] = min(100, needs['need_safety'] + 30)
        
        # 自然需求增长
        for need in needs:
            needs[need] = min(100, needs[need] + 0.1)
    
    def _record_emotional_memory(self, event_type: str, event_data: Dict):
        """记录情感记忆"""
        memory_entry = {
            'event_type': event_type,
            'event_data': event_data,
            'emotional_state': self.get_current_mood(),
            'timestamp': datetime.now().isoformat(),
            'intensity': self._calculate_event_intensity(event_type, event_data)
        }
        
        self.emotional_state['memory']['recent_events'].append(memory_entry)
        
        # 保持最近事件数量
        if len(self.emotional_state['memory']['recent_events']) > 20:
            self.emotional_state['memory']['recent_events'] = \
                self.emotional_state['memory']['recent_events'][-20:]
        
        # 如果是高强度事件，记录为重要时刻
        if memory_entry['intensity'] > 70:
            self.emotional_state['memory']['significant_moments'].append(memory_entry)
            
            if len(self.emotional_state['memory']['significant_moments']) > 10:
                self.emotional_state['memory']['significant_moments'] = \
                    self.emotional_state['memory']['significant_moments'][-10:]
    
    def _calculate_event_intensity(self, event_type: str, event_data: Dict) -> float:
        """计算事件强度"""
        base_intensities = {
            'received_compliment': 65,
            'received_gift': 80,
            'quality_time': 60,
            'ignored': 70,
            'criticized': 75,
            'conflict': 85,
            'received_message': 40,
            'system_activation': 30
        }
        
        intensity = base_intensities.get(event_type, 50)
        
        # 根据事件数据调整
        if 'length' in event_data:
            intensity += min(20, event_data['length'] / 50)
        
        return min(100, intensity)
    
    def get_current_mood(self) -> Dict[str, Any]:
        """获取当前情绪状态"""
        mood = self.emotional_state['current_mood'].copy()
        
        # 添加额外信息
        mood.update({
            'physiological_state': self.emotional_state['physiological'],
            'emotional_needs': self.emotional_state['needs'],
            'base_emotions_summary': {
                'dominant': max(self.emotional_state['base_emotions'].items(), key=lambda x: x[1])[0],
                'average_intensity': sum(self.emotional_state['base_emotions'].values()) / 
                                     len(self.emotional_state['base_emotions'])
            }
        })
        
        return mood
    
    def get_mood_trend(self, hours: int = 24) -> List[Dict]:
        """获取情绪趋势"""
        if not self.mood_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        trend = []
        for mood_entry in self.mood_history:
            timestamp = datetime.fromisoformat(mood_entry['timestamp'])
            if timestamp >= cutoff_time:
                trend.append(mood_entry)
        
        return trend
    
    def should_express_emotion(self, emotion_type: str) -> bool:
        """判断是否应该表达某种情绪"""
        current_mood = self.emotional_state['current_mood']
        needs = self.emotional_state['needs']
        
        if emotion_type == 'affection':
            # 需要表达关爱时
            return (current_mood['valence'] > 0.4 and 
                    needs['need_affection'] < 60 and
                    random.random() < 0.7)
        
        elif emotion_type == 'annoyance':
            # 需要表达不满时
            return (current_mood['valence'] < -0.2 and
                    needs['need_attention'] > 70 and
                    random.random() < 0.4)
        
        elif emotion_type == 'excitement':
            # 需要表达兴奋时
            return (current_mood['arousal'] > 0.6 and
                    current_mood['valence'] > 0.5 and
                    random.random() < 0.6)
        
        return False
    
    def get_emotional_response_style(self) -> Dict[str, Any]:
        """获取情感响应风格"""
        mood = self.emotional_state['current_mood']
        
        # 基于情绪决定响应风格
        if mood['valence'] > 0.5:
            style = {
                'tone': 'warm',
                'verbosity': 'moderate',
                'emoji_frequency': 'high',
                'response_speed': 'fast',
                'segmentation': True if mood['arousal'] > 0.6 else False
            }
        elif mood['valence'] < -0.3:
            style = {
                'tone': 'cool',
                'verbosity': 'low',
                'emoji_frequency': 'low',
                'response_speed': 'slow',
                'segmentation': False
            }
        else:
            style = {
                'tone': 'neutral',
                'verbosity': 'moderate',
                'emoji_frequency': 'medium',
                'response_speed': 'normal',
                'segmentation': False
            }
        
        # 添加情绪特定的修饰
        if mood['name'] == 'happy':
            style['tone'] = 'cheerful'
            style['emoji_frequency'] = 'very_high'
        elif mood['name'] == 'sad':
            style['tone'] = 'gentle'
            style['response_speed'] = 'very_slow'
        
        return style
    
    def save_state(self):
        """保存情感状态"""
        try:
            data_path = Path(self.config.get('env.system.data_path', './data'))
            emotion_dir = data_path / "emotion"
            emotion_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存当前状态
            state_file = emotion_dir / "emotional_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                # 不保存瞬时状态
                save_state = self.emotional_state.copy()
                save_state['current_mood']['start_time'] = datetime.now().isoformat()
                save_state['current_mood']['duration'] = 0
                
                json.dump(save_state, f, ensure_ascii=False, indent=2)
            
            # 保存情绪历史
            history_file = emotion_dir / "mood_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.mood_history[-50:], f, ensure_ascii=False, indent=2)
            
            self.logger.debug("情感状态已保存")
            
        except Exception as e:
            self.logger.error(f"保存情感状态失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            'current_mood': self.emotional_state['current_mood'],
            'physiological': {
                'energy': self.emotional_state['physiological']['energy_level'],
                'stress': self.emotional_state['physiological']['stress_level'],
                'fatigue': self.emotional_state['physiological']['fatigue']
            },
            'needs': self.emotional_state['needs'],
            'stability': self.emotional_state['stability'],
            'history_length': len(self.mood_history)
        }
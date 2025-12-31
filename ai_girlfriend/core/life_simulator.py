#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 生活模拟器模块
模拟虚拟人物的日常生活、作息规律和活动安排
参考：The Sims的生活模拟系统
"""

import json
import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import calendar

class LifeSimulator:
    """生活模拟器 - 模拟AI的日常生活"""
    
    def __init__(self, config_manager):
        """
        初始化生活模拟器
        
        参数:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger("LifeSimulator")
        self.config = config_manager
        
        # 加载角色配置文件
        self.character_config = self.config.get('character', {})
        
        # 初始化生活状态
        self.life_state = self._initialize_life_state()
        
        # 加载保存的状态
        self._load_saved_state()
        
        # 日常活动计划
        self.daily_schedule = self._load_daily_schedule()
        
        # 特殊日期配置
        self.special_dates = self._load_special_dates()
        
        # 当前活动
        self.current_activity = None
        self.activity_start_time = None
        self.next_activity_check = None
        
        self.logger.info("生活模拟器初始化完成")
        self.logger.info(f"当前职业: {self.life_state['occupation']}")
    
    def _initialize_life_state(self) -> Dict[str, Any]:
        """初始化生活状态"""
        character = self.character_config.get('character', {})
        
        # 基本信息
        occupation = character.get('occupation', '数字艺术家')
        location = character.get('location', '上海')
        
        # 财务状况（虚拟）
        financial_state = {
            'income_level': 3,        # 收入等级 (1-5)
            'savings': 50000,         # 存款（虚拟货币）
            'monthly_expenses': 8000, # 月支出
            'last_payday': None       # 最后发薪日
        }
        
        # 健康状况
        health_state = {
            'physical_health': 90.0,   # 身体健康
            'mental_health': 85.0,     # 心理健康
            'energy_reserve': 80.0,    # 能量储备
            'last_checkup': None       # 上次检查
        }
        
        # 社交生活
        social_state = {
            'social_circle_size': 15,          # 社交圈大小
            'close_friends': 3,                # 亲密朋友
            'last_social_event': None,         # 上次社交活动
            'social_battery': 100.0,           # 社交电量
            'weekly_social_quota': 3           # 每周社交配额
        }
        
        # 日常习惯
        daily_habits = {
            'wakeup_time': '07:30',            # 起床时间
            'bedtime': '23:00',                # 睡觉时间
            'meal_times': ['08:00', '12:30', '19:00'],  # 进餐时间
            'work_hours': ['09:00', '18:00'],  # 工作时间
            'weekend_routine': 'flexible'      # 周末作息
        }
        
        # 兴趣爱好状态
        hobby_state = {
            'current_hobbies': character.get('hobbies', []),
            'hobby_proficiency': {},           # 爱好熟练度
            'last_practiced': {},              # 上次练习时间
            'hobby_energy': 100.0              # 爱好能量
        }
        
        # 初始化爱好熟练度
        for hobby in hobby_state['current_hobbies']:
            hobby_state['hobby_proficiency'][hobby] = random.randint(30, 70)
            hobby_state['last_practiced'][hobby] = None
        
        # 工作日状态
        work_state = {
            'current_project': '数字艺术创作',
            'project_deadline': None,
            'workload': 60.0,                  # 工作负荷
            'productivity': 75.0,              # 生产力
            'work_satisfaction': 70.0          # 工作满意度
        }
        
        return {
            'occupation': occupation,
            'location': location,
            'financial': financial_state,
            'health': health_state,
            'social': social_state,
            'habits': daily_habits,
            'hobbies': hobby_state,
            'work': work_state,
            'last_updated': datetime.now().isoformat(),
            'day_in_life': 1                   # 虚拟生活的天数
        }
    
    def _load_saved_state(self):
        """加载保存的状态"""
        try:
            data_path = Path(self.config.get('env.system.data_path', './data'))
            life_dir = data_path / "life"
            life_dir.mkdir(parents=True, exist_ok=True)
            
            state_file = life_dir / "life_state.json"
            
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                
                # 合并状态，保留一些动态值
                for key in ['financial', 'health', 'social', 'hobbies', 'work']:
                    if key in saved_state:
                        self.life_state[key].update(saved_state[key])
                
                # 更新天数
                if 'day_in_life' in saved_state:
                    self.life_state['day_in_life'] = saved_state['day_in_life'] + 1
                
                self.logger.info(f"生活状态已加载，虚拟天数: {self.life_state['day_in_life']}")
                
        except Exception as e:
            self.logger.warning(f"加载生活状态失败: {e}")
    
    def _load_daily_schedule(self) -> Dict[str, List[Dict]]:
        """加载日常作息表"""
        # 从配置文件加载或使用默认
        schedule_config = self.character_config.get('character', {}).get('daily_routine', {})
        
        if schedule_config:
            return schedule_config
        
        # 默认作息（中国城市白领）
        default_schedule = {
            'weekday': [
                {'time': '07:30', 'activity': 'wakeup', 'description': '起床洗漱'},
                {'time': '08:00', 'activity': 'breakfast', 'description': '早餐'},
                {'time': '08:30', 'activity': 'commute', 'description': '通勤'},
                {'time': '09:00', 'activity': 'work', 'description': '开始工作'},
                {'time': '12:00', 'activity': 'lunch', 'description': '午休'},
                {'time': '13:30', 'activity': 'work', 'description': '下午工作'},
                {'time': '18:00', 'activity': 'off_work', 'description': '下班'},
                {'time': '19:00', 'activity': 'dinner', 'description': '晚餐'},
                {'time': '20:00', 'activity': 'leisure', 'description': '休闲时间'},
                {'time': '22:30', 'activity': 'wind_down', 'description': '准备睡觉'},
                {'time': '23:00', 'activity': 'sleep', 'description': '睡觉'}
            ],
            'weekend': [
                {'time': '09:00', 'activity': 'wakeup', 'description': '自然醒'},
                {'time': '10:00', 'activity': 'breakfast', 'description': '早餐'},
                {'time': '11:00', 'activity': 'leisure', 'description': '自由活动'},
                {'time': '14:00', 'activity': 'activity', 'description': '外出或宅家'},
                {'time': '19:00', 'activity': 'dinner', 'description': '晚餐'},
                {'time': '21:00', 'activity': 'entertainment', 'description': '娱乐时间'},
                {'time': '23:30', 'activity': 'sleep', 'description': '睡觉'}
            ]
        }
        
        return default_schedule
    
    def _load_special_dates(self) -> Dict[str, Dict]:
        """加载特殊日期配置"""
        special_dates_config = self.character_config.get('character', {}).get('special_dates', {})
        
        special_dates = {
            # 固定日期节日
            'fixed': {
                '0101': {'type': 'holiday', 'name': '元旦', 'importance': 80},
                '0214': {'type': 'holiday', 'name': '情人节', 'importance': 90},
                '0308': {'type': 'holiday', 'name': '妇女节', 'importance': 60},
                '0501': {'type': 'holiday', 'name': '劳动节', 'importance': 75},
                '1001': {'type': 'holiday', 'name': '国庆节', 'importance': 85},
                '1225': {'type': 'holiday', 'name': '圣诞节', 'importance': 70}
            },
            # 农历节日（简化处理）
            'lunar': {
                '0101': {'type': 'holiday', 'name': '春节', 'importance': 95},
                '0115': {'type': 'holiday', 'name': '元宵节', 'importance': 70},
                '0505': {'type': 'holiday', 'name': '端午节', 'importance': 75},
                '0707': {'type': 'holiday', 'name': '七夕', 'importance': 85},
                '0815': {'type': 'holiday', 'name': '中秋节', 'importance': 80},
                '0909': {'type': 'holiday', 'name': '重阳节', 'importance': 65}
            },
            # 个人重要日期
            'personal': {
                'birthday': {'type': 'birthday', 'date': '0214', 'importance': 95},  # 2月14日生日
                'anniversary': {'type': 'anniversary', 'date': None, 'importance': 90}  # 纪念日
            }
        }
        
        # 合并用户配置
        if special_dates_config:
            for key, value in special_dates_config.items():
                if key in special_dates['personal']:
                    special_dates['personal'][key].update(value)
        
        return special_dates
    
    def update(self, current_time: datetime):
        """更新生活状态"""
        # 检查是否需要更新当前活动
        self._update_current_activity(current_time)
        
        # 更新各种状态
        self._update_time_based_states(current_time)
        
        # 检查特殊日期
        self._check_special_dates(current_time)
        
        # 更新最后更新时间
        self.life_state['last_updated'] = current_time.isoformat()
        
        # 每天一次的状态更新
        if self._is_new_day(current_time):
            self._daily_update(current_time)
    
    def _update_current_activity(self, current_time: datetime):
        """更新当前活动"""
        if not self.next_activity_check or current_time >= self.next_activity_check:
            # 根据时间表确定当前活动
            new_activity = self._get_scheduled_activity(current_time)
            
            if new_activity != self.current_activity:
                self.current_activity = new_activity
                self.activity_start_time = current_time
                self.logger.debug(f"活动变更: {self.current_activity}")
            
            # 设置下次检查时间（30分钟后）
            self.next_activity_check = current_time + timedelta(minutes=30)
    
    def _get_scheduled_activity(self, current_time: datetime) -> str:
        """根据时间表获取计划活动"""
        is_weekend = current_time.weekday() >= 5  # 5=周六, 6=周日
        schedule_type = 'weekend' if is_weekend else 'weekday'
        
        current_hour_min = current_time.strftime("%H:%M")
        
        # 查找当前时间对应的活动
        schedule = self.daily_schedule.get(schedule_type, [])
        
        for item in schedule:
            schedule_time = item['time']
            if current_hour_min >= schedule_time:
                # 找到最近的时间点
                activity = item['activity']
            else:
                break
        
        # 如果没有找到，根据时间推测
        if not activity:
            hour = current_time.hour
            
            if 0 <= hour < 6:
                activity = 'sleeping'
            elif 6 <= hour < 9:
                activity = 'morning_routine'
            elif 9 <= hour < 12:
                activity = 'working' if not is_weekend else 'leisure'
            elif 12 <= hour < 14:
                activity = 'lunch'
            elif 14 <= hour < 18:
                activity = 'working' if not is_weekend else 'leisure'
            elif 18 <= hour < 20:
                activity = 'dinner'
            elif 20 <= hour < 23:
                activity = 'leisure'
            else:
                activity = 'wind_down'
        
        return activity
    
    def _update_time_based_states(self, current_time: datetime):
        """更新时间相关的状态"""
        hour = current_time.hour
        is_weekend = current_time.weekday() >= 5
        
        # 更新健康状态
        health = self.life_state['health']
        
        # 夜晚恢复能量
        if 23 <= hour or hour < 7:
            health['energy_reserve'] = min(100, health['energy_reserve'] + 0.5)
        # 白天消耗能量
        elif 9 <= hour < 18 and not is_weekend:
            health['energy_reserve'] = max(0, health['energy_reserve'] - 0.3)
        
        # 更新社交电量
        social = self.life_state['social']
        
        # 社交活动消耗社交电量
        if self.current_activity in ['socializing', 'working']:
            social['social_battery'] = max(0, social['social_battery'] - 0.2)
        # 独处时恢复
        elif self.current_activity in ['leisure', 'sleeping']:
            social['social_battery'] = min(100, social['social_battery'] + 0.3)
        
        # 更新爱好能量
        hobbies = self.life_state['hobbies']
        
        # 进行爱好活动时消耗
        if self.current_activity == 'hobby':
            hobbies['hobby_energy'] = max(0, hobbies['hobby_energy'] - 0.5)
        # 其他时间恢复
        else:
            hobbies['hobby_energy'] = min(100, hobbies['hobby_energy'] + 0.1)
    
    def _check_special_dates(self, current_time: datetime):
        """检查特殊日期"""
        today_str = current_time.strftime("%m%d")
        
        # 检查固定日期节日
        fixed_dates = self.special_dates['fixed']
        if today_str in fixed_dates:
            holiday = fixed_dates[today_str]
            self._handle_special_date(current_time, holiday)
        
        # 检查个人重要日期
        personal_dates = self.special_dates['personal']
        
        # 生日检查
        birthday = personal_dates.get('birthday', {})
        if birthday.get('date') == today_str:
            self._handle_birthday(current_time)
        
        # 纪念日检查
        anniversary = personal_dates.get('anniversary', {})
        if anniversary.get('date') == today_str:
            self._handle_anniversary(current_time, anniversary)
    
    def _handle_special_date(self, current_time: datetime, holiday_info: Dict):
        """处理特殊节日"""
        holiday_type = holiday_info.get('type', 'holiday')
        holiday_name = holiday_info.get('name', '节日')
        importance = holiday_info.get('importance', 50)
        
        # 记录节日事件
        holiday_event = {
            'type': holiday_type,
            'name': holiday_name,
            'date': current_time.strftime("%Y-%m-%d"),
            'importance': importance,
            'handled': False
        }
        
        # 如果是重要节日，调整活动
        if importance >= 70:
            # 节日当天减少工作，增加休闲
            if self.current_activity == 'working':
                self.current_activity = 'leisure'
                self.logger.info(f"节日 {holiday_name}，休息一天")
            # 发送节日相关消息
            self._generate_holiday_message(holiday_name, current_time)
    
    def _handle_birthday(self, current_time: datetime):
        """处理生日"""
        birthday_event = {
            'type': 'birthday',
            'date': current_time.strftime("%Y-%m-%d"),
            'age': self._calculate_virtual_age(),
            'importance': 95,
            'celebration_planned': False
        }
        
        # 生日当天特殊处理
        self.current_activity = 'celebrating'
        
        # 更新社交状态（生日会有社交活动）
        social = self.life_state['social']
        social['last_social_event'] = current_time.isoformat()
        social['social_circle_size'] = min(50, social['social_circle_size'] + 1)
        
        self.logger.info(f"今天是生日！虚拟年龄: {birthday_event['age']}")
    
    def _handle_anniversary(self, current_time: datetime, anniversary_info: Dict):
        """处理纪念日"""
        days_together = anniversary_info.get('days', 0)
        
        anniversary_event = {
            'type': 'anniversary',
            'date': current_time.strftime("%Y-%m-%d"),
            'days': days_together,
            'importance': 90,
            'celebration_planned': False
        }
        
        # 纪念日特殊处理
        self.current_activity = 'reflecting'
        
        self.logger.info(f"纪念日！在一起 {days_together} 天")
    
    def _generate_holiday_message(self, holiday_name: str, current_time: datetime) -> str:
        """生成节日消息"""
        messages = {
            '春节': "新年快乐！🎉 祝你新的一年心想事成~",
            '情人节': "情人节快乐！💖 今天有没有什么特别的安排呀？",
            '中秋节': "中秋节快乐！🌕 记得吃月饼哦~",
            '圣诞节': "圣诞快乐！🎄 新的一年就要到啦",
            '生日': "今天是我的生日呢~ 🎂 又长大一岁啦！"
        }
        
        return messages.get(holiday_name, f"{holiday_name}快乐！")
    
    def _calculate_virtual_age(self) -> int:
        """计算虚拟年龄"""
        base_age = self.character_config.get('character', {}).get('age', 24)
        days_lived = self.life_state['day_in_life']
        
        # 每365虚拟天增加1岁
        age_increase = days_lived // 365
        
        return base_age + age_increase
    
    def _is_new_day(self, current_time: datetime) -> bool:
        """判断是否是新的一天"""
        last_updated = datetime.fromisoformat(self.life_state['last_updated'])
        
        return current_time.date() > last_updated.date()
    
    def _daily_update(self, current_time: datetime):
        """每日更新"""
        self.life_state['day_in_life'] += 1
        
        # 更新财务状态（虚拟发薪）
        self._update_financial_state(current_time)
        
        # 更新社交状态
        self._update_social_state(current_time)
        
        # 更新工作状态
        self._update_work_state(current_time)
        
        # 更新爱好状态
        self._update_hobby_state(current_time)
        
        self.logger.info(f"虚拟生活第 {self.life_state['day_in_life']} 天")
    
    def _update_financial_state(self, current_time: datetime):
        """更新财务状态"""
        financial = self.life_state['financial']
        
        # 每月1号发薪
        if current_time.day == 1:
            income = financial['income_level'] * 10000  # 简化计算
            financial['savings'] += income
            financial['last_payday'] = current_time.isoformat()
            self.logger.info(f"发薪日！收入: {income}，存款: {financial['savings']}")
        
        # 日常支出
        daily_expense = financial['monthly_expenses'] / 30
        financial['savings'] = max(0, financial['savings'] - daily_expense)
    
    def _update_social_state(self, current_time: datetime):
        """更新社交状态"""
        social = self.life_state['social']
        
        # 恢复社交电量
        social['social_battery'] = min(100, social['social_battery'] + 30)
        
        # 随机社交事件
        if random.random() < 0.3:  # 30%概率有社交事件
            social['last_social_event'] = current_time.isoformat()
            
            # 可能认识新朋友
            if random.random() < 0.2:
                social['social_circle_size'] += 1
    
    def _update_work_state(self, current_time: datetime):
        """更新工作状态"""
        work = self.life_state['work']
        
        # 工作日更新工作状态
        if current_time.weekday() < 5:  # 周一到周五
            # 随机工作事件
            events = [
                {'type': 'project_progress', 'change': random.uniform(5, 15)},
                {'type': 'workload_change', 'change': random.uniform(-10, 10)},
                {'type': 'productivity_change', 'change': random.uniform(-5, 5)}
            ]
            
            for event in events:
                if event['type'] == 'project_progress':
                    # 项目进度
                    pass
                elif event['type'] == 'workload_change':
                    work['workload'] = max(0, min(100, work['workload'] + event['change']))
                elif event['type'] == 'productivity_change':
                    work['productivity'] = max(0, min(100, work['productivity'] + event['change']))
    
    def _update_hobby_state(self, current_time: datetime):
        """更新爱好状态"""
        hobbies = self.life_state['hobbies']
        
        # 随机练习一个爱好
        if hobbies['current_hobbies'] and random.random() < 0.4:
            hobby = random.choice(hobbies['current_hobbies'])
            
            # 提升熟练度
            current_proficiency = hobbies['hobby_proficiency'].get(hobby, 0)
            improvement = random.uniform(0.1, 0.5)
            hobbies['hobby_proficiency'][hobby] = min(100, current_proficiency + improvement)
            
            hobbies['last_practiced'][hobby] = current_time.isoformat()
            
            self.logger.debug(f"练习爱好: {hobby}，熟练度: {hobbies['hobby_proficiency'][hobby]:.1f}")
    
    def get_current_activity(self) -> str:
        """获取当前活动"""
        if not self.current_activity:
            return 'unknown'
        
        activity_map = {
            'wakeup': 'morning_routine',
            'breakfast': 'eating',
            'commute': 'commuting',
            'work': 'working',
            'lunch': 'eating',
            'off_work': 'transitioning',
            'dinner': 'eating',
            'leisure': 'relaxing',
            'wind_down': 'preparing_bed',
            'sleep': 'sleeping',
            'activity': 'engaging',
            'entertainment': 'enjoying'
        }
        
        return activity_map.get(self.current_activity, self.current_activity)
    
    def get_daily_events(self, current_time: datetime) -> List[Dict]:
        """获取当天的日常事件"""
        events = []
        
        # 基于当前活动的事件
        current_activity = self.get_current_activity()
        
        # 添加当前活动事件
        events.append({
            'type': 'current_activity',
            'activity': current_activity,
            'description': self._get_activity_description(current_activity),
            'should_notify': False,
            'data': {'start_time': self.activity_start_time.isoformat() if self.activity_start_time else None}
        })
        
        # 检查是否有需要通知的事件
        notify_events = self._get_notify_events(current_time)
        events.extend(notify_events)
        
        return events
    
    def _get_activity_description(self, activity: str) -> str:
        """获取活动描述"""
        descriptions = {
            'morning_routine': '正在起床洗漱',
            'eating': '正在吃饭',
            'commuting': '正在通勤',
            'working': '正在工作',
            'relaxing': '正在休息',
            'sleeping': '正在睡觉',
            'celebrating': '正在庆祝',
            'reflecting': '正在回忆'
        }
        
        return descriptions.get(activity, '正在活动')
    
    def _get_notify_events(self, current_time: datetime) -> List[Dict]:
        """获取需要通知的事件"""
        events = []
        hour = current_time.hour
        
        # 用餐时间提醒
        meal_times = self.life_state['habits']['meal_times']
        current_hour_min = current_time.strftime("%H:%M")
        
        for meal_time in meal_times:
            if current_hour_min == meal_time:
                meal_name = {
                    '08:00': 'breakfast',
                    '12:30': 'lunch',
                    '19:00': 'dinner'
                }.get(meal_time, 'meal')
                
                events.append({
                    'type': 'meal_time',
                    'activity': 'eating',
                    'description': f'现在是{meal_name}时间',
                    'should_notify': True,
                    'data': {'meal_type': meal_name}
                })
        
        # 工作时间提醒
        if not current_time.weekday() >= 5:  # 工作日
            work_hours = self.life_state['habits']['work_hours']
            
            if current_hour_min == work_hours[0]:
                events.append({
                    'type': 'work_start',
                    'activity': 'working',
                    'description': '开始工作啦',
                    'should_notify': True,
                    'data': {'location': 'office'}
                })
            elif current_hour_min == work_hours[1]:
                events.append({
                    'type': 'work_end',
                    'activity': 'off_work',
                    'description': '下班时间到',
                    'should_notify': True,
                    'data': {}
                })
        
        # 睡觉时间提醒
        bedtime = self.life_state['habits']['bedtime']
        if current_hour_min == bedtime:
            events.append({
                'type': 'bedtime',
                'activity': 'wind_down',
                'description': '该准备睡觉啦',
                'should_notify': True,
                'data': {}
            })
        
        return events
    
    def check_special_dates(self, current_time: datetime) -> List[Dict]:
        """检查特殊日期并返回事件"""
        events = []
        today_str = current_time.strftime("%m%d")
        
        # 检查固定节日
        fixed_dates = self.special_dates['fixed']
        if today_str in fixed_dates:
            holiday = fixed_dates[today_str]
            events.append({
                'type': 'holiday',
                'description': f"今天是{holiday['name']}",
                'should_notify': True,
                'data': holiday
            })
        
        # 检查生日
        birthday = self.special_dates['personal'].get('birthday', {})
        if birthday.get('date') == today_str:
            events.append({
                'type': 'birthday',
                'description': '今天是我的生日！',
                'should_notify': True,
                'data': birthday
            })
        
        return events
    
    def should_initiate_conversation(self) -> bool:
        """判断是否应该主动发起对话"""
        current_activity = self.get_current_activity()
        
        # 不适合主动发起对话的活动
        busy_activities = ['working', 'sleeping', 'commuting', 'eating']
        
        if current_activity in busy_activities:
            return False
        
        # 检查社交电量
        social_battery = self.life_state['social']['social_battery']
        if social_battery < 30:
            return False
        
        # 检查精力水平
        energy = self.life_state['health']['energy_reserve']
        if energy < 40:
            return False
        
        # 随机因素
        return random.random() < 0.3  # 30%概率
    
    def generate_conversation_topic(self) -> str:
        """生成对话话题"""
        current_activity = self.get_current_activity()
        
        # 基于当前活动的话题
        activity_topics = {
            'working': ['工作项目', '同事趣事', '工作挑战'],
            'relaxing': ['最近看的电影', '听的音乐', '读书心得'],
            'eating': ['美食推荐', '烹饪心得', '餐厅体验'],
            'commuting': ['交通状况', '路上见闻', '通勤音乐']
        }
        
        topics = activity_topics.get(current_activity, ['日常琐事', '心情分享', '未来计划'])
        
        # 添加爱好相关话题
        hobbies = self.life_state['hobbies']['current_hobbies']
        if hobbies:
            topics.extend([f'{hobby}相关' for hobby in hobbies[:2]])
        
        return random.choice(topics)
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            'current_activity': self.get_current_activity(),
            'occupation': self.life_state['occupation'],
            'day_in_life': self.life_state['day_in_life'],
            'virtual_age': self._calculate_virtual_age(),
            'health': {
                'energy': self.life_state['health']['energy_reserve'],
                'mental_health': self.life_state['health']['mental_health']
            },
            'social': {
                'battery': self.life_state['social']['social_battery'],
                'circle_size': self.life_state['social']['social_circle_size']
            },
            'work': {
                'workload': self.life_state['work']['workload'],
                'productivity': self.life_state['work']['productivity']
            }
        }
    
    def save_state(self):
        """保存生活状态"""
        try:
            data_path = Path(self.config.get('env.system.data_path', './data'))
            life_dir = data_path / "life"
            life_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存当前状态
            state_file = life_dir / "life_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(self.life_state, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("生活状态已保存")
            
        except Exception as e:
            self.logger.error(f"保存生活状态失败: {e}")
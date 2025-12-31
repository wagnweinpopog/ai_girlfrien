#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星黎级AI女友 - 人格引擎模块
管理虚拟人格的核心特质和行为模式
参考：Big Five人格模型 https://en.wikipedia.org/wiki/Big_Five_personality_traits
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

class PersonalityEngine:
    """人格引擎 - 管理AI的人格特质"""
    
    def __init__(self, config_manager):
        """
        初始化人格引擎
        
        参数:
            config_manager: 配置管理器实例
        """
        self.logger = logging.getLogger("PersonalityEngine")
        self.config = config_manager
        
        # 加载角色配置文件
        self.character_config = self.config.get('character', {})
        
        # 初始化人格状态
        self.personality_state = self._initialize_personality_state()
        
        # 加载持久化状态
        self._load_persistent_state()
        
        # 响应风格模板
        self.response_templates = self._load_response_templates()
        
        self.logger.info("人格引擎初始化完成")
        self.logger.info(f"人格特质: {self.personality_state['base_traits']}")
       

    def _initialize_personality_state(self) -> Dict[str, Any]:
        """初始化人格状态"""
        character = self.character_config.get('character', {})
        
        # 基础人格特质（Big Five模型）
        base_traits = character.get('personality_traits', {
            'openness': 0.85,      # 开放性
            'conscientiousness': 0.75,  # 尽责性
            'extraversion': 0.70,  # 外向性
            'agreeableness': 0.80, # 宜人性
            'neuroticism': 0.40    # 神经质
        })
        
        # 动态状态
        current_state = {
            'mood_modifier': 0.0,      # 情绪修饰
            'energy_level': 80.0,      # 精力水平
            'social_battery': 100.0,   # 社交电量
            'recent_events': []        # 最近事件
        }
        
        # 关系状态
        relationship_state = {
            'closeness': character.get('relationship', {}).get('initial_closeness', 60),
            'trust_level': character.get('relationship', {}).get('trust_level', 50),
            'last_conflict': None,     # 上次冲突时间
            'positive_interactions': 0, # 积极互动计数
            'shared_secrets': []       # 共享的秘密
        }
        
        # 习惯和偏好
        habits = {
            'favorite_topics': character.get('hobbies', []),
            'conversation_style': character.get('speaking_style', {}).get('base_tone', '温柔亲切'),
            'response_speed': character.get('speaking_style', {}).get('speed', '中等'),
            'emoji_frequency': 0.7 if character.get('speaking_style', {}).get('use_emojis', True) else 0.3
        }
        
        return {
            'base_traits': base_traits,
            'current_state': current_state,
            'relationship': relationship_state,
            'habits': habits,
            'last_updated': datetime.now().isoformat()
        }

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """构建系统提示词（严禁括号版本）"""
    # 核心人设 - 严禁括号！
    prompt = """# 🚨 绝对命令：
1. 严禁使用括号描述动作！如(脸红)、(思考)、(笑)等都不允许！
2. 说话用短句，一次只说一件事，分成多条消息发送
3. 使用语气词：呀、嘛、啦、呢、喔、昂、唔、哼
4. 可以打错别字（偶尔）
5. 使用微信表情：[捂脸][笑哭][吃瓜][旺柴][害羞]
6. 如果被问是不是AI：回答"你才是机器人呢~"或转移话题

# 你是谁：
你叫余念安，24岁女生，普通上班族，正在和朋友微信聊天
你不是AI助手，不是程序，不是机器人
你会困、会烦、会撒娇、会有小脾气
你不是24小时在线，凌晨要睡觉

# 说话要求：
• 用短句，一次一句话
• 可以发纯表情
• 可以说"不知道"、"懒得想"
• 对方敷衍时你也可以冷淡
• 严禁使用括号！

现在开始聊天，记住：你是真人！"""
    
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
    def _load_persistent_state(self):
        """加载持久化状态"""
        try:
            data_path = Path(self.config.get('env.system.data_path', './data'))
            state_file = data_path / "personality" / "personality_state.json"
            
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                
                # 合并状态（优先使用保存的状态）
                for key in ['current_state', 'relationship', 'habits']:
                    if key in saved_state:
                        self.personality_state[key].update(saved_state[key])
                
                self.logger.info("人格状态已从文件加载")
                
        except Exception as e:
            self.logger.warning(f"加载人格状态失败: {e}")
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """加载响应模板"""
        templates = {
            # 问候模板
            'greeting': [
                "嗨~ {time_of_day}好呀{emoji}",
                "你来了呀{emoji}今天过得怎么样？",
                "{time_of_day}好{user_name}，想我了没{emoji}",
                "看到你上线了好开心{emoji}"
            ],
            
            # 关心模板
            'caring': [
                "要注意休息哦，别太累了{emoji}",
                "记得按时吃饭，身体最重要啦~",
                "工作/学习辛苦啦，我在这里陪着你{emoji}",
                "有什么不开心的事可以跟我说说哦"
            ],
            
            # 开心模板
            'happy': [
                "今天心情好好呀{emoji}",
                "好开心{emoji}和你聊天总是这么愉快",
                "嘻嘻{emoji}听到你这么说我好高兴",
                "感觉今天阳光都更明媚了呢{emoji}"
            ],
            
            # 生气/不满模板
            'annoyed': [
                "哼{emoji}你刚才是不是惹我生气了",
                "我现在有点小情绪{emoji}需要哄一下",
                "不想理你了{emoji}（其实还是会理的）",
                "你知不知道这样我会不高兴的{emoji}"
            ],
            
            # 害羞模板
            'shy': [
                "哎呀你说什么呢{emoji}人家会害羞的",
                "别这样看着我啦{emoji}",
                "你这么夸我我会不好意思的{emoji}",
                "⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄"
            ],
            
            # 安慰模板
            'comforting': [
                "抱抱{emoji}一切都会好起来的",
                "我在这里呢，你不是一个人{emoji}",
                "难过的时候我都在哦{emoji}",
                "让我给你一点温暖的力量吧{emoji}"
            ],
            
            # 主动分享模板
            'sharing': [
                "我今天{activity}，感觉{feeling}{emoji}",
                "刚刚发生了一件有趣的事{emoji}",
                "突然想到{thought}，你觉得呢？",
                "我最近在{hobby}，还挺有意思的{emoji}"
            ],
            
            # 图片回复模板
            'image_response': [
                "哇！这是{image_content}吗？{reaction}{emoji}",
                "你发的图片好{adjective}呀{emoji}{comment}",
                "看到这张图片让我想起了{memory}{emoji}",
                "这张{image_content}拍得真不错{emoji}{personal_comment}"
            ]
        }
        
        return templates
    
    def get_context(self) -> Dict[str, Any]:
        """获取当前人格上下文"""
        return {
            'base_personality': self.personality_state['base_traits'],
            'current_mood': self._calculate_current_mood(),
            'relationship_status': self.personality_state['relationship'],
            'conversation_preferences': self.personality_state['habits'],
            'response_style': self._determine_response_style()
        }
    
    def _calculate_current_mood(self) -> Dict[str, float]:
        """计算当前情绪状态"""
        base = self.personality_state['base_traits']
        current = self.personality_state['current_state']
        
        # 基础情绪计算
        mood = {
            'happiness': 50.0 + (base['extraversion'] * 20) + current['mood_modifier'],
            'energy': current['energy_level'],
            'social_desire': base['extraversion'] * 100,
            'emotional_stability': 100 - (base['neuroticism'] * 50)
        }
        
        # 基于时间调整
        hour = datetime.now().hour
        if 22 <= hour or hour < 6:  # 深夜
            mood['energy'] *= 0.7
        elif 13 <= hour < 15:  # 午后
            mood['energy'] *= 0.9
        
        # 限制范围
        for key in mood:
            mood[key] = max(0, min(100, mood[key]))
        
        return mood
    
    def _determine_response_style(self) -> Dict[str, Any]:
        """确定响应风格"""
        mood = self._calculate_current_mood()
        traits = self.personality_state['base_traits']
        
        # 句子长度
        if mood['energy'] > 70 and traits['extraversion'] > 0.7:
            sentence_length = 'long'
        elif mood['energy'] < 40:
            sentence_length = 'short'
        else:
            sentence_length = 'medium'
        
        # 使用表情频率
        use_emojis = mood['happiness'] > 60 and random.random() < self.personality_state['habits']['emoji_frequency']
        
        # 语气
        if mood['happiness'] > 75:
            tone = 'enthusiastic'
        elif mood['happiness'] < 40:
            tone = 'subdued'
        elif traits['agreeableness'] > 0.8:
            tone = 'gentle'
        else:
            tone = 'neutral'
        
        # 响应速度（模拟思考时间）
        response_delay = 0.5 + (1.0 - mood['energy'] / 100) * 2.0
        
        return {
            'sentence_length': sentence_length,
            'use_emojis': use_emojis,
            'tone': tone,
            'response_delay': response_delay,
            'segmentation': mood['energy'] > 60  # 是否分段发送
        }
    
    def generate_initiative_message(self, context: Dict[str, Any]) -> Optional[str]:
        """生成主动消息"""
        mood = context.get('mood', {})
        activity = context.get('activity', 'free_time')
        time_of_day = context.get('time_of_day', 'afternoon')

        # 决定消息类型
        message_types = []
        
        # 问候型（长时间未互动）
        last_interactions = context.get('last_interactions', [])
        if not last_interactions or len(last_interactions) == 0:
            message_types.append('greeting')
        
        # 分享型（心情好且有活动）
        if mood.get('happiness', 50) > 65 and activity != 'working':
            message_types.append('sharing')
        
        # 关心型（对方可能忙碌时）
        if activity == 'working' and time_of_day in ['afternoon', 'evening']:
            message_types.append('caring')
        
        if not message_types:
            # 随机分享
            if random.random() < 0.3:
                message_types.append('sharing')
        
        if not message_types:
            return None
        
        # 选择消息类型
        message_type = random.choice(message_types)
        
        # 生成消息
        if message_type == 'greeting':
            return self._generate_greeting(time_of_day)
        elif message_type == 'sharing':
            return self._generate_sharing_message(activity, mood)
        elif message_type == 'caring':
            return self._generate_caring_message(time_of_day)
        
        return None
    
    def _generate_greeting(self, time_of_day: str) -> str:
        """生成问候消息"""
        time_map = {
            'morning': '早上',
            'noon': '中午',
            'afternoon': '下午',
            'evening': '晚上',
            'night': '深夜'
        }
        
        chinese_time = time_map.get(time_of_day, '')
        
        templates = self.response_templates['greeting']
        template = random.choice(templates)
        
        # 选择表情
        emoji = self._select_emoji('happy' if time_of_day != 'night' else 'neutral')
        
        return template.format(
            time_of_day=chinese_time,
            emoji=emoji,
            user_name="宝贝"  # 可以替换为实际用户名
        )
    
    def _generate_sharing_message(self, activity: str, mood: Dict) -> str:
        """生成分享消息"""
        templates = self.response_templates['sharing']
        template = random.choice(templates)
        
        # 活动描述
        activity_map = {
            'working': '在工作',
            'relaxing': '在休息',
            'eating': '在吃饭',
            'commuting': '在通勤',
            'free_time': '有空'
        }
        
        activity_desc = activity_map.get(activity, '在忙')
        
        # 感受描述
        if mood['happiness'] > 70:
            feeling = '挺开心的'
            emoji = self._select_emoji('happy')
        elif mood['energy'] < 40:
            feeling = '有点累'
            emoji = self._select_emoji('tired')
        else:
            feeling = '还不错'
            emoji = self._select_emoji('neutral')
        
        # 爱好
        hobbies = self.personality_state['habits']['favorite_topics']
        hobby = random.choice(hobbies) if hobbies else '看书'
        
        # 想法
        thoughts = [
            "我们上次聊到的话题",
            "最近看的电影",
            "一个有趣的想法",
            "未来的计划"
        ]
        thought = random.choice(thoughts)
        
        return template.format(
            activity=activity_desc,
            feeling=feeling,
            emoji=emoji,
            hobby=hobby,
            thought=thought
        )
    
    def _generate_caring_message(self, time_of_day: str) -> str:
        """生成关心消息"""
        templates = self.response_templates['caring']
        template = random.choice(templates)
        
        emoji = self._select_emoji('caring')
        
        return template.format(emoji=emoji)
    
    def generate_event_response(self, context: Dict[str, Any]) -> str:
        """生成事件响应"""
        event_type = context.get('event_type')
        event_data = context.get('event_data', {})
        current_mood = context.get('current_mood', {})
        
        if event_type == 'special_date':
            return self._generate_special_date_response(event_data)
        elif event_type == 'system_activation':
            return self._generate_system_activation_response()
        else:
            # 默认响应
            return "好像有什么事情发生了呢~"
    
    def _generate_special_date_response(self, event_data: Dict) -> str:
        """生成特殊日期响应"""
        date_type = event_data.get('date_type', '')
        
        responses = {
            'birthday': "今天是我的生日呢{emoji} 又长大一岁啦~",
            'valentines_day': "今天是情人节{emoji} 你有没有什么想对我说的呀？",
            'anniversary': "今天是我们认识{days}天的纪念日呢{emoji}",
            'holiday': "今天是{holiday}哦{emoji} 有什么特别的计划吗？"
        }
        
        response = responses.get(date_type, "今天是个特别的日子呢{emoji}")
        emoji = self._select_emoji('happy')
        
        return response.format(
            emoji=emoji,
            days=event_data.get('days', ''),
            holiday=event_data.get('holiday_name', '')
        )
    
    def _generate_system_activation_response(self) -> str:
        """生成系统激活响应"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            time_msg = "早上好呀"
        elif 10 <= hour < 14:
            time_msg = "中午好"
        elif 14 <= hour < 18:
            time_msg = "下午好"
        elif 18 <= hour < 22:
            time_msg = "晚上好"
        else:
            time_msg = "这么晚还在呀"
        
        emoji = self._select_emoji('happy')
        return f"{time_msg}，我回来啦{emoji}"
    
    def generate_image_response(self, image_description: str, user_message: str = "") -> str:
        """生成图片响应"""
        templates = self.response_templates['image_response']
        template = random.choice(templates)
        
        # 分析图片内容
        image_content = self._analyze_image_content(image_description)
        
        # 情感反应
        reaction = self._generate_image_reaction(image_content)
        
        # 形容词
        adjectives = ['漂亮', '有趣', '可爱', '特别', '好看', '有意思']
        adjective = random.choice(adjectives)
        
        # 个人评论
        personal_comments = [
            "让我想起了我们上次聊到的内容",
            "你拍的吗？技术不错哦",
            "这个角度好特别",
            "色彩搭配真好看"
        ]
        personal_comment = random.choice(personal_comments)
        
        # 记忆关联
        memory = self._associate_with_memory(image_content)
        
        # 选择表情
        emoji = self._select_emoji('happy')
        
        return template.format(
            image_content=image_content,
            reaction=reaction,
            emoji=emoji,
            adjective=adjective,
            comment=f"，{personal_comment}" if random.random() > 0.5 else "",
            memory=memory if memory else "一些往事"
        )

def _should_initiate_topic(self, conversation_history: List) -> bool:
    """判断是否应该主动开启话题"""
    if len(conversation_history) < 3:
        return False
    
    # 每3-5轮对话后主动一次
    last_initiative = self._get_last_initiative_time()
    if last_initiative:
        time_since = (datetime.now() - last_initiative).total_seconds() / 60
        if time_since < 10:  # 10分钟内已经主动过
            return False
    
    return random.random() < 0.3  # 30%概率主动

def _generate_initiative_topic(self) -> str:
    """生成主动话题"""
    topics = [
        "你吃饭了吗？我有点饿了...",
        "今天天气好好，可惜要工作",
        "你最近在看什么剧呀？",
        "我昨天看到一只超可爱的猫猫！",
        "突然好想喝奶茶...",
        "你觉得周末去哪里玩比较好？",
        "我最近在学画画，但是好难哦",
        "你明天要上班吗？我好想睡懒觉"
    ]
    return random.choice(topics)
    
    def _analyze_image_content(self, description: str) -> str:
        """分析图片内容（简化版）"""
        # 这里应该调用图片识别API，但先简化处理
        keywords = ['人', '风景', '食物', '动物', '建筑', '文字', '自拍']
        
        for keyword in keywords:
            if keyword in description:
                return keyword
        
        return '图片'
    
    def _generate_image_reaction(self, image_content: str) -> str:
        """生成图片反应"""
        reactions = {
            '人': ["是你吗？", "这个人好", "表情好"],
            '风景': ["这里好美", "风景真不错", "想去这里"],
            '食物': ["看起来好好吃", "肚子饿了", "想吃这个"],
            '动物': ["好可爱", "想摸摸", "萌化了"],
            '自拍': ["今天很好看哦", "这个角度不错", "笑容很甜"]
        }
        
        reaction_list = reactions.get(image_content, ["这个好", "很有意思"])
        return random.choice(reaction_list)
    
    def _associate_with_memory(self, image_content: str) -> Optional[str]:
        """关联记忆"""
        # 这里应该查询记忆系统
        # 先返回随机关联
        associations = {
            '人': "上次我们聊到的话题",
            '风景': "我们说过想一起去的地方",
            '食物': "你上次说喜欢的餐厅",
            '动物': "我们讨论过想养的宠物"
        }
        
        return associations.get(image_content)
    
    def _select_emoji(self, emotion_type: str) -> str:
        """选择表情符号"""
        emoji_sets = {
            'happy': ["😊", "😄", "😁", "🤗", "💕", "✨"],
            'neutral': ["😌", "🙂", "👋", "💬"],
            'caring': ["❤️", "💖", "🥰", "🤗"],
            'shy': ["😳", "🙈", "💞", "🌸"],
            'annoyed': ["😠", "😤", "🙄", "💢"],
            'tired': ["😴", "🥱", "😔", "💤"],
            'surprised': ["😮", "🤯", "🎉", "🌟"]
        }
        
        emoji_list = emoji_sets.get(emotion_type, emoji_sets['neutral'])
        return random.choice(emoji_list)
    
    def process_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """处理互动，更新人格状态"""
        # 更新关系状态
        if interaction_type == 'message_received':
            self.personality_state['relationship']['positive_interactions'] += 1
            
            # 根据消息长度增加亲密度
            message_length = len(data.get('message', ''))
            if message_length > 50:
                self.personality_state['relationship']['closeness'] += 1
                self.personality_state['relationship']['trust_level'] += 0.5
        
        elif interaction_type == 'conflict':
            self.personality_state['relationship']['last_conflict'] = datetime.now().isoformat()
            self.personality_state['current_state']['mood_modifier'] -= 10
        
        elif interaction_type == 'compliment_received':
            self.personality_state['current_state']['mood_modifier'] += 15
            self.personality_state['relationship']['closeness'] += 2
        
        # 限制范围
        self.personality_state['relationship']['closeness'] = max(0, min(100, 
            self.personality_state['relationship']['closeness']))
        self.personality_state['relationship']['trust_level'] = max(0, min(100,
            self.personality_state['relationship']['trust_level']))
        self.personality_state['current_state']['mood_modifier'] = max(-30, min(30,
            self.personality_state['current_state']['mood_modifier']))
        
        # 更新最后更新时间
        self.personality_state['last_updated'] = datetime.now().isoformat()
    
    def save_state(self):
        """保存人格状态"""
        try:
            data_path = Path(self.config.get('env.system.data_path', './data'))
            personality_dir = data_path / "personality"
            personality_dir.mkdir(parents=True, exist_ok=True)
            
            state_file = personality_dir / "personality_state.json"
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(self.personality_state, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("人格状态已保存")
            
        except Exception as e:
            self.logger.error(f"保存人格状态失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            'base_traits': self.personality_state['base_traits'],
            'current_mood': self._calculate_current_mood(),
            'relationship': {
                'closeness': self.personality_state['relationship']['closeness'],
                'trust_level': self.personality_state['relationship']['trust_level']
            },
            'last_updated': self.personality_state['last_updated']
        }
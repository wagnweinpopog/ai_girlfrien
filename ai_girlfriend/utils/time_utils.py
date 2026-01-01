#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间工具函数
处理时间相关操作和格式化
"""

from datetime import datetime, timedelta, date
from typing import Dict, Tuple, Optional
import logging

class TimeUtils:
    """时间工具类"""
    
    @staticmethod
    def get_current_time() -> datetime:
        """获取当前时间"""
        return datetime.now()
    
    @staticmethod
    def format_time(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化时间"""
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_time(time_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        """解析时间字符串"""
        try:
            return datetime.strptime(time_str, format_str)
        except ValueError:
            return None
    
    @staticmethod
    def get_time_of_day() -> str:
        """获取时间段（早上/中午/下午/晚上/深夜）"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return "morning"
        elif 10 <= hour < 14:
            return "noon"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    @staticmethod
    def get_chinese_time_of_day() -> str:
        """获取中文时间段"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return "早上"
        elif 10 <= hour < 14:
            return "中午"
        elif 14 <= hour < 18:
            return "下午"
        elif 18 <= hour < 22:
            return "晚上"
        else:
            return "深夜"
    
    @staticmethod
    def is_weekend() -> bool:
        """判断是否是周末"""
        return datetime.now().weekday() >= 5  # 5=周六, 6=周日
    
    @staticmethod
    def is_working_hours() -> bool:
        """判断是否是工作时间"""
        now = datetime.now()
        
        # 周末不是工作时间
        if now.weekday() >= 5:
            return False
        
        # 工作时间判断 (9:00-18:00)
        hour = now.hour
        return 9 <= hour < 18
    
    @staticmethod
    def get_chinese_weekday() -> str:
        """获取中文星期几"""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[datetime.now().weekday()]
    
    @staticmethod
    def is_special_date() -> Tuple[bool, Optional[str]]:
        """判断是否是特殊日期"""
        today = datetime.now()
        month_day = today.strftime("%m%d")
        
        special_dates = {
            "0101": "元旦",
            "0214": "情人节",
            "0308": "妇女节",
            "0401": "愚人节",
            "0501": "劳动节",
            "0601": "儿童节",
            "1001": "国庆节",
            "1225": "圣诞节"
        }
        
        if month_day in special_dates:
            return True, special_dates[month_day]
        
        return False, None
    
    @staticmethod
    def calculate_time_diff(start_time: datetime, end_time: datetime = None) -> Dict[str, int]:
        """计算时间差"""
        if end_time is None:
            end_time = datetime.now()
        
        diff = end_time - start_time
        
        # 转换为各种单位
        total_seconds = diff.total_seconds()
        
        return {
            "days": int(total_seconds // 86400),
            "hours": int((total_seconds % 86400) // 3600),
            "minutes": int((total_seconds % 3600) // 60),
            "seconds": int(total_seconds % 60),
            "total_seconds": int(total_seconds)
        }
    
    @staticmethod
    def format_time_diff(diff_dict: Dict[str, int]) -> str:
        """格式化时间差"""
        if diff_dict["days"] > 0:
            return f"{diff_dict['days']}天{diff_dict['hours']}小时"
        elif diff_dict["hours"] > 0:
            return f"{diff_dict['hours']}小时{diff_dict['minutes']}分钟"
        elif diff_dict["minutes"] > 0:
            return f"{diff_dict['minutes']}分钟{diff_dict['seconds']}秒"
        else:
            return f"{diff_dict['seconds']}秒"
    
    @staticmethod
    def should_send_morning_greeting() -> bool:
        """是否应该发送早安问候"""
        now = datetime.now()
        hour = now.hour
        
        # 早上7-9点
        return 7 <= hour < 9
    
    @staticmethod
    def should_send_night_greeting() -> bool:
        """是否应该发送晚安问候"""
        now = datetime.now()
        hour = now.hour
        
        # 晚上10-12点
        return 22 <= hour < 24
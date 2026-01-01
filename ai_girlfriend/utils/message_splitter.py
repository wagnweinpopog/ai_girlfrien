"""
消息拆分器 - 将长消息按标点拆分并逐条发送
"""
import re
import time
import random
from typing import List, Callable, Optional
import logging

class MessageSplitter:
    """消息拆分和逐条发送器"""
    
    def __init__(self, 
                 min_delay: float = 0.3,
                 max_delay: float = 1.5,
                 max_length: int = 50,
                 enable_typing_effect: bool = True):
        """
        初始化消息拆分器
        
        Args:
            min_delay: 最小发送延迟（秒）
            max_delay: 最大发送延迟（秒）
            max_length: 单条消息最大长度（超过会强制拆分）
            enable_typing_effect: 是否启用打字机效果
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_length = max_length
        self.enable_typing_effect = enable_typing_effect
        self.logger = logging.getLogger(__name__)
        
        # 定义拆分标点符号的正则表达式
        self.split_pattern = re.compile(
            r'([。！？\.\!\?][」」）】\)】]?|[；;,、][ ]?|～|…{1,2}|(?<=[^.])\.{3}(?![.]))'
        )
    
    def split_message(self, message: str) -> List[str]:
        """
        将消息拆分成多个短句
        
        Args:
            message: 原始消息
            
        Returns:
            拆分后的消息列表
        """
        if not message or len(message.strip()) == 0:
            return []
            
        message = message.strip()
        
        if len(message) <= self.max_length:
            if not re.search(r'[。！？\.\!\?;；,，]', message):
                return [message]
        
        parts = self.split_pattern.split(message)
        
        sentences = []
        current_sentence = ""
        
        for i in range(0, len(parts), 2):
            if i < len(parts):
                text = parts[i]
                punctuation = parts[i + 1] if i + 1 < len(parts) else ""
                
                if (len(current_sentence) + len(text) > self.max_length and 
                    current_sentence.strip()):
                    sentences.append(current_sentence.strip())
                    current_sentence = text + punctuation
                else:
                    current_sentence += text + punctuation
                
                if punctuation.strip() and current_sentence.strip():
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
        
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        final_sentences = []
        for sentence in sentences:
            if len(sentence) > self.max_length:
                sub_sentences = self._split_long_sentence(sentence)
                final_sentences.extend(sub_sentences)
            else:
                final_sentences.append(sentence)
        
        final_sentences = [s for s in final_sentences if s.strip()]
        
        self.logger.debug(f"消息拆分结果: {len(final_sentences)} 条")
        
        return final_sentences
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """拆分过长的句子"""
        if len(sentence) <= self.max_length:
            return [sentence]
        
        comma_parts = re.split(r'[,，]', sentence)
        if len(comma_parts) > 1 and max(len(p) for p in comma_parts) < self.max_length * 1.5:
            result = []
            for part in comma_parts:
                if part.strip():
                    result.append(part.strip() + ('，' if part != comma_parts[-1] else ''))
            return result
        
        words = sentence.split()
        if len(words) > 1:
            result = []
            current = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 > self.max_length and current:
                    result.append(' '.join(current))
                    current = [word]
                    current_length = len(word)
                else:
                    current.append(word)
                    current_length += len(word) + 1
            
            if current:
                result.append(' '.join(current))
            
            return result
        
        return [sentence[i:i+self.max_length] for i in range(0, len(sentence), self.max_length)]
    
    def send_with_delay(self, 
                       message: str, 
                       send_callback: Callable,
                       progress_callback: Optional[Callable] = None) -> None:
        """
        拆分消息并逐条发送，带有随机延迟
        """
        sentences = self.split_message(message)
        
        if not sentences:
            return
        
        self.logger.info(f"发送消息（拆分为 {len(sentences)} 条）")
        
        for i, sentence in enumerate(sentences):
            if i > 0:
                delay = random.uniform(self.min_delay, self.max_delay)
                length_factor = min(len(sentence) / 20, 2.0)
                delay *= length_factor
                
                if self.enable_typing_effect:
                    typing_delay = min(len(sentence) * 0.05, 1.5)
                    time.sleep(typing_delay)
                
                time.sleep(delay)
            
            try:
                if callable(send_callback):
                    send_callback(sentence)
                else:
                    self.logger.error("send_callback 不可调用")
            except Exception as e:
                self.logger.error(f"发送消息失败: {e}")
            
            if progress_callback and callable(progress_callback):
                progress_callback(i + 1, len(sentences))
        
        self.logger.info("消息发送完成")
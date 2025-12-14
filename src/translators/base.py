"""
翻译器基类
定义翻译器接口和通用功能
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TranslationResult:
    """翻译结果"""
    original: str
    translated: str
    source_lang: str
    target_lang: str
    

class BaseTranslator(ABC):
    """
    翻译器基类
    所有翻译器实现都需要继承此类
    """
    
    def __init__(self, source_lang: str = "en", target_lang: str = "zh"):
        """
        初始化翻译器
        
        Args:
            source_lang: 源语言代码
            target_lang: 目标语言代码
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
    
    @abstractmethod
    def translate(self, text: str) -> TranslationResult:
        """
        翻译单段文本
        
        Args:
            text: 要翻译的文本
        
        Returns:
            TranslationResult对象
        """
        pass
    
    def translate_batch(self, texts: List[str]) -> List[TranslationResult]:
        """
        批量翻译文本
        默认实现逐个翻译，子类可以覆盖实现更高效的批量翻译
        
        Args:
            texts: 要翻译的文本列表
        
        Returns:
            翻译结果列表
        """
        return [self.translate(text) for text in texts]
    
    def _should_skip(self, text: str) -> bool:
        """
        判断是否应该跳过翻译
        
        Args:
            text: 文本内容
        
        Returns:
            是否跳过
        """
        # 跳过空白文本
        if not text or not text.strip():
            return True
        
        # 跳过纯数字
        if text.strip().replace(".", "").replace(",", "").isdigit():
            return True
        
        # 跳过太短的文本（可能是标点或符号）
        if len(text.strip()) < 2:
            return True
        
        return False
    
    def _create_skip_result(self, text: str) -> TranslationResult:
        """创建跳过翻译的结果（原文即译文）"""
        return TranslationResult(
            original=text,
            translated=text,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
        )

"""
文本处理工具
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    清理文本
    
    - 移除多余空白
    - 规范化换行
    - 处理特殊字符
    """
    # 规范化空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除首尾空白
    text = text.strip()
    
    return text


def split_sentences(text: str) -> List[str]:
    """
    将文本分割为句子
    
    支持中英文标点
    """
    # 句子结束标点
    pattern = r'(?<=[.!?。！？])\s+'
    
    sentences = re.split(pattern, text)
    
    return [s.strip() for s in sentences if s.strip()]


def is_cjk_text(text: str) -> bool:
    """
    判断文本是否主要是CJK字符
    """
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return cjk_count > len(text) * 0.3


def estimate_translation_length(
    text: str, 
    source_lang: str, 
    target_lang: str
) -> float:
    """
    估算翻译后的文本长度比例
    
    Args:
        text: 原文
        source_lang: 源语言
        target_lang: 目标语言
    
    Returns:
        估计的长度比例
    """
    # 简单的经验值
    # 英文->中文通常会变短（字符数，但不是视觉宽度）
    # 中文->英文通常会变长
    
    length_ratios = {
        ("en", "zh"): 0.6,
        ("zh", "en"): 1.8,
        ("en", "ja"): 0.8,
        ("ja", "en"): 1.5,
    }
    
    return length_ratios.get((source_lang, target_lang), 1.0)

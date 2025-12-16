"""
翻译器模块
支持多种翻译后端：Google Translate、OpenAI、本地LLM
"""

from .base import BaseTranslator, TranslationResult
from .google import GoogleTranslator
from .openai import OpenAITranslator
from .local_llm import LocalLLMTranslator

__all__ = [
    "BaseTranslator",
    "TranslationResult",
    "GoogleTranslator",
    "OpenAITranslator",
    "LocalLLMTranslator",
    "get_translator",
]


def get_translator(name: str, **kwargs) -> BaseTranslator:
    """
    获取翻译器实例
    
    Args:
        name: 翻译器名称 (google, openai, local_llm)
        **kwargs: 传递给翻译器的配置参数
    
    Returns:
        翻译器实例
    """
    translators = {
        "google": GoogleTranslator,
        "openai": OpenAITranslator,
        "local_llm": LocalLLMTranslator,
    }
    
    if name not in translators:
        raise ValueError(f"未知的翻译器: {name}，可用选项: {list(translators.keys())}")
    
    return translators[name](**kwargs)

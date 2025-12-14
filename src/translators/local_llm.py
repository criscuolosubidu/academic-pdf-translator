"""
本地LLM翻译器
支持vLLM、Ollama等本地部署的LLM服务
使用OpenAI兼容的API接口
"""

from typing import List, Optional
import httpx

from .base import BaseTranslator, TranslationResult


# 默认的学术翻译提示词
DEFAULT_SYSTEM_PROMPT = """你是一位专业的学术论文翻译专家，精通医学和计算机科学领域。
请将以下学术文本翻译成{target_lang}，保持专业术语的准确性。

翻译要求：
1. 保留重要专业术语的英文原文（用括号标注）
2. 保持学术论文的正式语体
3. 确保医学/计算机术语翻译的准确性
4. 不要添加任何解释或额外内容，只输出翻译结果"""


class LocalLLMTranslator(BaseTranslator):
    """
    本地LLM翻译器
    支持任何提供OpenAI兼容API的本地LLM服务（如vLLM、Ollama、LocalAI等）
    """
    
    def __init__(
        self,
        source_lang: str = "en",
        target_lang: str = "zh",
        base_url: str = "http://localhost:8000/v1",
        model: str = "qwen2.5-72b-instruct",
        api_key: str = "not-needed",
        system_prompt: Optional[str] = None,
        timeout: float = 120.0,
    ):
        """
        初始化本地LLM翻译器
        
        Args:
            source_lang: 源语言代码
            target_lang: 目标语言代码
            base_url: 本地LLM服务的API地址
            model: 模型名称
            api_key: API密钥（本地部署通常不需要）
            system_prompt: 自定义系统提示词
            timeout: 请求超时时间（本地模型可能较慢）
        """
        super().__init__(source_lang, target_lang)
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT.format(
            target_lang=self._get_lang_name(target_lang)
        )
    
    def _get_lang_name(self, code: str) -> str:
        """将语言代码转换为语言名称"""
        lang_map = {
            "zh": "中文",
            "en": "English",
            "ja": "日本語",
            "ko": "한국어",
        }
        return lang_map.get(code, code)
    
    def translate(self, text: str) -> TranslationResult:
        """
        使用本地LLM翻译文本
        
        Args:
            text: 要翻译的文本
        
        Returns:
            翻译结果
        """
        if self._should_skip(text):
            return self._create_skip_result(text)
        
        # 使用OpenAI兼容的API格式
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.3,
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
        
        translated = result["choices"][0]["message"]["content"].strip()
        
        return TranslationResult(
            original=text,
            translated=translated,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
        )
    
    def translate_batch(self, texts: List[str]) -> List[TranslationResult]:
        """
        批量翻译
        
        Args:
            texts: 文本列表
        
        Returns:
            翻译结果列表
        """
        return [self.translate(text) for text in texts]
    
    def check_connection(self) -> bool:
        """
        检查与本地LLM服务的连接
        
        Returns:
            连接是否成功
        """
        try:
            url = f"{self.base_url}/models"
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                return response.status_code == 200
        except Exception:
            return False

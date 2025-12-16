"""
OpenAI API 翻译器
使用OpenAI GPT模型进行翻译，适合学术论文的高质量翻译
"""

from typing import List, Optional

from .base import BaseTranslator, TranslationResult


# 默认的学术翻译提示词
DEFAULT_SYSTEM_PROMPT = """你是一位专业的学术论文翻译专家，精通医学和计算机科学领域。
请将以下学术文本翻译成{target_lang}，保持专业术语的准确性。

翻译要求：
1. 保留重要专业术语的英文原文（用括号标注）
2. 保持学术论文的正式语体
3. 确保医学/计算机术语翻译的准确性
4. 不要添加任何解释或额外内容，只输出翻译结果"""


class OpenAITranslator(BaseTranslator):
    """
    OpenAI API 翻译器
    使用GPT模型进行高质量学术翻译
    """
    
    def __init__(
        self,
        source_lang: str = "en",
        target_lang: str = "zh",
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
        system_prompt: Optional[str] = None,
    ):
        """
        初始化OpenAI翻译器
        
        Args:
            source_lang: 源语言代码
            target_lang: 目标语言代码
            api_key: OpenAI API密钥
            model: 使用的模型
            base_url: API基础URL
            system_prompt: 自定义系统提示词
        """
        super().__init__(source_lang, target_lang)
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT.format(
            target_lang=self._get_lang_name(target_lang)
        )
        self._client = None
    
    def _get_lang_name(self, code: str) -> str:
        """将语言代码转换为语言名称"""
        lang_map = {
            "zh": "中文",
            "en": "English",
            "ja": "日本語",
            "ko": "한국어",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
        }
        return lang_map.get(code, code)
    
    @property
    def client(self):
        """延迟加载OpenAI客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("请安装 openai: pip install openai")
        return self._client
    
    def translate(self, text: str) -> TranslationResult:
        """
        使用OpenAI翻译文本
        
        Args:
            text: 要翻译的文本
        
        Returns:
            翻译结果
        """
        if self._should_skip(text):
            return self._create_skip_result(text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.3,  # 翻译任务使用较低温度保证一致性
        )
        
        translated = response.choices[0].message.content.strip()
        
        return TranslationResult(
            original=text,
            translated=translated,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
        )
    
    def translate_batch(self, texts: List[str]) -> List[TranslationResult]:
        """
        批量翻译（逐个调用，可以考虑使用异步优化）
        
        Args:
            texts: 文本列表
        
        Returns:
            翻译结果列表
        """
        # 对于需要高质量翻译的场景，逐个翻译以保证质量
        # 如果需要加速，可以使用 asyncio 并发
        return [self.translate(text) for text in texts]

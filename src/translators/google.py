"""
Google Translate API 翻译器
使用Google Cloud Translation API
"""

from typing import List, Optional

from .base import BaseTranslator, TranslationResult


class GoogleTranslator(BaseTranslator):
    """
    Google Translate API 翻译器
    
    需要设置环境变量 GOOGLE_APPLICATION_CREDENTIALS 指向服务账号密钥文件
    或者使用 gcloud auth application-default login 进行认证
    """
    
    def __init__(
        self,
        source_lang: str = "en",
        target_lang: str = "zh",
        project_id: Optional[str] = None,
    ):
        """
        初始化Google翻译器
        
        Args:
            source_lang: 源语言代码
            target_lang: 目标语言代码
            project_id: GCP项目ID
        """
        super().__init__(source_lang, target_lang)
        self.project_id = project_id
        self._client = None
    
    @property
    def client(self):
        """延迟加载Google Translate客户端"""
        if self._client is None:
            try:
                from google.cloud import translate_v2 as translate
                self._client = translate.Client()
            except ImportError:
                raise ImportError(
                    "请安装 google-cloud-translate: pip install google-cloud-translate"
                )
        return self._client
    
    def translate(self, text: str) -> TranslationResult:
        """
        使用Google Translate翻译文本
        
        Args:
            text: 要翻译的文本
        
        Returns:
            翻译结果
        """
        if self._should_skip(text):
            return self._create_skip_result(text)
        
        result = self.client.translate(
            text,
            target_language=self.target_lang,
            source_language=self.source_lang,
        )
        
        return TranslationResult(
            original=text,
            translated=result["translatedText"],
            source_lang=self.source_lang,
            target_lang=self.target_lang,
        )
    
    def translate_batch(self, texts: List[str]) -> List[TranslationResult]:
        """
        批量翻译（Google API支持批量请求）
        
        Args:
            texts: 文本列表
        
        Returns:
            翻译结果列表
        """
        if not texts:
            return []
        
        # 分离需要翻译和不需要翻译的文本
        results = []
        to_translate = []
        to_translate_indices = []
        
        for i, text in enumerate(texts):
            if self._should_skip(text):
                results.append(self._create_skip_result(text))
            else:
                results.append(None)  # 占位
                to_translate.append(text)
                to_translate_indices.append(i)
        
        # 批量翻译
        if to_translate:
            batch_results = self.client.translate(
                to_translate,
                target_language=self.target_lang,
                source_language=self.source_lang,
            )
            
            for idx, result in zip(to_translate_indices, batch_results):
                results[idx] = TranslationResult(
                    original=texts[idx],
                    translated=result["translatedText"],
                    source_lang=self.source_lang,
                    target_lang=self.target_lang,
                )
        
        return results

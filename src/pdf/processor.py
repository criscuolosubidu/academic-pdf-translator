"""
PDF处理器
基于MinerU解析PDF，翻译Markdown内容
"""

import re
import os
import shutil
from enum import Enum
from pathlib import Path
from typing import List, Optional, Callable
from tqdm import tqdm
from loguru import logger


class OutputFormat(Enum):
    """输出格式枚举"""
    PDF = "pdf"
    MARKDOWN = "markdown"
    BOTH = "both"

from .mineru_parser import MineruParser, ParsedDocument
from ..translators.base import BaseTranslator


class PDFProcessor:
    """
    PDF处理器
    使用MinerU解析PDF为Markdown，然后翻译内容
    """
    
    def __init__(
        self,
        translator: BaseTranslator,
        bilingual: bool = False,
        mineru_backend: str = "pipeline",
        mineru_lang: str = "ch",
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """
        初始化PDF处理器
        
        Args:
            translator: 翻译器实例
            bilingual: 是否生成双语对照
            mineru_backend: MinerU后端类型
            mineru_lang: MinerU语言设置
            progress_callback: 进度回调函数 (current, total)
        """
        self.translator = translator
        self.bilingual = bilingual
        self.progress_callback = progress_callback
        
        self.parser = MineruParser(
            backend=mineru_backend,
            lang=mineru_lang,
        )
    
    def _split_into_paragraphs(self, markdown: str) -> List[dict]:
        """
        将Markdown分割为可翻译的段落
        
        Args:
            markdown: Markdown内容
        
        Returns:
            段落列表，每个元素包含 {text, translatable, type}
        """
        paragraphs = []
        lines = markdown.split('\n')
        
        current_block = []
        in_code_block = False
        in_table = False
        
        for line in lines:
            # 检测代码块
            if line.strip().startswith('```'):
                if current_block:
                    paragraphs.append({
                        'text': '\n'.join(current_block),
                        'translatable': not in_code_block and not in_table,
                        'type': 'text'
                    })
                    current_block = []
                in_code_block = not in_code_block
                paragraphs.append({
                    'text': line,
                    'translatable': False,
                    'type': 'code_fence'
                })
                continue
            
            # 代码块内的内容不翻译
            if in_code_block:
                paragraphs.append({
                    'text': line,
                    'translatable': False,
                    'type': 'code'
                })
                continue
            
            # 检测表格
            if line.strip().startswith('|') or line.strip().startswith('<table'):
                if current_block:
                    paragraphs.append({
                        'text': '\n'.join(current_block),
                        'translatable': True,
                        'type': 'text'
                    })
                    current_block = []
                # 表格内容暂不翻译（保持格式）
                paragraphs.append({
                    'text': line,
                    'translatable': False,
                    'type': 'table'
                })
                continue
            
            # 检测图片引用
            if re.match(r'^\s*!\[.*\]\(.*\)\s*$', line):
                if current_block:
                    paragraphs.append({
                        'text': '\n'.join(current_block),
                        'translatable': True,
                        'type': 'text'
                    })
                    current_block = []
                paragraphs.append({
                    'text': line,
                    'translatable': False,
                    'type': 'image'
                })
                continue
            
            # 检测公式块
            if line.strip().startswith('$$') or line.strip().startswith('$'):
                if current_block:
                    paragraphs.append({
                        'text': '\n'.join(current_block),
                        'translatable': True,
                        'type': 'text'
                    })
                    current_block = []
                paragraphs.append({
                    'text': line,
                    'translatable': False,
                    'type': 'formula'
                })
                continue
            
            # 空行分隔段落
            if not line.strip():
                if current_block:
                    paragraphs.append({
                        'text': '\n'.join(current_block),
                        'translatable': True,
                        'type': 'text'
                    })
                    current_block = []
                paragraphs.append({
                    'text': '',
                    'translatable': False,
                    'type': 'empty'
                })
                continue
            
            # 普通文本行
            current_block.append(line)
        
        # 处理最后的块
        if current_block:
            paragraphs.append({
                'text': '\n'.join(current_block),
                'translatable': True,
                'type': 'text'
            })
        
        return paragraphs
    
    def _should_translate(self, text: str) -> bool:
        """
        判断文本是否需要翻译
        """
        text = text.strip()
        
        # 太短的文本
        if len(text) < 3:
            return False
        
        # 纯数字或标点
        if text.replace('.', '').replace(',', '').replace(' ', '').isdigit():
            return False
        
        # 纯标题标记
        if re.match(r'^#+\s*$', text):
            return False
        
        return True
    
    def _translate_paragraph(self, text: str) -> str:
        """
        翻译单个段落，保留Markdown格式标记
        """
        if not self._should_translate(text):
            return text
        
        # 提取标题前缀
        header_match = re.match(r'^(#{1,6}\s+)', text)
        header_prefix = header_match.group(1) if header_match else ''
        content = text[len(header_prefix):] if header_prefix else text
        
        # 翻译内容
        try:
            result = self.translator.translate(content)
            translated = result.translated
        except Exception as e:
            logger.warning(f"翻译失败: {e}")
            return text
        
        return header_prefix + translated
    
    def translate_markdown(self, markdown: str) -> str:
        """
        翻译Markdown内容
        
        Args:
            markdown: 原始Markdown内容
        
        Returns:
            翻译后的Markdown内容
        """
        paragraphs = self._split_into_paragraphs(markdown)
        
        # 统计可翻译段落数
        translatable_count = sum(1 for p in paragraphs if p['translatable'] and self._should_translate(p['text']))
        
        result_parts = []
        translated_count = 0
        
        for para in tqdm(paragraphs, desc="翻译中", disable=translatable_count < 5):
            if para['translatable'] and self._should_translate(para['text']):
                translated_text = self._translate_paragraph(para['text'])
                
                if self.bilingual:
                    # 双语模式：翻译在前，原文在引用块中
                    result_parts.append(translated_text)
                    result_parts.append('')
                    # 将原文作为引用
                    original_lines = para['text'].split('\n')
                    quoted = '\n'.join(f'> {line}' for line in original_lines)
                    result_parts.append(quoted)
                else:
                    result_parts.append(translated_text)
                
                translated_count += 1
                if self.progress_callback:
                    self.progress_callback(translated_count, translatable_count)
            else:
                result_parts.append(para['text'])
        
        return '\n'.join(result_parts)
    
    def process(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        pages: Optional[List[int]] = None,
    ) -> str:
        """
        处理PDF文件
        
        Args:
            input_path: 输入PDF路径
            output_path: 输出目录或文件路径
            pages: 要处理的页码列表 (0-based)，默认处理所有页
        
        Returns:
            输出的Markdown文件路径
        """
        input_path = Path(input_path)
        
        # 确定输出路径
        if output_path is None:
            output_dir = input_path.parent / input_path.stem
        else:
            output_path = Path(output_path)
            if output_path.suffix == '.md':
                output_dir = output_path.parent
            else:
                output_dir = output_path
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 计算页码范围
        start_page = 0
        end_page = None
        if pages:
            start_page = min(pages)
            end_page = max(pages) + 1
        
        logger.info(f"正在解析PDF: {input_path}")
        
        # 使用MinerU解析PDF
        parsed = self.parser.parse_pdf(
            str(input_path),
            str(output_dir),
            start_page=start_page,
            end_page=end_page,
        )
        
        logger.info("PDF解析完成，开始翻译...")
        
        # 翻译Markdown内容
        translated_markdown = self.translate_markdown(parsed.markdown_content)
        
        # 保存翻译后的Markdown
        md_filename = f"{input_path.stem}_translated.md"
        final_output_dir = output_dir / input_path.stem / "auto"
        final_output_dir.mkdir(parents=True, exist_ok=True)
        
        md_output_path = final_output_dir / md_filename
        
        with open(md_output_path, 'w', encoding='utf-8') as f:
            f.write(translated_markdown)
        
        logger.info(f"翻译完成，已保存到: {md_output_path}")
        
        if parsed.images_dir and os.path.exists(parsed.images_dir):
            target_images_dir = final_output_dir / "images"
            if os.path.realpath(parsed.images_dir) != os.path.realpath(target_images_dir):
                if os.path.exists(target_images_dir):
                    shutil.rmtree(target_images_dir)
                shutil.copytree(parsed.images_dir, target_images_dir)
        return str(md_output_path)

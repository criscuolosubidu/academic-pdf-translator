"""
PDF处理器
整合提取、翻译、渲染的完整流程
"""

from pathlib import Path
from typing import List, Optional, Callable, Literal
from tqdm import tqdm
from enum import Enum

from .extractor import PDFExtractor, PageContent, TextBlock
from .renderer import PDFRenderer
from .markdown_renderer import MarkdownRenderer
from ..translators.base import BaseTranslator


class OutputFormat(Enum):
    """输出格式"""
    PDF = "pdf"
    MARKDOWN = "markdown"
    BOTH = "both"  # 同时输出PDF和Markdown


class PDFProcessor:
    """
    PDF处理器
    提供完整的PDF翻译工作流
    """
    
    def __init__(
        self,
        translator: BaseTranslator,
        font_scale: float = 0.9,
        bilingual: bool = False,
        fallback_font: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        output_format: OutputFormat = OutputFormat.PDF,
    ):
        """
        初始化PDF处理器
        
        Args:
            translator: 翻译器实例
            font_scale: 字体缩放因子
            bilingual: 是否生成双语对照
            fallback_font: 备用字体路径
            progress_callback: 进度回调函数 (current, total)
            output_format: 输出格式 (pdf, markdown, both)
        """
        self.translator = translator
        self.font_scale = font_scale
        self.bilingual = bilingual
        self.fallback_font = fallback_font
        self.progress_callback = progress_callback
        self.output_format = output_format
    
    def _should_translate_block(self, block: TextBlock) -> bool:
        """
        判断文本块是否需要翻译
        
        跳过：
        - 太短的文本（可能是页码、符号等）
        - 纯数字
        - 可能是公式的内容
        """
        text = block.text.strip()
        
        # 太短
        if len(text) < 3:
            return False
        
        # 纯数字或标点
        if text.replace(".", "").replace(",", "").replace(" ", "").isdigit():
            return False
        
        # 可能是公式（包含大量特殊字符）
        special_chars = sum(1 for c in text if not c.isalnum() and c not in " .,;:!?-'\"")
        if special_chars / len(text) > 0.3:
            return False
        
        return True
    
    def _merge_blocks_to_paragraphs(
        self, 
        blocks: List[TextBlock],
        line_threshold: float = 5.0,
    ) -> List[List[TextBlock]]:
        """
        将相邻的文本块合并为段落
        
        Args:
            blocks: 文本块列表
            line_threshold: 行间距阈值
        
        Returns:
            段落列表（每个段落是文本块列表）
        """
        if not blocks:
            return []
        
        # 按y坐标排序
        sorted_blocks = sorted(blocks, key=lambda b: (b.y0, b.x0))
        
        paragraphs = []
        current_para = [sorted_blocks[0]]
        
        for block in sorted_blocks[1:]:
            prev_block = current_para[-1]
            
            # 判断是否属于同一段落
            # 条件：y坐标接近，或x坐标连续
            y_diff = abs(block.y0 - prev_block.y0)
            same_line = y_diff < line_threshold
            
            # 检查是否是下一行（行间距合理）
            next_line = (
                block.y0 > prev_block.y1 and 
                block.y0 - prev_block.y1 < prev_block.height * 1.5
            )
            
            if same_line or next_line:
                current_para.append(block)
            else:
                paragraphs.append(current_para)
                current_para = [block]
        
        if current_para:
            paragraphs.append(current_para)
        
        return paragraphs
    
    def translate_page(self, page_content: PageContent) -> PageContent:
        """
        翻译单页内容
        
        Args:
            page_content: 页面内容
        
        Returns:
            翻译后的页面内容
        """
        # 筛选需要翻译的块
        blocks_to_translate = [
            b for b in page_content.text_blocks 
            if self._should_translate_block(b)
        ]
        
        # 合并为段落以获得更好的翻译质量
        paragraphs = self._merge_blocks_to_paragraphs(blocks_to_translate)
        
        for para_blocks in paragraphs:
            # 合并段落文本
            para_text = " ".join(b.text for b in para_blocks)
            
            # 翻译整个段落
            result = self.translator.translate(para_text)
            
            # 将翻译结果分配回各个块
            # 简单策略：按原文比例分配
            if len(para_blocks) == 1:
                para_blocks[0].translated_text = result.translated
            else:
                # 多个块，按比例分配翻译结果
                translated_words = result.translated
                total_len = sum(len(b.text) for b in para_blocks)
                
                current_pos = 0
                for block in para_blocks:
                    ratio = len(block.text) / total_len
                    char_count = int(len(translated_words) * ratio)
                    
                    # 找到合适的分割点（尽量在标点或空格处分割）
                    end_pos = current_pos + char_count
                    
                    # 尝试找到更好的分割点
                    for i in range(end_pos, min(end_pos + 10, len(translated_words))):
                        if i < len(translated_words) and translated_words[i] in "，。、；：？！ ":
                            end_pos = i + 1
                            break
                    
                    block.translated_text = translated_words[current_pos:end_pos]
                    current_pos = end_pos
                
                # 最后一个块获取剩余文本
                if para_blocks and current_pos < len(translated_words):
                    para_blocks[-1].translated_text += translated_words[current_pos:]
        
        return page_content
    
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
            output_path: 输出路径（不带扩展名时会自动添加）
            pages: 要处理的页码列表，默认处理所有页
        
        Returns:
            输出文件路径（如果是both模式，返回Markdown路径）
        """
        input_path = Path(input_path)
        
        # 确定输出路径
        if output_path is None:
            base_output = input_path.with_stem(f"{input_path.stem}_translated")
        else:
            base_output = Path(output_path)
            # 如果指定了完整路径，根据格式调整扩展名
            if base_output.suffix:
                base_output = base_output.with_suffix("")
        
        # 提取PDF内容
        with PDFExtractor(str(input_path)) as extractor:
            total_pages = extractor.page_count
            
            if pages is None:
                pages = list(range(total_pages))
            
            # 提取所有页面
            all_pages_content = []
            for i in range(total_pages):
                all_pages_content.append(extractor.extract_page(i))
        
        # 翻译指定页面
        for i in tqdm(pages, desc="翻译中"):
            if i < len(all_pages_content):
                all_pages_content[i] = self.translate_page(all_pages_content[i])
                
                if self.progress_callback:
                    self.progress_callback(i + 1, len(pages))
        
        output_files = []
        
        # 根据输出格式渲染
        if self.output_format in (OutputFormat.PDF, OutputFormat.BOTH):
            pdf_output = base_output.with_suffix(".pdf")
            
            renderer = PDFRenderer(
                font_scale=self.font_scale,
                fallback_font_path=self.fallback_font,
                bilingual=self.bilingual,
            )
            
            renderer.render(
                str(input_path),
                all_pages_content,
                str(pdf_output),
            )
            output_files.append(str(pdf_output))
        
        if self.output_format in (OutputFormat.MARKDOWN, OutputFormat.BOTH):
            md_output = base_output.with_suffix(".md")
            
            md_renderer = MarkdownRenderer(
                bilingual=self.bilingual,
                include_page_breaks=True,
                preserve_structure=True,
            )
            
            # 使用文件名作为标题
            title = input_path.stem.replace("_", " ").replace("-", " ")
            
            md_renderer.render(
                all_pages_content,
                str(md_output),
                title=title,
            )
            output_files.append(str(md_output))
        
        # 返回主要输出路径
        if self.output_format == OutputFormat.MARKDOWN:
            return output_files[0]
        elif self.output_format == OutputFormat.BOTH:
            return output_files[-1]  # 返回Markdown路径
        else:
            return output_files[0]  # 返回PDF路径

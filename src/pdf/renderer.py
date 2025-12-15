"""
PDF渲染模块
将翻译后的文本重新渲染到PDF中，保持原有布局
"""

from pathlib import Path
from typing import List, Optional, Tuple
import io
import textwrap

from .extractor import PageContent, TextBlock


class PDFRenderer:
    """
    PDF渲染器
    将翻译后的文本渲染到新的PDF中，尽可能保持原有格式
    """
    
    def __init__(
        self,
        font_scale: float = 0.9,
        fallback_font_path: Optional[str] = None,
        bilingual: bool = False,
    ):
        """
        初始化渲染器
        
        Args:
            font_scale: 字体缩放因子（翻译后文本可能更长）
            fallback_font_path: 备用字体路径（用于CJK字符）
            bilingual: 是否生成双语对照
        """
        self.font_scale = font_scale
        self.fallback_font_path = fallback_font_path
        self.bilingual = bilingual
        self._fitz = None
        self._font_cache = {}
    
    @property
    def fitz(self):
        """延迟导入fitz"""
        if self._fitz is None:
            try:
                import fitz
                self._fitz = fitz
            except ImportError:
                raise ImportError("请安装 PyMuPDF: pip install PyMuPDF")
        return self._fitz
    
    def _get_font_for_text(self, text: str, font_name: str) -> Tuple[str, Optional[bytes]]:
        """
        根据文本内容选择合适的字体
        
        对于包含CJK字符的文本，需要使用支持CJK的字体
        """
        # 检查是否包含CJK字符
        has_cjk = any('\u4e00' <= char <= '\u9fff' or
                      '\u3400' <= char <= '\u4dbf' or
                      '\u3000' <= char <= '\u303f' for char in text)
        
        if has_cjk:
            # 使用内置的CJK字体
            # PyMuPDF支持使用系统字体或嵌入字体
            return "china-s", None  # 使用PyMuPDF内置的简体中文字体
        
        # 对于纯英文，尝试使用原字体或默认字体
        return "helv", None  # Helvetica
    
    def _get_font(self, font_name: str):
        """获取或缓存字体对象"""
        if font_name not in self._font_cache:
            self._font_cache[font_name] = self.fitz.Font(font_name)
        return self._font_cache[font_name]
    
    def _calculate_text_width(self, text: str, font, font_size: float) -> float:
        """计算文本的实际宽度"""
        try:
            return font.text_length(text, fontsize=font_size)
        except Exception:
            # 粗略估计：中文字符约等于字体大小，英文约0.6倍
            width = 0
            for char in text:
                if '\u4e00' <= char <= '\u9fff':
                    width += font_size
                else:
                    width += font_size * 0.5
            return width
    
    def _wrap_text_to_width(
        self,
        text: str,
        font,
        font_size: float,
        max_width: float,
    ) -> List[str]:
        """
        将文本按指定宽度换行
        
        Args:
            text: 待换行的文本
            font: 字体对象
            font_size: 字体大小
            max_width: 最大宽度
        
        Returns:
            换行后的文本行列表
        """
        if not text.strip():
            return []
        
        lines = []
        current_line = ""
        
        # 对于中文，按字符分割；对于英文，按单词分割
        has_cjk = any('\u4e00' <= c <= '\u9fff' for c in text)
        
        if has_cjk:
            # 按字符处理
            for char in text:
                test_line = current_line + char
                width = self._calculate_text_width(test_line, font, font_size)
                
                if width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
        else:
            # 按单词处理
            words = text.split()
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                width = self._calculate_text_width(test_line, font, font_size)
                
                if width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text]
    
    def _calculate_font_size(
        self, 
        original_size: float, 
        original_text: str, 
        translated_text: str,
        max_width: float,
        max_height: float,
        font,
    ) -> float:
        """
        计算翻译后文本应该使用的字体大小
        
        考虑翻译后文本长度变化和可用空间，动态调整字体大小
        """
        # 从原始大小开始尝试
        size = original_size * self.font_scale
        min_size = max(6, original_size * 0.4)  # 最小字体
        
        # 逐步减小字体直到文本能够容纳
        while size > min_size:
            lines = self._wrap_text_to_width(translated_text, font, size, max_width)
            total_height = len(lines) * size * 1.2  # 行高约1.2倍
            
            if total_height <= max_height * 1.5:  # 允许一定的溢出
                break
            
            size -= 0.5
        
        return max(size, min_size)
    
    def render_page(
        self,
        source_doc,
        page_no: int,
        page_content: PageContent,
        output_doc,
    ) -> None:
        """
        渲染单页
        
        Args:
            source_doc: 源PDF文档
            page_no: 页码
            page_content: 页面内容（包含翻译后的文本）
            output_doc: 输出PDF文档
        """
        fitz = self.fitz
        
        # 复制原页面到输出文档
        output_doc.insert_pdf(source_doc, from_page=page_no, to_page=page_no)
        out_page = output_doc[-1]
        
        # 创建遮罩和文本层
        for block in page_content.text_blocks:
            if block.translated_text is None:
                continue
            
            # 获取文本区域
            rect = fitz.Rect(block.bbox)
            
            # 稍微扩展区域以确保完全覆盖
            expanded_rect = fitz.Rect(
                rect.x0 - 1,
                rect.y0 - 1,
                rect.x1 + 1,
                rect.y1 + 1,
            )
            
            # 创建白色背景遮盖原文本
            shape = out_page.new_shape()
            shape.draw_rect(expanded_rect)
            shape.finish(color=None, fill=(1, 1, 1))  # 白色填充
            shape.commit()
            
            # 选择字体
            font_name, _ = self._get_font_for_text(
                block.translated_text, 
                block.font_name
            )
            
            # 获取字体对象
            font = self._get_font(font_name)
            
            # 计算字体大小（考虑换行）
            font_size = self._calculate_font_size(
                block.font_size,
                block.text,
                block.translated_text,
                block.width,
                block.height,
                font,
            )
            
            # 转换颜色
            color = self._int_to_rgb(block.font_color)
            
            # 将文本换行
            lines = self._wrap_text_to_width(
                block.translated_text,
                font,
                font_size,
                block.width,
            )
            
            # 计算行高
            line_height = font_size * 1.15
            
            # 插入翻译后的文本（逐行）
            try:
                tw = fitz.TextWriter(out_page.rect)
                
                # 计算起始位置
                y_start = block.y0 + font_size
                
                for i, line in enumerate(lines):
                    y_pos = y_start + i * line_height
                    
                    # 如果超出区域太多，跳过后续行
                    if y_pos > block.y1 + block.height * 0.5:
                        break
                    
                    text_point = fitz.Point(block.x0, y_pos)
                    tw.append(
                        text_point,
                        line,
                        font=font,
                        fontsize=font_size,
                    )
                
                tw.write_text(out_page, color=color)
                
            except Exception:
                # 回退到使用 insert_textbox 方法，自动处理换行
                try:
                    out_page.insert_textbox(
                        rect,
                        block.translated_text,
                        fontname=font_name,
                        fontsize=font_size,
                        color=color,
                        align=0,  # 左对齐
                    )
                except Exception:
                    # 最后回退到简单的insert_text
                    out_page.insert_text(
                        fitz.Point(block.x0, block.y0 + font_size),
                        block.translated_text[:50] + "..." if len(block.translated_text) > 50 else block.translated_text,
                        fontname=font_name,
                        fontsize=font_size,
                        color=color,
                    )
    
    def render_page_overlay(
        self,
        source_doc,
        page_no: int,
        page_content: PageContent,
        output_doc,
    ) -> None:
        """
        渲染双语对照页面
        翻译文本作为叠加层显示在原文下方
        
        Args:
            source_doc: 源PDF文档
            page_no: 页码
            page_content: 页面内容
            output_doc: 输出文档
        """
        fitz = self.fitz
        
        # 复制原页面
        output_doc.insert_pdf(source_doc, from_page=page_no, to_page=page_no)
        out_page = output_doc[-1]
        
        for block in page_content.text_blocks:
            if block.translated_text is None:
                continue
            
            # 在原文下方添加翻译
            font_name, _ = self._get_font_for_text(
                block.translated_text,
                block.font_name
            )
            
            # 使用较小的字体
            font_size = block.font_size * 0.7
            
            # 在原文块下方添加翻译（使用浅色背景）
            trans_y = block.y1 + 2
            
            out_page.insert_text(
                fitz.Point(block.x0, trans_y + font_size),
                block.translated_text,
                fontname=font_name,
                fontsize=font_size,
                color=(0.2, 0.2, 0.6),  # 蓝色文字
            )
    
    def _int_to_rgb(self, color_int: int) -> Tuple[float, float, float]:
        """将整数颜色转换为RGB元组 (0-1范围)"""
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)
    
    def render(
        self,
        source_path: str,
        pages_content: List[PageContent],
        output_path: str,
    ) -> None:
        """
        渲染整个PDF
        
        Args:
            source_path: 源PDF路径
            pages_content: 所有页面内容
            output_path: 输出PDF路径
        """
        fitz = self.fitz
        
        source_doc = fitz.open(source_path)
        output_doc = fitz.open()
        
        try:
            for page_no, page_content in enumerate(pages_content):
                if self.bilingual:
                    self.render_page_overlay(
                        source_doc, page_no, page_content, output_doc
                    )
                else:
                    self.render_page(
                        source_doc, page_no, page_content, output_doc
                    )
            
            # 保存输出PDF
            output_doc.save(output_path)
            
        finally:
            source_doc.close()
            output_doc.close()

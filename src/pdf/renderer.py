"""
PDF渲染模块
将翻译后的文本重新渲染到PDF中，保持原有布局
"""

from pathlib import Path
from typing import List, Optional, Tuple
import io

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
    
    def _calculate_font_size(
        self, 
        original_size: float, 
        original_text: str, 
        translated_text: str,
        max_width: float,
    ) -> float:
        """
        计算翻译后文本应该使用的字体大小
        
        考虑翻译后文本长度变化，动态调整字体大小
        """
        # 基础缩放
        size = original_size * self.font_scale
        
        # 根据文本长度比例进一步调整
        len_ratio = len(translated_text) / max(len(original_text), 1)
        
        if len_ratio > 1.5:
            # 翻译后文本明显变长，进一步缩小字体
            size = size / (len_ratio * 0.7)
        
        # 设置字体大小范围
        size = max(min(size, original_size), original_size * 0.5)
        
        return size
    
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
            
            # 创建白色背景遮盖原文本
            shape = out_page.new_shape()
            shape.draw_rect(rect)
            shape.finish(color=None, fill=(1, 1, 1))  # 白色填充
            shape.commit()
            
            # 选择字体
            font_name, _ = self._get_font_for_text(
                block.translated_text, 
                block.font_name
            )
            
            # 计算字体大小
            font_size = self._calculate_font_size(
                block.font_size,
                block.text,
                block.translated_text,
                block.width,
            )
            
            # 转换颜色
            color = self._int_to_rgb(block.font_color)
            
            # 插入翻译后的文本
            # 使用text writer来更好地控制文本渲染
            try:
                # 尝试使用TextWriter获得更好的控制
                tw = fitz.TextWriter(out_page.rect)
                
                # 加载字体
                font = fitz.Font(font_name)
                
                # 计算文本位置
                text_point = fitz.Point(block.x0, block.y1 - 2)
                
                # 写入文本（可能需要分行）
                tw.append(
                    text_point,
                    block.translated_text,
                    font=font,
                    fontsize=font_size,
                )
                
                tw.write_text(out_page, color=color)
                
            except Exception:
                # 回退到简单的insert_text方法
                out_page.insert_text(
                    fitz.Point(block.x0, block.y1 - 2),
                    block.translated_text,
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

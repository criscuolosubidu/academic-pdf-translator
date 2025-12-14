"""
PDF内容提取模块
使用PyMuPDF提取PDF中的文本块及其布局信息
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from pathlib import Path


@dataclass
class TextBlock:
    """
    文本块，包含位置、样式和内容信息
    """
    text: str                           # 文本内容
    bbox: Tuple[float, float, float, float]  # 边界框 (x0, y0, x1, y1)
    font_name: str = ""                 # 字体名称
    font_size: float = 12.0             # 字体大小
    font_color: int = 0                 # 字体颜色 (RGB整数)
    is_bold: bool = False               # 是否粗体
    is_italic: bool = False             # 是否斜体
    block_no: int = 0                   # 块编号
    line_no: int = 0                    # 行编号
    
    # 翻译后的文本
    translated_text: Optional[str] = None
    
    @property
    def x0(self) -> float:
        return self.bbox[0]
    
    @property
    def y0(self) -> float:
        return self.bbox[1]
    
    @property
    def x1(self) -> float:
        return self.bbox[2]
    
    @property
    def y1(self) -> float:
        return self.bbox[3]
    
    @property
    def width(self) -> float:
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        return self.y1 - self.y0


@dataclass
class PageContent:
    """
    页面内容，包含该页的所有文本块
    """
    page_no: int                        # 页码 (从0开始)
    width: float                        # 页面宽度
    height: float                       # 页面高度
    text_blocks: List[TextBlock] = field(default_factory=list)
    
    def get_blocks_in_region(
        self, 
        x0: float, y0: float, 
        x1: float, y1: float
    ) -> List[TextBlock]:
        """获取指定区域内的文本块"""
        return [
            block for block in self.text_blocks
            if (block.x0 >= x0 and block.y0 >= y0 and
                block.x1 <= x1 and block.y1 <= y1)
        ]


class PDFExtractor:
    """
    PDF内容提取器
    使用PyMuPDF提取文本块及其样式信息
    """
    
    def __init__(self, pdf_path: str):
        """
        初始化提取器
        
        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = Path(pdf_path)
        self._doc = None
    
    @property
    def doc(self):
        """延迟加载PDF文档"""
        if self._doc is None:
            try:
                import fitz
                self._doc = fitz.open(self.pdf_path)
            except ImportError:
                raise ImportError("请安装 PyMuPDF: pip install PyMuPDF")
        return self._doc
    
    @property
    def page_count(self) -> int:
        """获取PDF页数"""
        return len(self.doc)
    
    def extract_page(self, page_no: int) -> PageContent:
        """
        提取单页内容
        
        Args:
            page_no: 页码 (从0开始)
        
        Returns:
            PageContent对象
        """
        page = self.doc[page_no]
        
        page_content = PageContent(
            page_no=page_no,
            width=page.rect.width,
            height=page.rect.height,
        )
        
        # 使用dict方法获取详细的文本信息
        blocks = page.get_text("dict", flags=11)["blocks"]
        
        for block_no, block in enumerate(blocks):
            # 只处理文本块，跳过图片块
            if block.get("type") != 0:
                continue
            
            # 遍历块中的行
            for line_no, line in enumerate(block.get("lines", [])):
                # 合并同一行的所有span
                line_text = ""
                line_bbox = list(line["bbox"])
                font_info = None
                
                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                    
                    # 使用第一个span的字体信息
                    if font_info is None:
                        font_info = {
                            "font_name": span.get("font", ""),
                            "font_size": span.get("size", 12.0),
                            "font_color": span.get("color", 0),
                            "flags": span.get("flags", 0),
                        }
                
                if line_text.strip() and font_info:
                    # 解析字体标志
                    flags = font_info["flags"]
                    is_bold = bool(flags & 2 ** 4)  # bit 4
                    is_italic = bool(flags & 2 ** 1)  # bit 1
                    
                    text_block = TextBlock(
                        text=line_text,
                        bbox=tuple(line_bbox),
                        font_name=font_info["font_name"],
                        font_size=font_info["font_size"],
                        font_color=font_info["font_color"],
                        is_bold=is_bold,
                        is_italic=is_italic,
                        block_no=block_no,
                        line_no=line_no,
                    )
                    page_content.text_blocks.append(text_block)
        
        return page_content
    
    def extract_all_pages(self) -> List[PageContent]:
        """
        提取所有页面内容
        
        Returns:
            PageContent列表
        """
        return [self.extract_page(i) for i in range(self.page_count)]
    
    def close(self):
        """关闭PDF文档"""
        if self._doc is not None:
            self._doc.close()
            self._doc = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

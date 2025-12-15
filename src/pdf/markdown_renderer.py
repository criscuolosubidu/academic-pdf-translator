"""
Markdown渲染模块
将翻译后的内容输出为结构良好的Markdown文件
"""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from .extractor import PageContent, TextBlock


class BlockType(Enum):
    """文本块类型"""
    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CAPTION = "caption"
    FOOTER = "footer"
    OTHER = "other"


@dataclass
class StructuredBlock:
    """结构化的文本块"""
    block_type: BlockType
    original_text: str
    translated_text: Optional[str]
    level: int = 0  # 标题级别 (1-6)
    font_size: float = 12.0
    is_bold: bool = False


class MarkdownRenderer:
    """
    Markdown渲染器
    将翻译后的内容输出为格式良好的Markdown
    """
    
    def __init__(
        self,
        bilingual: bool = True,
        include_page_breaks: bool = True,
        preserve_structure: bool = True,
    ):
        """
        初始化渲染器
        
        Args:
            bilingual: 是否生成双语对照
            include_page_breaks: 是否包含分页符
            preserve_structure: 是否保留文档结构（标题层级等）
        """
        self.bilingual = bilingual
        self.include_page_breaks = include_page_breaks
        self.preserve_structure = preserve_structure
    
    def _classify_block(self, block: TextBlock, page_height: float) -> StructuredBlock:
        """
        分类文本块的类型
        
        根据字体大小、位置、样式等判断块类型
        """
        text = block.text.strip()
        font_size = block.font_size
        is_bold = block.is_bold
        
        # 判断是否是页脚（在页面底部）
        if block.y0 > page_height * 0.9:
            return StructuredBlock(
                block_type=BlockType.FOOTER,
                original_text=text,
                translated_text=block.translated_text,
                font_size=font_size,
                is_bold=is_bold,
            )
        
        # 判断是否是标题（字体较大或粗体）
        # 学术论文中标题通常字体较大
        if font_size >= 14 or (is_bold and len(text) < 100):
            # 根据字体大小确定标题级别
            if font_size >= 18:
                level = 1
            elif font_size >= 16:
                level = 2
            elif font_size >= 14:
                level = 3
            elif is_bold:
                level = 4
            else:
                level = 5
            
            block_type = BlockType.TITLE if level == 1 else BlockType.HEADING
            
            return StructuredBlock(
                block_type=block_type,
                original_text=text,
                translated_text=block.translated_text,
                level=level,
                font_size=font_size,
                is_bold=is_bold,
            )
        
        # 判断是否是图表说明（以Figure、Table等开头）
        lower_text = text.lower()
        if lower_text.startswith(('figure', 'fig.', 'fig ', 'table', 'tab.', 'tab ')):
            return StructuredBlock(
                block_type=BlockType.CAPTION,
                original_text=text,
                translated_text=block.translated_text,
                font_size=font_size,
                is_bold=is_bold,
            )
        
        # 默认为段落
        return StructuredBlock(
            block_type=BlockType.PARAGRAPH,
            original_text=text,
            translated_text=block.translated_text,
            font_size=font_size,
            is_bold=is_bold,
        )
    
    def _format_block(self, block: StructuredBlock) -> str:
        """
        将结构化块格式化为Markdown文本
        """
        lines = []
        
        if block.block_type == BlockType.FOOTER:
            # 页脚使用小字体格式，或直接跳过
            return ""
        
        elif block.block_type in (BlockType.TITLE, BlockType.HEADING):
            # 标题
            prefix = "#" * block.level + " "
            
            if self.bilingual and block.translated_text:
                lines.append(f"{prefix}{block.translated_text}")
                lines.append("")
                lines.append(f"> {block.original_text}")
            elif block.translated_text:
                lines.append(f"{prefix}{block.translated_text}")
            else:
                lines.append(f"{prefix}{block.original_text}")
        
        elif block.block_type == BlockType.CAPTION:
            # 图表说明
            if self.bilingual and block.translated_text:
                lines.append(f"**{block.translated_text}**")
                lines.append(f"*{block.original_text}*")
            elif block.translated_text:
                lines.append(f"**{block.translated_text}**")
            else:
                lines.append(f"**{block.original_text}**")
        
        else:
            # 普通段落
            if self.bilingual and block.translated_text:
                lines.append(block.translated_text)
                lines.append("")
                lines.append(f"> {block.original_text}")
            elif block.translated_text:
                lines.append(block.translated_text)
            else:
                lines.append(block.original_text)
        
        lines.append("")  # 段落之间空行
        return "\n".join(lines)
    
    def _merge_paragraph_blocks(
        self,
        blocks: List[StructuredBlock],
    ) -> List[StructuredBlock]:
        """
        合并连续的段落块
        """
        if not blocks:
            return []
        
        merged = []
        current = None
        
        for block in blocks:
            if block.block_type == BlockType.PARAGRAPH:
                if current is None:
                    current = StructuredBlock(
                        block_type=BlockType.PARAGRAPH,
                        original_text=block.original_text,
                        translated_text=block.translated_text or "",
                        font_size=block.font_size,
                        is_bold=block.is_bold,
                    )
                else:
                    # 合并到当前段落
                    current.original_text += " " + block.original_text
                    if block.translated_text:
                        current.translated_text += block.translated_text
            else:
                # 非段落块，先保存当前段落
                if current is not None:
                    merged.append(current)
                    current = None
                merged.append(block)
        
        if current is not None:
            merged.append(current)
        
        return merged
    
    def render_page(self, page_content: PageContent) -> str:
        """
        渲染单页为Markdown
        
        Args:
            page_content: 页面内容
        
        Returns:
            Markdown格式的文本
        """
        # 分类所有文本块
        structured_blocks = [
            self._classify_block(block, page_content.height)
            for block in page_content.text_blocks
        ]
        
        # 合并段落
        if self.preserve_structure:
            structured_blocks = self._merge_paragraph_blocks(structured_blocks)
        
        # 格式化输出
        lines = []
        for block in structured_blocks:
            formatted = self._format_block(block)
            if formatted:
                lines.append(formatted)
        
        return "\n".join(lines)
    
    def render(
        self,
        pages_content: List[PageContent],
        output_path: str,
        title: Optional[str] = None,
    ) -> None:
        """
        渲染整个文档为Markdown
        
        Args:
            pages_content: 所有页面内容
            output_path: 输出文件路径
            title: 可选的文档标题
        """
        output_path = Path(output_path)
        
        lines = []
        
        # 添加文档标题
        if title:
            lines.append(f"# {title}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # 渲染每一页
        for i, page_content in enumerate(pages_content):
            page_md = self.render_page(page_content)
            
            if page_md.strip():
                lines.append(page_md)
                
                if self.include_page_breaks and i < len(pages_content) - 1:
                    lines.append("")
                    lines.append(f"---")
                    lines.append(f"*第 {i + 2} 页*")
                    lines.append("")
        
        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

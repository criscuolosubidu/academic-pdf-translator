"""
MinerU PDF解析模块
使用MinerU将PDF转换为Markdown
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from loguru import logger


@dataclass
class ParsedDocument:
    """解析后的文档"""
    markdown_content: str  # Markdown内容
    images_dir: Optional[str]  # 图片目录路径
    content_list: Optional[List[dict]]  # 内容列表
    

class MineruParser:
    """
    MinerU PDF解析器
    将PDF转换为Markdown格式
    """
    
    def __init__(
        self,
        backend: str = "pipeline",
        lang: str = "ch",
        method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
    ):
        """
        初始化MinerU解析器
        
        Args:
            backend: 后端类型 ("pipeline", "vlm-transformers", "vlm-vllm-engine", "vlm-http-client")
            lang: 语言设置 ('ch', 'en', 'korean', 'japan', etc.)
            method: 解析方法 ('auto', 'txt', 'ocr')
            formula_enable: 是否启用公式解析
            table_enable: 是否启用表格解析
        """
        self.backend = backend
        self.lang = lang
        self.method = method
        self.formula_enable = formula_enable
        self.table_enable = table_enable
        
        # 延迟导入检查
        self._mineru_available = None
    
    def _check_mineru(self) -> bool:
        """检查MinerU是否可用"""
        if self._mineru_available is None:
            try:
                from mineru.cli.common import read_fn
                self._mineru_available = True
            except ImportError:
                self._mineru_available = False
                logger.warning("MinerU未安装，请运行: pip install mineru")
        return self._mineru_available
    
    def parse_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        start_page: int = 0,
        end_page: Optional[int] = None,
    ) -> ParsedDocument:
        """
        解析PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，默认使用临时目录
            start_page: 起始页码 (0-based)
            end_page: 结束页码 (0-based)，None表示到最后
        
        Returns:
            ParsedDocument: 解析后的文档对象
        """
        if not self._check_mineru():
            raise ImportError("MinerU未安装，请运行: pip install mineru")
        
        from mineru.cli.common import (
            convert_pdf_bytes_to_bytes_by_pypdfium2,
            prepare_env,
            read_fn,
        )
        from mineru.data.data_reader_writer import FileBasedDataWriter
        from mineru.utils.enum_class import MakeMode
        from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
        from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
        from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
        from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
        from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make
        
        pdf_path = Path(pdf_path)
        pdf_file_name = pdf_path.stem
        
        # 读取PDF字节
        pdf_bytes = read_fn(str(pdf_path))
        
        # 确定输出目录
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="mineru_")
            cleanup_temp = True
        else:
            output_dir = str(output_dir)
            cleanup_temp = False
        
        try:
            if self.backend == "pipeline":
                # 处理页码范围
                pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(
                    pdf_bytes, start_page, end_page
                )
                
                # 进行文档分析
                infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = \
                    pipeline_doc_analyze(
                        [pdf_bytes],
                        [self.lang],
                        parse_method=self.method,
                        formula_enable=self.formula_enable,
                        table_enable=self.table_enable,
                    )
                
                # 准备输出环境
                local_image_dir, local_md_dir = prepare_env(output_dir, pdf_file_name, self.method)
                image_writer = FileBasedDataWriter(local_image_dir)
                
                # 转换结果
                middle_json = pipeline_result_to_middle_json(
                    infer_results[0],
                    all_image_lists[0],
                    all_pdf_docs[0],
                    image_writer,
                    lang_list[0],
                    ocr_enabled_list[0],
                    self.formula_enable,
                )
                
                pdf_info = middle_json["pdf_info"]
                image_dir = os.path.basename(local_image_dir)
                
                # 生成Markdown内容
                md_content = pipeline_union_make(pdf_info, MakeMode.MM_MD, image_dir)
                
                # 生成内容列表
                content_list = pipeline_union_make(pdf_info, MakeMode.CONTENT_LIST, image_dir)
                
            else:
                # VLM后端
                backend_name = self.backend[4:] if self.backend.startswith("vlm-") else self.backend
                
                # 处理页码范围
                pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(
                    pdf_bytes, start_page, end_page
                )
                
                local_image_dir, local_md_dir = prepare_env(output_dir, pdf_file_name, "vlm")
                image_writer = FileBasedDataWriter(local_image_dir)
                
                middle_json, _ = vlm_doc_analyze(
                    pdf_bytes,
                    image_writer=image_writer,
                    backend=backend_name,
                )
                
                pdf_info = middle_json["pdf_info"]
                image_dir = os.path.basename(local_image_dir)
                
                # 生成Markdown内容
                md_content = vlm_union_make(pdf_info, MakeMode.MM_MD, image_dir)
                
                # 生成内容列表
                content_list = vlm_union_make(pdf_info, MakeMode.CONTENT_LIST, image_dir)
            
            return ParsedDocument(
                markdown_content=md_content,
                images_dir=local_image_dir,
                content_list=content_list,
            )
            
        except Exception as e:
            logger.exception(f"解析PDF失败: {e}")
            if cleanup_temp and os.path.exists(output_dir):
                shutil.rmtree(output_dir, ignore_errors=True)
            raise
    
    def parse_pdf_to_file(
        self,
        pdf_path: str,
        output_dir: str,
        start_page: int = 0,
        end_page: Optional[int] = None,
        dump_images: bool = True,
        dump_content_list: bool = False,
    ) -> str:
        """
        解析PDF并保存到文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            start_page: 起始页码
            end_page: 结束页码
            dump_images: 是否保存图片
            dump_content_list: 是否保存内容列表JSON
        
        Returns:
            生成的Markdown文件路径
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 解析PDF
        result = self.parse_pdf(
            str(pdf_path),
            str(output_dir),
            start_page,
            end_page,
        )
        
        # 确定输出文件名
        md_filename = f"{pdf_path.stem}.md"
        md_path = output_dir / pdf_path.stem / "auto" / md_filename
        
        # 写入Markdown
        md_path.parent.mkdir(parents=True, exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.markdown_content)
        
        # 保存内容列表
        if dump_content_list and result.content_list:
            content_list_path = md_path.with_suffix(".content_list.json")
            with open(content_list_path, "w", encoding="utf-8") as f:
                json.dump(result.content_list, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Markdown已保存到: {md_path}")
        
        return str(md_path)


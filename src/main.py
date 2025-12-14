"""
学术论文翻译器主程序
提供命令行接口和编程接口
"""

import click
from pathlib import Path
from typing import Optional, List

from .config import load_config, Config
from .translators import get_translator
from .pdf import PDFProcessor


def create_processor(
    config: Config,
    translator_name: Optional[str] = None,
) -> PDFProcessor:
    """
    根据配置创建PDF处理器
    
    Args:
        config: 配置对象
        translator_name: 翻译器名称，默认使用配置中的默认翻译器
    
    Returns:
        PDFProcessor实例
    """
    translator_name = translator_name or config.default_translator
    
    # 根据翻译器类型获取配置
    if translator_name == "google":
        translator = get_translator(
            "google",
            source_lang=config.source_lang,
            target_lang=config.target_lang,
            project_id=config.google.project_id,
        )
    elif translator_name == "openai":
        translator = get_translator(
            "openai",
            source_lang=config.source_lang,
            target_lang=config.target_lang,
            api_key=config.openai.api_key,
            model=config.openai.model,
            base_url=config.openai.base_url,
            system_prompt=config.openai.system_prompt or None,
        )
    elif translator_name == "local_llm":
        translator = get_translator(
            "local_llm",
            source_lang=config.source_lang,
            target_lang=config.target_lang,
            base_url=config.local_llm.base_url,
            model=config.local_llm.model,
            api_key=config.local_llm.api_key,
            system_prompt=config.local_llm.system_prompt or None,
        )
    else:
        raise ValueError(f"未知的翻译器: {translator_name}")
    
    return PDFProcessor(
        translator=translator,
        font_scale=config.pdf.font_scale,
        bilingual=config.pdf.bilingual,
        fallback_font=config.pdf.fallback_font,
    )


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """学术论文翻译器 - 支持多种翻译API，保留PDF排版格式"""
    pass


@cli.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="输出文件路径")
@click.option("-c", "--config", "config_path", type=click.Path(exists=True), help="配置文件路径")
@click.option("-t", "--translator", type=click.Choice(["google", "openai", "local_llm"]), help="翻译器")
@click.option("--source-lang", default="en", help="源语言 (默认: en)")
@click.option("--target-lang", default="zh", help="目标语言 (默认: zh)")
@click.option("--pages", help="要翻译的页码，如 '1,2,3' 或 '1-5'")
@click.option("--bilingual", is_flag=True, help="生成双语对照版本")
def translate(
    input_pdf: str,
    output: Optional[str],
    config_path: Optional[str],
    translator: Optional[str],
    source_lang: str,
    target_lang: str,
    pages: Optional[str],
    bilingual: bool,
):
    """翻译PDF学术论文"""
    # 加载配置
    config = load_config(config_path)
    
    # 命令行参数覆盖配置
    if source_lang:
        config.source_lang = source_lang
    if target_lang:
        config.target_lang = target_lang
    if bilingual:
        config.pdf.bilingual = bilingual
    
    # 解析页码
    page_list = None
    if pages:
        page_list = parse_page_range(pages)
    
    # 创建处理器
    processor = create_processor(config, translator)
    
    click.echo(f"正在翻译: {input_pdf}")
    click.echo(f"翻译器: {translator or config.default_translator}")
    click.echo(f"语言: {config.source_lang} -> {config.target_lang}")
    
    # 执行翻译
    output_path = processor.process(
        input_path=input_pdf,
        output_path=output,
        pages=page_list,
    )
    
    click.echo(f"翻译完成: {output_path}")


@cli.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="输出文件路径")
def extract(input_pdf: str, output: Optional[str]):
    """提取PDF文本内容（用于调试）"""
    from .pdf import PDFExtractor
    import json
    
    with PDFExtractor(input_pdf) as extractor:
        pages = extractor.extract_all_pages()
        
        result = []
        for page in pages:
            page_data = {
                "page_no": page.page_no,
                "width": page.width,
                "height": page.height,
                "blocks": [
                    {
                        "text": b.text,
                        "bbox": b.bbox,
                        "font_size": b.font_size,
                    }
                    for b in page.text_blocks
                ]
            }
            result.append(page_data)
    
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        click.echo(f"已保存到: {output}")
    else:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))


@cli.command()
@click.option("-t", "--translator", type=click.Choice(["google", "openai", "local_llm"]), default="openai")
@click.option("-c", "--config", "config_path", type=click.Path(exists=True), help="配置文件路径")
def test_connection(translator: str, config_path: Optional[str]):
    """测试翻译API连接"""
    config = load_config(config_path)
    
    click.echo(f"测试 {translator} 连接...")
    
    try:
        if translator == "local_llm":
            from .translators import LocalLLMTranslator
            t = LocalLLMTranslator(
                base_url=config.local_llm.base_url,
                model=config.local_llm.model,
            )
            if t.check_connection():
                click.echo("✓ 连接成功!")
            else:
                click.echo("✗ 连接失败")
        else:
            # 简单测试翻译
            processor = create_processor(config, translator)
            result = processor.translator.translate("Hello, world!")
            click.echo(f"✓ 连接成功!")
            click.echo(f"测试翻译: 'Hello, world!' -> '{result.translated}'")
            
    except Exception as e:
        click.echo(f"✗ 连接失败: {e}")


def parse_page_range(pages_str: str) -> List[int]:
    """
    解析页码范围字符串
    
    支持格式:
    - "1,2,3" -> [0, 1, 2]
    - "1-5" -> [0, 1, 2, 3, 4]
    - "1,3-5,7" -> [0, 2, 3, 4, 6]
    
    注意：输入是1-based，输出是0-based
    """
    pages = []
    
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            pages.extend(range(int(start) - 1, int(end)))
        else:
            pages.append(int(part) - 1)
    
    return sorted(set(pages))


# 编程接口
def translate_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    translator: str = "openai",
    source_lang: str = "en",
    target_lang: str = "zh",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    pages: Optional[List[int]] = None,
    bilingual: bool = False,
) -> str:
    """
    翻译PDF的简单接口
    
    Args:
        input_path: 输入PDF路径
        output_path: 输出PDF路径
        translator: 翻译器名称
        source_lang: 源语言
        target_lang: 目标语言
        api_key: API密钥
        model: 模型名称
        base_url: API基础URL
        pages: 要翻译的页码列表（0-based）
        bilingual: 是否生成双语版本
    
    Returns:
        输出文件路径
    
    Example:
        >>> from src.main import translate_pdf
        >>> output = translate_pdf(
        ...     "paper.pdf",
        ...     translator="openai",
        ...     api_key="sk-xxx",
        ... )
    """
    # 构建配置
    config = load_config()
    config.source_lang = source_lang
    config.target_lang = target_lang
    config.pdf.bilingual = bilingual
    
    if api_key:
        if translator == "openai":
            config.openai.api_key = api_key
        elif translator == "local_llm":
            config.local_llm.api_key = api_key
    
    if model:
        if translator == "openai":
            config.openai.model = model
        elif translator == "local_llm":
            config.local_llm.model = model
    
    if base_url:
        if translator == "openai":
            config.openai.base_url = base_url
        elif translator == "local_llm":
            config.local_llm.base_url = base_url
    
    processor = create_processor(config, translator)
    
    return processor.process(
        input_path=input_path,
        output_path=output_path,
        pages=pages,
    )


if __name__ == "__main__":
    cli()

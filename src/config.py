"""
配置管理模块
支持从YAML文件和环境变量加载配置
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class GoogleConfig:
    """Google Translate配置"""
    project_id: str = ""


@dataclass
class OpenAIConfig:
    """OpenAI API配置"""
    api_key: str = ""
    model: str = "gpt-4o"
    base_url: str = "https://api.openai.com/v1"
    system_prompt: str = ""


@dataclass
class LocalLLMConfig:
    """本地LLM配置"""
    base_url: str = "http://localhost:8000/v1"
    model: str = "qwen2.5-72b-instruct"
    api_key: str = "not-needed"
    system_prompt: str = ""


@dataclass
class PDFConfig:
    """PDF处理配置"""
    bilingual: bool = False
    font_scale: float = 0.9
    fallback_font: Optional[str] = None


@dataclass
class Config:
    """主配置类"""
    default_translator: str = "openai"
    source_lang: str = "en"
    target_lang: str = "zh"
    google: GoogleConfig = field(default_factory=GoogleConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    local_llm: LocalLLMConfig = field(default_factory=LocalLLMConfig)
    pdf: PDFConfig = field(default_factory=PDFConfig)


def _expand_env_vars(value: str) -> str:
    """展开环境变量 ${VAR_NAME} 格式"""
    if not isinstance(value, str):
        return value
    pattern = re.compile(r'\$\{([^}]+)\}')
    
    def replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, "")
    
    return pattern.sub(replacer, value)


def _expand_dict(d: dict) -> dict:
    """递归展开字典中的环境变量"""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _expand_dict(v)
        elif isinstance(v, str):
            result[k] = _expand_env_vars(v)
        else:
            result[k] = v
    return result


def load_config(config_path: Optional[str] = None) -> Config:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，默认查找 config.yaml
    
    Returns:
        Config对象
    """
    # 默认配置文件路径
    if config_path is None:
        for name in ["config.yaml", "config.yml"]:
            if Path(name).exists():
                config_path = name
                break
    
    config = Config()
    
    if config_path and Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f) or {}
        
        # 展开环境变量
        raw_config = _expand_dict(raw_config)
        
        # 填充配置
        config.default_translator = raw_config.get("default_translator", config.default_translator)
        config.source_lang = raw_config.get("source_lang", config.source_lang)
        config.target_lang = raw_config.get("target_lang", config.target_lang)
        
        if "google" in raw_config:
            config.google = GoogleConfig(**raw_config["google"])
        
        if "openai" in raw_config:
            config.openai = OpenAIConfig(**raw_config["openai"])
        
        if "local_llm" in raw_config:
            config.local_llm = LocalLLMConfig(**raw_config["local_llm"])
        
        if "pdf" in raw_config:
            config.pdf = PDFConfig(**raw_config["pdf"])
    
    # 从环境变量覆盖关键配置
    if os.environ.get("OPENAI_API_KEY"):
        config.openai.api_key = os.environ["OPENAI_API_KEY"]
    
    if os.environ.get("OPENAI_BASE_URL"):
        config.openai.base_url = os.environ["OPENAI_BASE_URL"]
    
    return config

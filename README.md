# 📚 Academic Paper Translator

学术论文翻译器 - 支持多种翻译API，**保留PDF排版格式**

专为医学和计算机科学领域的学术论文设计，提供高质量的翻译体验。

## ✨ 特性

- 🔄 **多翻译后端支持**
  - Google Translate API
  - OpenAI API (GPT-4o等)
  - 本地LLM (vLLM, Ollama等OpenAI兼容接口)

- 📄 **保留PDF格式**
  - 提取原始文本位置和样式
  - 在原位置渲染翻译文本
  - 支持双语对照模式

- 🎯 **学术翻译优化**
  - 专业术语保留英文原文
  - 医学/计算机领域优化
  - 保持学术语体

- 🛠️ **简洁可扩展架构**
  - 模块化设计
  - 易于添加新翻译器
  - 配置灵活

## 📦 安装

```bash
# 克隆仓库
git clone <repository-url>
cd academic-paper-translator

# 安装依赖
pip install -r requirements.txt
```

## 🚀 快速开始

### 命令行使用

```bash
# 使用OpenAI翻译
export OPENAI_API_KEY="your-api-key"
python translate.py translate paper.pdf

# 指定输出文件
python translate.py translate paper.pdf -o paper_zh.pdf

# 使用本地LLM
python translate.py translate paper.pdf -t local_llm

# 生成双语对照版本
python translate.py translate paper.pdf --bilingual

# 只翻译指定页面
python translate.py translate paper.pdf --pages "1-5,10"
```

### Python API使用

```python
from src.main import translate_pdf

# 简单使用
output = translate_pdf(
    "paper.pdf",
    translator="openai",
    api_key="sk-xxx",
)

# 完整参数
output = translate_pdf(
    input_path="paper.pdf",
    output_path="paper_translated.pdf",
    translator="openai",  # google, openai, local_llm
    source_lang="en",
    target_lang="zh",
    api_key="sk-xxx",
    model="gpt-4o",
    pages=[0, 1, 2],  # 0-based页码
    bilingual=False,
)
```

### 使用本地LLM (vLLM)

```python
from src.main import translate_pdf

# 使用vLLM部署的本地模型
output = translate_pdf(
    "paper.pdf",
    translator="local_llm",
    base_url="http://localhost:8000/v1",
    model="qwen2.5-72b-instruct",
)
```

## ⚙️ 配置

复制配置模板并编辑：

```bash
cp config.yaml.example config.yaml
```

配置文件示例：

```yaml
# 默认翻译器
default_translator: openai

# 语言设置
source_lang: en
target_lang: zh

# OpenAI配置
openai:
  api_key: ${OPENAI_API_KEY}  # 从环境变量读取
  model: gpt-4o
  base_url: https://api.openai.com/v1
  system_prompt: |
    你是一位专业的学术论文翻译专家...

# 本地LLM配置
local_llm:
  base_url: http://localhost:8000/v1
  model: qwen2.5-72b-instruct

# PDF处理配置
pdf:
  bilingual: false      # 双语对照
  font_scale: 0.9       # 字体缩放
```

## 🏗️ 项目结构

```
.
├── translate.py          # 命令行入口
├── config.yaml.example   # 配置模板
├── requirements.txt      # 依赖
└── src/
    ├── __init__.py
    ├── main.py           # 主程序和CLI
    ├── config.py         # 配置管理
    ├── translators/      # 翻译器模块
    │   ├── base.py       # 翻译器基类
    │   ├── google.py     # Google翻译
    │   ├── openai.py     # OpenAI翻译
    │   └── local_llm.py  # 本地LLM翻译
    ├── pdf/              # PDF处理模块
    │   ├── extractor.py  # 内容提取
    │   ├── renderer.py   # 重新渲染
    │   └── processor.py  # 处理流程
    └── utils/            # 工具函数
        └── text.py       # 文本处理
```

## 🔧 扩展

### 添加新的翻译器

1. 在 `src/translators/` 下创建新文件
2. 继承 `BaseTranslator` 类
3. 实现 `translate()` 方法
4. 在 `__init__.py` 中注册

```python
from .base import BaseTranslator, TranslationResult

class MyTranslator(BaseTranslator):
    def translate(self, text: str) -> TranslationResult:
        # 实现翻译逻辑
        translated = my_translation_api(text)
        return TranslationResult(
            original=text,
            translated=translated,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
        )
```

### 自定义PDF渲染

可以继承或修改 `PDFRenderer` 类来自定义渲染行为：

```python
from src.pdf import PDFRenderer

class CustomRenderer(PDFRenderer):
    def render_page(self, ...):
        # 自定义渲染逻辑
        pass
```

## 📋 命令参考

```bash
# 查看帮助
python translate.py --help
python translate.py translate --help

# 翻译PDF
python translate.py translate <input.pdf> [OPTIONS]

# 提取PDF文本（调试用）
python translate.py extract <input.pdf> -o output.json

# 测试API连接
python translate.py test-connection -t openai
python translate.py test-connection -t local_llm
```

## ⚠️ 注意事项

1. **PDF格式保留限制**
   - 复杂布局（多栏、表格）可能需要手动调整
   - 公式和图片会保留，但其中的文字不会翻译
   - 字体渲染取决于系统可用字体

2. **翻译质量**
   - OpenAI/大模型通常提供更好的学术翻译质量
   - Google Translate速度快，适合草稿翻译
   - 专业术语建议检查

3. **API费用**
   - 请注意各翻译服务的计费方式
   - 建议先用少量页面测试

## 📄 许可证

MIT License

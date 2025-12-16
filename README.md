# Academic PDF Translator

学术论文 PDF 翻译工具，基于 [MinerU](https://github.com/opendatalab/MinerU) 解析 PDF，支持公式、表格、图片识别，输出高质量 Markdown。

## 特性

- 🔬 **MinerU 解析引擎**：智能识别论文结构、公式、表格和图片
- 🌐 **多翻译器支持**：OpenAI、Google Cloud、本地 LLM
- 📝 **双语对照**：可选生成中英对照版本
- 📐 **公式保留**：LaTeX 公式原样保留不翻译
- 📊 **表格保持**：保持表格结构完整

## 安装

```bash
# 安装 uv（如未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/your-username/academic-pdf-translator.git
cd academic-pdf-translator

# 安装依赖
uv sync
```

### MinerU 依赖

MinerU 需要额外安装模型，首次运行时会自动下载。如果网络问题，可设置：

```bash
export MINERU_MODEL_SOURCE=modelscope
```

## 配置

复制并编辑配置文件：

```bash
cp config.yaml.example config.yaml
```

设置 API Key（任选一种）：

```yaml
# config.yaml
default_translator: openai

openai:
  api_key: sk-xxx
  base_url: https://api.openai.com/v1  # 或其他兼容接口
  model: gpt-4o

# 或使用本地 LLM
local_llm:
  base_url: http://localhost:11434/v1
  model: qwen2.5:14b
```

## 使用

### 命令行

```bash
# 基本翻译（输出 Markdown）
uv run translate paper.pdf

# 指定输出路径
uv run translate paper.pdf -o ./output

# 双语对照模式
uv run translate paper.pdf --bilingual

# 翻译指定页码
uv run translate paper.pdf --pages 1-10

# 使用不同翻译器
uv run translate paper.pdf -t local_llm
```

### Python API

```python
from src.main import translate_pdf

# 基本用法
output = translate_pdf(
    "paper.pdf",
    translator="openai",
    api_key="sk-xxx",
)

# 双语对照
output = translate_pdf(
    "paper.pdf",
    translator="openai",
    api_key="sk-xxx",
    bilingual=True,
)
```

## 输出结构

```
output/
└── paper/
    └── auto/
        ├── paper_translated.md    # 翻译后的 Markdown
        └── images/                # 提取的图片
            ├── 1.png
            └── ...
```

## 常见问题

### 路径包含中文

如果项目路径包含中文，使用：

```bash
uv run --no-editable translate paper.pdf
# 或
uv run python -m src.main translate paper.pdf
```

### MinerU 模型下载慢

设置国内镜像源：

```bash
export MINERU_MODEL_SOURCE=modelscope
```

## 许可证

MIT

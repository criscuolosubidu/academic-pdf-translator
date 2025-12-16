# Academic PDF Translator

学术论文 PDF 翻译工具，保留原文排版。

## 安装

```bash
# 安装 uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 安装依赖
uv sync
```

## 配置

复制并编辑配置文件：

```bash
cp config.yaml.example config.yaml
```

设置 API Key（任选一种）：

```yaml
# config.yaml
openai:
  api_key: sk-xxx
  base_url: https://api.openai.com/v1  # 或其他兼容接口
  model: gpt-4o
```

## 使用

```bash
# 翻译 PDF（输出到 output/ 目录）
uv run --no-editable translate translate paper.pdf

# 指定输出文件
uv run --no-editable translate translate paper.pdf -o translated.pdf

# 输出 Markdown 格式
uv run --no-editable translate translate paper.pdf -f markdown

# 双语对照
uv run --no-editable translate translate paper.pdf --bilingual
```

> **注意**：如果项目路径包含中文，必须加 `--no-editable` 参数，或使用：
> ```bash
> uv run python -m src.main translate paper.pdf
> ```

## 许可证

MIT

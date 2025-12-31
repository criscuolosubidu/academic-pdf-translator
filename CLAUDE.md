# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Academic PDF Translator - A Python tool that parses academic papers using MinerU, preserves structure (formulas, tables, images), and translates content using LLM backends (OpenAI, Google Cloud, local LLMs). Outputs bilingual Markdown with LaTeX formula preservation.

## Development Commands

```bash
# Install dependencies (uses uv)
uv sync

# Install with optional groups
uv sync --extra vlm          # VLM backend support
uv sync --extra local-llm    # Local LLM support
uv sync --extra dev          # Dev dependencies (pytest, ruff, mypy)

# Run the translator CLI
uv run translate <paper.pdf>

# Common CLI options
uv run translate paper.pdf -o ./output          # Output path
uv run translate paper.pdf --bilingual          # Bilingual mode
uv run translate paper.pdf --pages 1-10         # Page range
uv run translate paper.pdf -t openai            # Translator backend

# Linting and type checking
uv run ruff check src/                           # Linter
uv run ruff check --fix src/                     # Auto-fix issues
uv run mypy src/                                 # Type checker

# Testing
uv run pytest
uv run pytest --cov=src                         # With coverage
```

## Architecture

```
src/
├── main.py              # CLI entry point, translate_pdf() API
├── config.py            # YAML config + env var loading
├── pdf/
│   ├── mineru_parser.py # MinerU PDF → Markdown conversion
│   └── processor.py     # PDFProcessor: splits content, identifies
│                        # translatable vs preserved elements
└── translators/
    ├── base.py          # BaseTranslator ABC
    ├── openai.py        # OpenAI-compatible API (DeepSeek, etc.)
    ├── google.py        # Google Cloud Translate
    ├── local_llm.py     # Local vLLM/Ollama (OpenAI-compatible)
    └── prompts.py       # Academic translation prompts
```

**Translation Flow:**
1. CLI/API receives PDF path and options
2. MinerU parses PDF → structured Markdown (preserves formulas, tables, images)
3. PDFProcessor splits into translatable paragraphs vs. preserved blocks
4. Translator backend processes content in batches
5. Reassembly preserves non-translatable elements (LaTeX, code, tables)

**Preserved Elements (not translated):**
- LaTeX formulas: `$`, `$$`
- Code blocks: ` ``` `
- Tables: `|`
- Images: `![]()`

## Configuration

Configure via `config.yaml` or environment variables:
- `OPENAI_API_KEY` / `OPENAI_BASE_URL` - Override OpenAI settings
- `MINERU_MODEL_SOURCE=modelscope` - Faster Chinese model downloads

## Key Dependencies

- **MinerU** - PDF structure recognition (formulas, tables, images)
- **loguru** - Logging
- **click** - CLI framework
- **pyyaml** - Config parsing

## Output Format

```
output/<paper_name>/auto/
├── <paper>_translated.md  # Translated Markdown
└── images/               # Extracted figures
```

---
name: opendataloader-pdf
description: "PDF 解析工具，支援 PDF 轉 Markdown/JSON/HTML。#1 benchmark 精準度 (0.907)。支援批量處理、表格提取、OCR、hybrid AI 模式、公式提取、圖表描述、AI 安全過濾。當使用者需要「解析 PDF」「提取 PDF 文字」「PDF 轉 Markdown」「PDF 轉 JSON」「處理掃描 PDF」「提取 PDF 表格」「PDF OCR」「批量處理 PDF」時觸發。"
version: 2.4.3
license: Apache-2.0
source: https://github.com/opendataloader-project/opendataloader-pdf
tags:
  - pdf
  - ocr
  - data-extraction
  - markdown
  - json
  - rag
  - mcp
  - table-extraction
  - hybrid-ai
  - bounding-boxes
---

# OpenDataLoader PDF — PDF Parser for AI-ready Data

## Overview

OpenDataLoader PDF is the #1 ranked open-source PDF parser (0.907 overall accuracy). It extracts Markdown, JSON (with bounding boxes), and HTML from any PDF. Deterministic local mode runs at 0.015s/page on CPU — no GPU required.

**Key Capabilities:**
- Correct reading order (XY-Cut++) for multi-column layouts
- Bounding boxes for every element (heading, paragraph, table, image)
- Table extraction (simple and complex/borderless)
- AI safety filters (hidden text, prompt injection protection)
- Hybrid mode: AI backend for complex pages, OCR, formulas, chart descriptions
- Tagged PDF structure extraction
- Python, Node.js, Java SDKs

## Prerequisites

- **Java 11+** (JDK 17 recommended, installed at `C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot`)
- **Python 3.10+**

Ensure `JAVA_HOME` points to JDK 17:
```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
```

## Installed Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `opendataloader-pdf` | 2.4.3 | Core PDF parser (Python wrapper around Java engine) |
| `opendataloader-pdf[hybrid]` | 2.4.3 | Hybrid mode with docling OCR, AI tables, formulas |
| `opendataloader-pdf-mcp` | 0.2.0 | MCP Server for AI agent integration |

---

## Usage Methods

### Method 1: Python SDK

```python
import opendataloader_pdf

opendataloader_pdf.convert(
    input_path=["file1.pdf", "file2.pdf", "folder/"],
    output_dir="output/",
    format="markdown,json"
)
```

**Available formats:** `json`, `markdown`, `html`, `text`, `markdown-with-html`, `markdown-with-images`

**Advanced options:**
```python
opendataloader_pdf.convert(
    input_path=["file.pdf"],
    output_dir="output/",
    format="json,markdown",
    use_struct_tree=True,
    sanitize=True,
    pages="1,3,5-7",
    image_output="embedded",
    image_format="jpeg",
    keep_line_breaks=True,
    hybrid="docling-fast",
)
```

### Method 2: CLI

```bash
opendataloader-pdf file1.pdf file2.pdf folder/ --format markdown,json --output-dir output/
opendataloader-pdf file.pdf --sanitize
opendataloader-pdf file.pdf --pages 1,3,5-7
opendataloader-pdf file.pdf --use-struct-tree
```

### Method 3: Hybrid Mode (OCR + AI Tables + Formulas + Charts)

**Terminal 1 — Start backend:**
```bash
opendataloader-pdf-hybrid --port 5002
```

**Terminal 2 — Process:**
```bash
opendataloader-pdf --hybrid docling-fast file.pdf
opendataloader-pdf --hybrid docling-fast --hybrid-mode full file.pdf  # for formulas/charts
```

**Backend options:**
```bash
opendataloader-pdf-hybrid --port 5002 --force-ocr              # OCR for scanned PDFs
opendataloader-pdf-hybrid --port 5002 --force-ocr --ocr-lang "ch_tra,en"  # Chinese + English OCR
opendataloader-pdf-hybrid --port 5002 --enrich-formula          # LaTeX formula extraction
opendataloader-pdf-hybrid --port 5002 --enrich-picture-description  # AI chart/image description
```

### Method 4: MCP Server (AI Agent Integration)

Already registered to Claude Code via:
```bash
claude mcp add opendataloader-pdf -- uvx opendataloader-pdf-mcp
```

MCP tool `convert_pdf` accepts: `input_path`, `format`, `pages`, `password`, `sanitize`, `use_struct_tree`, `hybrid`, `hybrid_mode`, and all other options.

---

## JSON Output Structure

```json
{
  "type": "heading|paragraph|table|list|image|caption|formula",
  "id": 42,
  "page number": 1,
  "bounding box": [72.0, 700.0, 540.0, 730.0],
  "heading level": 1,
  "content": "Extracted text..."
}
```

- `bounding box`: `[left, bottom, right, top]` in PDF points (72pt = 1 inch)
- Every element includes coordinates — ideal for RAG source citation

---

## Key Options Reference

| Option | CLI Flag | Python Kwarg | Description |
|--------|----------|-------------|-------------|
| Format | `--format` | `format` | `json`, `markdown`, `html`, `text` |
| Pages | `--pages` | `pages` | e.g. `"1,3,5-7"` |
| Sanitize | `--sanitize` | `sanitize=True` | Mask emails, URLs, phones, credit cards |
| Struct tree | `--use-struct-tree` | `use_struct_tree=True` | Use native PDF tags |
| Image output | `--image-output` | `image_output` | `off`, `embedded`, `external` |
| Hybrid | `--hybrid` | `hybrid` | `docling-fast` for AI backend |
| Hybrid mode | `--hybrid-mode` | `hybrid_mode` | `auto` or `full` |
| AI safety off | `--content-safety-off` | `content_safety_off` | Disable safety filters |
| Table method | `--table-method` | `table_method` | `default` or `cluster` |
| Reading order | `--reading-order` | `reading_order` | `off` or `xycut` |

---

## When to Use vs Other Skills

| Scenario | Use This Skill | Not |
|----------|---------------|-----|
| Parse PDF to Markdown/JSON for RAG | **opendataloader-pdf** | markitdown (less accurate for PDF) |
| Extract tables with bounding boxes | **opendataloader-pdf** | pdf-ocr (no table support) |
| OCR scanned Chinese/Asian PDFs | **opendataloader-pdf** (hybrid) | pdf-ocr (simpler OCR) |
| Convert DOCX/PPTX/XLSX to Markdown | markitdown | opendataloader-pdf (PDF only) |
| Simple OCR on images (non-PDF) | pdf-ocr | opendataloader-pdf (PDF only) |
| Need source citation coordinates | **opendataloader-pdf** | All others |
| Batch 100+ PDFs quickly | **opendataloader-pdf** (local mode) | |

---

## Performance Characteristics

| Mode | Speed | Accuracy | Use Case |
|------|-------|----------|----------|
| Local (default) | 0.015s/page (60+ pages/s) | 0.831 overall | Standard digital PDFs |
| Hybrid | 0.463s/page | 0.907 overall (#1) | Complex tables, scanned, formulas |
| Hybrid + OCR | ~0.5s/page | High | Scanned/image-based PDFs |

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `java` not found or wrong version | Set `JAVA_HOME` to JDK 17 path, prepend to `PATH` |
| First run is slow | Downloads shaded JAR (~22MB) on first use |
| `FileNotFoundError` for JAR | Reinstall: `pip install -U opendataloader-pdf` |
| Hybrid mode silently skips enrichments | Client must use `--hybrid-mode full` for formulas/pictures |
| OCR not working | Start backend with `--force-ocr`, check `--ocr-lang` |
| Permission denied on output dir | Ensure write access to `output_dir` |

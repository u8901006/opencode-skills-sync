---
name: book-worm
description: |
  Use when converting a book (PDF, EPUB, MOBI, AZW3) into chapter-based
  Traditional Chinese public-health articles. Triggers on: make articles
  from book, book to articles, pdf to articles, epub to articles,
  衛教文章, 書籍轉文章, 章節文章. Orchestrates text extraction,
  chapter detection, parallel subagent dispatch, SEO metadata, and index creation.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - Todowrite
metadata:
  trigger: "book to articles, pdf to articles, epub to articles, mobi to articles, 衛教文章, 書籍轉文章, 章節文章, make articles from book, convert book"
  source: "Based on IFS article generation workflow (2026-05-24)"
---

# book-worm: Book-to-Article Pipeline

## Overview

Convert a book (PDF / EPUB / MOBI / AZW3) into chapter-based Traditional Chinese
public-health articles. The pipeline has four phases:

```
Extract → Configure → Dispatch → Assemble
```

Core principle: **Do not reproduce long passages from the source.** Write original
explanatory articles based on each chapter's ideas.

## When to Use

- User provides a book file and asks for chapter-based articles
- "把這本書轉成衛教文章" / "每章寫一篇文章" / "書籍轉文章"
- Any need to decompose a book into standalone knowledge articles

Do NOT use for:
- Single-article SEO optimization → use `seo-writing-skill`
- Copy/文案 rewriting → use `copywriting-optimizer`
- Academic paper writing → use `academic-paper`

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| pymupdf | PDF extraction | `pip install pymupdf` |
| ebooklib | EPUB extraction | `pip install ebooklib` |
| lxml | XML parsing | `pip install lxml` |
| Calibre | MOBI/AZW3 conversion | https://calibre-ebook.com/download |

Before starting, check availability:

```bash
python -c "import fitz; print('pymupdf OK')"
python -c "import ebooklib; print('ebooklib OK')"
where.exe ebook-convert   # Windows — for MOBI/AZW3
```

Install any missing packages. If Calibre is absent, warn the user that MOBI/AZW3
will be skipped.

---

## Phase 1: Extract

### Step 1: Create directories

```
{book_parent_dir}/article/       ← final article output
{tmpdir}/{book-slug}/            ← extraction temp files
```

Where `{book_parent_dir}` = directory containing the book file.
Use `C:\Users\u8901\AppData\Local\Temp\opencode\book-worm-tmp\{book-slug}` for temp.

### Step 2: Run extract.py

```bash
python "<skill_dir>/scripts/extract.py" "<book_path>" --outdir "<tmpdir>"
```

`<skill_dir>` is the directory containing this SKILL.md file.

### Step 3: Check outputs

| File | Contents |
|------|----------|
| `full_text.txt` | Full book text with `[[PAGE N]]` markers |
| `chapters.json` | Array of `{number, title, start_page, end_page, char_count, source_file}` |
| `chapters/chapter-NN-slug.txt` | Per-chapter text with `[[PDF PAGE N]]` markers |

### Step 4: Handle detection failure

If `chapters.json` is empty or chapters look wrong:

1. Read `full_text.txt` pages 5–20 to find the table of contents manually
2. List candidate chapter headings to the user
3. Let the user confirm or manually specify chapter ranges
4. Re-run with `--chapters '{"chapters":[...]}'` override if needed

---

## Phase 2: Configure

Present these defaults to the user for confirmation:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `output_dir` | `{book_parent_dir}/article/` | Where to write .md files |
| `article_type` | `health-edu` | `health-edu` / `knowledge` / `book-review` |
| `language` | `zh-TW` | Target language |
| `chapters_per_agent` | `3` | Chapters per subagent |
| `safety_note` | `true` | Include medical safety note |

If the user says "go" without changes, use defaults silently.

---

## Phase 3: Dispatch

### Batch logic

Given N chapters and `chapters_per_agent` (default 3):

```
num_agents = ceil(N / chapters_per_agent)
batch_i = chapters[(i*3) : ((i+1)*3)]
```

### Dispatch all agents in parallel

Use the `Task` tool to launch all agents in a single message (one `Task` call per
batch). Each agent writes files directly — no need to pass content back.

### Subagent prompt template

Copy and fill the template below for each batch. Replace `{placeholders}`.

```
You are creating {language} {article_type} articles for the general public
based on a book chapter excerpt. Invoke and follow the seo-writing-skill,
copywriting-optimizer, and humanizer-zh-tw skills if available in your
agent environment. Do NOT reproduce long passages from the copyrighted
source; write original explanatory articles based on the chapter's ideas.

Scope: chapters {start_num}–{end_num} only.

Source files:
{list of chapter .txt file paths, one per line}

Output folder:
{output_dir}

Create these NEW Markdown files:
{list of expected output filenames, one per line}

ARTICLE REQUIREMENTS:

1. Language: Taiwan Traditional Chinese ({language}).
2. Audience: general public, people with health concerns and family members.
3. Use the book chapter as the main source, but explain in accessible
   public-health language. Be detailed; no strict word limit.
4. Include YAML frontmatter:
   - title: "[SEO title with keywords]"
   - description: "[120–155 chars]"
   - keywords: [array of 10–15 terms]
   - date: {date}
   - tags: [array]
   - schema_type: "Article"
   - source_chapter: "Chapter N: Title"
   - source_book: "{book_citation}"
5. H1 heading matching the title after frontmatter.
6. Required sections:
   - 核心觀念
   - 章節重點
   - 對民眾的衛教說明 (adapt heading for article_type)
   - 自我覺察練習
   - 何時需要尋求專業協助
   - 常見問題 FAQ (3–5 Q&As)
   - 參考資料
7. {safety_note_block}
8. Professional terms: provide clear translations on first use.
9. For exercises involving trauma, shame, or painful memories, include
   grounding, pacing, and permission to stop.
10. Include JSON-LD Article block near the end.
11. Include JSON-LD FAQPage block near the end.
12. References must include: {book_citation}
    External clinical facts → mark as [NEEDS VERIFICATION].
13. Avoid AI-sounding phrases (see humanizer-zh-tw for the 24 patterns).
    No overuse of bold, em dashes, or formulaic endings.
14. Do NOT overwrite source files.

Return only: list of created files with a brief note about each article's focus.
```

### Safety note block (when safety_note=true)

```
Add a clear safety note near the top of the article:

"安全提醒：[topic]可能有醫療風險。本文是教育文章，不是診斷或治療。
如果症狀嚴重、快速變化，出現昏倒、胸痛、自殺意念、自傷，
或明顯異常行為，請盡快尋求醫療與心理健康專業協助。"
```

Adjust the specific symptoms to match the book's topic.

### Book citation format

```
Author Last, First Initial. (Year). *Title*. Publisher.
```

Example: `Grabowski, A. Y. (2018). *An Internal Family Systems Guide to Recovery from Eating Disorders: Healing Part by Part*. Routledge.`

---

## Phase 4: Assemble

### Step 1: Verify output

For each expected article file, check:

- [ ] File exists in output_dir
- [ ] Starts with `---` (YAML frontmatter)
- [ ] Contains H1 heading (`# `)
- [ ] Contains `application/ld+json`
- [ ] Contains `FAQ`
- [ ] Contains `參考資料`

### Step 2: Create index.md

Write `{output_dir}/index.md` with:

```markdown
---
title: "{book_title} 衛教文章總覽"
description: "依據 {book_title} 各章重點整理的繁體中文衛教文章目錄。"
keywords: [...]
date: {date}
tags: [...]
schema_type: "CollectionPage"
source_book: "{book_citation}"
---

# {book_title} 衛教文章總覽

安全提醒：[generic safety note]

## 章節文章

1. [Chapter 1 title](01-slug.md)
2. [Chapter 2 title](02-slug.md)
...

## 建議閱讀順序

建議依章節順序閱讀。

## 參考資料

- {book_citation}
```

### Step 3: Report results

Print a summary table:

```
| # | File | Lines | Status |
|---|------|-------|--------|
| 1 | 01-xxx.md | 203 | frontmatter:h1:jsonld:faq:refs |
...
```

Mention any `[NEEDS VERIFICATION]` markers found across all articles.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python extract.py "book.pdf"` | Extract PDF text + chapters |
| `python extract.py "book.epub"` | Extract EPUB text + chapters |
| `python extract.py "book.mobi"` | Extract MOBI (needs Calibre) |
| `python extract.py "book.azw3"` | Extract AZW3 (needs Calibre) |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Copying long passages from the book | Rewrite as original explanatory text |
| Missing safety note | Add near the top of every article |
| Inconsistent terminology across chapters | Define a shared glossary before dispatch |
| index.md not updated | Regenerate in Phase 4 |
| MOBI/AZW3 fails silently | Check Calibre availability in Prerequisites |
| All agents write to same file | Each agent gets unique output filenames |
| Forgetting to install Python packages | Run prerequisite checks first |

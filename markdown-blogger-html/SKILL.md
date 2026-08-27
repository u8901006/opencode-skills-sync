---
name: markdown-blogger-html
description: Use when converting Markdown, Word-derived Markdown, or .docx article content into Google Blogger HTML with exact wrapper structure, Blogger read-more marker, tables, references, JSON-LD, and the clinic's system-font CSS styling (no webfonts).
---

# Markdown To Blogger HTML

## Overview
Convert Markdown or Word-derived article content into a single Blogger-ready HTML fragment/file. The output must preserve article semantics while matching the required Blogger structure exactly.

## When To Use
- The user asks to convert Markdown, Word, `.docx`, or article text into Blogger HTML.
- The output must be pasted into Google Blogger HTML mode.
- The article contains headings, references, tables, highlight boxes, JSON-LD, or a lead image.

## Required Output Order
1. Optional Blogger lead image block if the source has a lead image.
2. `<!--more-->` before the article body.
3. `<div id="app-2025-trd-paradigm-failure"><div class="article-content">...` wrapping all article content.
4. CTA card + 延伸閱讀 section (`.pre-faq-actions`) at the end of the article content, right before the references area.
5. Preserved JSON-LD `<script type="application/ld+json">...</script>` blocks.
6. The full CSS block from this skill, wrapped in `<style>/* <![CDATA[ */ ... /* ]]> */</style>`.

`<!--more-->` must appear after the optional lead image, but before `<div id="app-2025-trd-paradigm-failure">`. Never put `<!--more-->` inside `.article-content`.

## No Webfonts — Never Add Google Fonts
Never emit `<link>` tags pointing at `fonts.googleapis.com` or `fonts.gstatic.com`,
and never add `@font-face` or `@import` for a webfont. Typography comes entirely
from the system stack in `--font-body` / `--font-heading` below.

Why this rule exists (measured 2026-08-26): an earlier version of this skill
emitted a fixed three-line Google Fonts block. Because that block lands inside
the post body, it shipped on every article the skill produced — 34% of a
245-post sample, roughly 503 of 1,466 posts. On a live article it pulled
**38 font files totalling 1,982 KB, 55% of a 3,593 KB page**, almost all of it
Noto Sans TC CJK subsets. The Blogger theme ships no webfonts at all and already
declares a system stack, so the block was pure overhead fighting the theme.

The system stack renders Chinese correctly everywhere that matters: Microsoft
JhengHei on Windows, PingFang TC on macOS/iOS, Noto Sans CJK on Android.

## Content Mapping

| Source content | Blogger HTML output |
|---|---|
| Main chapter heading, e.g. `一、...` | `<h2>` |
| Secondary heading, e.g. `1. ...` | `<h3>` |
| Third-level heading, e.g. `(1) ...` | `<h4>` |
| Normal paragraph | `<p>` |
| Summary/leading paragraph, e.g. starts with `核心理念：` | `<p class="strong-lead">` |
| Bullet list | `<ul><li>...` |
| Numbered list | `<ol><li>...` |
| Nested list | Preserve nesting inside the parent `<li>` |
| Divider | `<hr>` |
| Table | `<div class="table-container"><table><thead>...<tbody>...` |
| Highlight / clinical example block | `<div class="highlight-box">` |
| Highlight block title | `<p class="highlight-title">`, not `<div>` or heading |
| References section | `<div class="references"><h3>...` then `<ol>` |
| DOI, PMID, NCT, ISBN, or code-like reference token | Wrap token in `<code>` |

## Strong Lead Rules
- Paragraphs beginning with `核心理念：`, `重點摘要：`, `本文重點：`, `臨床重點：`, or similar summary/lead wording must be `<p class="strong-lead">`.
- Do not leave these lead paragraphs as plain `<p>`.

## Highlight Box Rules
- If the source marks `重點提示`, `臨床情境舉例`, `💡`, `注意`, or similar callout text, wrap the full callout block in `<div class="highlight-box">`.
- The callout title must be the first child inside the box and must use `<p class="highlight-title">`.
- Do not place `<p class="highlight-title">` outside `.highlight-box`.
- Do not use a heading tag for the highlight title.

## Table Rules
- Always wrap tables in `<div class="table-container">`.
- Always split the first row into `<thead>` and remaining rows into `<tbody>`.
- Do not leave Markdown pipe tables in the output.

## References Rules
- Wrap the whole references area in `<div class="references">`.
- The references heading must be `<h3>`.
- The references list must be `<ol>`.
- Wrap DOI strings and similar identifiers in `<code>`.

## CTA & Related Reading Rules
- Insert the CTA card + 延伸閱讀 section at the very end of the article content (`.article-content`), immediately **before** the references area.
- The block uses `<section class="pre-faq-actions" aria-label="預約與延伸閱讀">` containing:
  1. `<div class="appointment-card">` — the CTA card with `.action-title`, a supporting paragraph, and `.action-link` wrapping the appointment link.
  2. `<div class="related-reading">` — a `<p><strong>延伸閱讀：</strong></p>` label followed by one `<p>` per related link.
- Leave a blank line after `</section>` (i.e., whitespace between the related-reading block and whatever follows, such as `<hr>` or the references `</div>`).
- Default appointment link: `https://lin.ee/mUIBMWa`, anchor text `預約李政洋身心診所有相關經驗的心理師`. Use `rel="noopener noreferrer" target="_blank"` on external links.
- If the source article has related-reading links, render each as its own `<p>` inside `.related-reading`; if none are provided, keep the section anyway with an empty list area (leave blank space after it).

## Default CTA & Related Reading Snippet
Use this structure when no custom appointment/reading info is supplied:

```html
<section class="pre-faq-actions" aria-label="預約與延伸閱讀">
  <div class="appointment-card">
    <p class="action-title">需要進一步的專業協助嗎？</p>
    <p>歡迎預約李政洋身心診所有相關經驗的心理師，讓專業人員陪你一起整理這些困擾，逐步理解它們背後的情緒需要。</p>
    <p class="action-link">
      <a href="https://lin.ee/mUIBMWa" rel="noopener noreferrer" target="_blank">預約李政洋身心診所有相關經驗的心理師</a>
    </p>
  </div>
  <div class="related-reading">
    <p><strong>延伸閱讀：</strong></p>
    <p><a href="RELATED_READING_URL" rel="noopener noreferrer" target="_blank">延伸閱讀標題</a></p>
  </div>
</section>
```

## JSON-LD Rules
- Preserve every JSON-LD block from the source.
- Do not escape JSON-LD into visible text.
- Keep it as `<script type="application/ld+json">...</script>`.
- If generating a full HTML file, JSON-LD may sit before or after `<!--more-->`, but it must remain valid JSON.
- **Write CJK punctuation as real characters — never as numeric character
  references.** Inside a `<script>` element the content is raw text, so HTML
  entities are *not* decoded: `&#65292;` reaches Google as the literal seven
  characters `&#65292;`, not as `，`. Use `，、。？（）｜` directly.
  A 2026-08-26 audit found 862 such escapes across an 80-post sample, up to 142
  on a single page, 91% of them inside post-body JSON-LD like this skill emits.
  Before finishing, check the output contains no `&#` sequence inside any
  `application/ld+json` block.
- Do not emit an `Article` (or `BlogPosting`) block if the Blogger theme already
  renders one. The theme at `theme-20260826-v2.xml` outputs
  `["Article","MedicalWebPage"]` on every item page; a second one from the post
  body produces two competing entities with conflicting headline and author,
  which is worse than having none. `FAQPage`, `HowTo`, and similar
  content-specific types are fine — they do not collide.

## Blogger Image Rules
If the source has a lead image, use Blogger-compatible structure:

```html
<div class="separator" style="clear: both; text-align: center;">
  <a href="IMAGE_URL" style="margin-left: 1em; margin-right: 1em;">
    <img alt="ALT_TEXT" border="0" data-original-height="HEIGHT" data-original-width="WIDTH" src="IMAGE_URL" />
  </a>
</div>
```

## Validation Checklist
Before finishing, verify:
- No `<link>` to `fonts.googleapis.com` / `fonts.gstatic.com` anywhere in the output.
- No `@font-face` or `@import` webfont declaration in the CSS.
- `<!--more-->` appears before the root article container.
- `<!--more-->` does not appear inside `#app-2025-trd-paradigm-failure`.
- All content is inside `#app-2025-trd-paradigm-failure .article-content`.
- Heading levels are `h2`, `h3`, `h4` per mapping.
- Highlight titles use `<p class="highlight-title">`.
- Highlight titles are inside `.highlight-box`, not before it.
- Strong lead paragraphs use `<p class="strong-lead">`.
- Tables have `.table-container`, `<thead>`, and `<tbody>`.
- References use `.references`, `<h3>`, `<ol>`, and `<code>` for identifiers.
- `.pre-faq-actions` (CTA card + 延伸閱讀) is present at the end of `.article-content`, before the references area.
- The `.appointment-card` CTA links to `https://lin.ee/mUIBMWa` with `rel="noopener noreferrer" target="_blank"`.
- Blank space is left after `</section>` (between the related-reading block and the references area).
- JSON-LD is preserved as script, not converted to paragraph text.
- The full CSS below is included exactly once.

## Common Mistakes
- Using placeholder CSS instead of the full CSS block.
- Converting reference headings to `<h2>`.
- Using `<div class="highlight-title">`; it must be `<p class="highlight-title">`.
- Omitting `<!--more-->`.
- Putting `<!--more-->` inside the article wrapper instead of before it.
- Leaving Markdown tables unconverted.
- Removing or escaping JSON-LD.
- Adding a Google Fonts `<link>`, `@font-face`, or `@import`.
- Writing CJK punctuation inside JSON-LD as numeric character references.
- Omitting the `.pre-faq-actions` CTA / 延伸閱讀 section.
- Placing the CTA / 延伸閱讀 section after the references area instead of before it.
- Squeezing the `</section>` directly against the next element without a blank line.

## Required CSS

```html
<style>/* <![CDATA[ */#app-2025-trd-paradigm-failure {

  /* --- Design Tokens --- */

  --font-body: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif;

  --font-heading: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif;

  --color-surface: #ffffff;

  --color-title: #2c3e50;

  --color-text: #34495e;

  --color-text-light: #526c84;

  --color-accent: #3498db;

  --color-accent-hover: #2980b9;

  --color-accent-bg: #eaf2f8;

  --color-border: #e0e5ea;

  --color-table-header: #f8f9fa;

  --shadow-level-1: 0 4px 12px rgba(0,0,0,.08);



  /* --- Base Styles & Resets --- */

  font-family: var(--font-body);

  color: var(--color-text);

  line-height: 1.8;

  background-color: transparent;

  padding: 1rem 0;

  box-sizing: border-box;

}#app-2025-trd-paradigm-failure *,#app-2025-trd-paradigm-failure *::before,#app-2025-trd-paradigm-failure *::after {

  box-sizing: border-box;

}#app-2025-trd-paradigm-failure .article-content {

    background-color: var(--color-surface);

    padding: 20px 30px;

    border-radius: 8px;

    box-shadow: var(--shadow-level-1);

}#app-2025-trd-paradigm-failure h1,#app-2025-trd-paradigm-failure h2,#app-2025-trd-paradigm-failure h3,#app-2025-trd-paradigm-failure h4 {

  font-family: var(--font-heading);

  color: var(--color-title);

  margin: 1.5em 0 0.8em;

  line-height: 1.4;

  font-weight: 700;

  padding-bottom: 0.3em;

  border-bottom: 1px solid var(--color-border);

}#app-2025-trd-paradigm-failure h2 { font-size: 1.8em; }#app-2025-trd-paradigm-failure h3 { font-size: 1.4em; border-bottom-style: dashed;}#app-2025-trd-paradigm-failure h4 { font-size: 1.1em; font-weight: 600; border-bottom: none; }#app-2025-trd-paradigm-failure p {

  margin: 0 0 1.2em;

}#app-2025-trd-paradigm-failure a {

  color: var(--color-accent);

  text-decoration: none;

  transition: color 0.2s ease;

}#app-2025-trd-paradigm-failure a:hover {

  color: var(--color-accent-hover);

  text-decoration: underline;

}#app-2025-trd-paradigm-failure strong, #app-2025-trd-paradigm-failure b {

    font-weight: 700;

    color: var(--color-title);

}#app-2025-trd-paradigm-failure .strong-lead {

    font-size: 1.1em;

    font-weight: 500;

    color: var(--color-title);

    border-left: 4px solid var(--color-accent);

    padding-left: 1em;

    margin: 1.5em 0;

}#app-2025-trd-paradigm-failure ul,#app-2025-trd-paradigm-failure ol {

  margin: 0 0 1.5em;

  padding-left: 2em;

}#app-2025-trd-paradigm-failure li {

  margin-bottom: 0.8em;

  padding-left: 0.5em;

}#app-2025-trd-paradigm-failure ul ul, #app-2025-trd-paradigm-failure ul ol,#app-2025-trd-paradigm-failure ol ul, #app-2025-trd-paradigm-failure ol ol {

    margin-top: 0.5em;

    margin-bottom: 0.8em;

}#app-2025-trd-paradigm-failure li::marker {

  color: var(--color-accent);

  font-weight: bold;

}#app-2025-trd-paradigm-failure .highlight-box {

    background-color: var(--color-accent-bg);

    border: 1px solid var(--color-border);

    border-left: 5px solid var(--color-accent);

    padding: 1.5em;

    margin: 2em 0;

    border-radius: 4px;

}#app-2025-trd-paradigm-failure .highlight-box .highlight-title {

    font-size: 1.2em;

    font-weight: bold;

    color: var(--color-title);

    margin-top: 0;

}#app-2025-trd-paradigm-failure .highlight-box ul {

    margin-bottom: 0;

}#app-2025-trd-paradigm-failure .table-container {

    overflow-x: auto;

    margin: 2em 0;

}#app-2025-trd-paradigm-failure table {

  width: 100%;

  border-collapse: collapse;

  border: 1px solid var(--color-border);

}#app-2025-trd-paradigm-failure th,#app-2025-trd-paradigm-failure td {

  padding: 12px 15px;

  text-align: left;

  border: 1px solid var(--color-border);

  vertical-align: top;

}#app-2025-trd-paradigm-failure thead th {

  background-color: var(--color-table-header);

  font-family: var(--font-heading);

  font-weight: 600;

  color: var(--color-title);

}#app-2025-trd-paradigm-failure tbody tr:nth-child(even) {

  background-color: #fdfdfd;

}#app-2025-trd-paradigm-failure hr {

    border: none;

    height: 1px;

    background-color: var(--color-border);

    margin: 3em 0;

}#app-2025-trd-paradigm-failure .references {

    font-size: 0.9em;

    color: var(--color-text-light);

}#app-2025-trd-paradigm-failure .references ol {

    padding-left: 1.5em;

    line-height: 1.7;

}#app-2025-trd-paradigm-failure .references li {

    margin-bottom: 1em;

}#app-2025-trd-paradigm-failure .references code {

    font-family: monospace;

    background-color: #ecf0f1;

    padding: 2px 5px;

    border-radius: 3px;

    font-size: 0.95em;

}#app-2025-trd-paradigm-failure .pre-faq-actions {

  border-top: 1px solid var(--color-border);

  margin: 3em 0 2em;

  padding-top: 2em;

}#app-2025-trd-paradigm-failure .appointment-card {

  background-color: var(--color-accent-bg);

  border: 1px solid var(--color-border);

  border-left: 5px solid var(--color-accent);

  border-radius: 6px;

  margin-bottom: 1.5em;

  padding: 1.5em;

}#app-2025-trd-paradigm-failure .appointment-card .action-title {

  color: var(--color-title);

  font-family: var(--font-heading);

  font-size: 1.2em;

  font-weight: 700;

  margin-bottom: 0.6em;

}#app-2025-trd-paradigm-failure .appointment-card .action-link { margin-bottom: 0; }#app-2025-trd-paradigm-failure .appointment-card .action-link a {

  display: inline-block;

  background-color: var(--color-accent);

  border-radius: 5px;

  color: #ffffff;

  font-weight: 700;

  padding: 0.7em 1.1em;

  text-decoration: none;

}#app-2025-trd-paradigm-failure .appointment-card .action-link a:hover {

  background-color: var(--color-accent-hover);

  color: #ffffff;

  text-decoration: none;

}#app-2025-trd-paradigm-failure .related-reading {

  border: 1px solid var(--color-border);

  border-radius: 6px;

  padding: 1.2em 1.5em;

}#app-2025-trd-paradigm-failure .related-reading p { margin-bottom: 0; }@media (min-width: 1100px) {

    .item-page .post-body { max-width: 1100px !important; }

}@media (max-width: 768px) {

    #app-2025-trd-paradigm-failure .article-content {

        padding: 15px 20px;

    }

    #app-2025-trd-paradigm-failure h2 { font-size: 1.6em; }

    #app-2025-trd-paradigm-failure h3 { font-size: 1.3em; }

}/* ]]> */</style>
```

#!/usr/bin/env python
"""
book-worm extract.py — Extract text and detect chapters from PDF/EPUB/MOBI/AZW3.

Usage:
    python extract.py <input_path> [--outdir DIR]

Output:
    {outdir}/full_text.txt          Full text with page markers
    {outdir}/chapters.json          Chapter metadata array
    {outdir}/chapters/              Per-chapter text files
"""

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile


def slugify(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", t)
    return t.strip("-")[:80]


def detect_format(path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    fmt_map = {".pdf": "pdf", ".epub": "epub", ".mobi": "mobi", ".azw3": "azw3", ".azw": "azw3"}
    if suffix in fmt_map:
        return fmt_map[suffix]
    raise ValueError(f"Unsupported format: {suffix}")


def check_dependencies(fmt: str) -> None:
    if fmt == "pdf":
        try:
            import fitz
        except ImportError:
            print("ERROR: pymupdf not installed. Run: pip install pymupdf", file=sys.stderr)
            sys.exit(1)
    elif fmt == "epub":
        try:
            import ebooklib
        except ImportError:
            print("ERROR: ebooklib not installed. Run: pip install ebooklib", file=sys.stderr)
            sys.exit(1)
    elif fmt in ("mobi", "azw3"):
        if not shutil.which("ebook-convert"):
            print(
                "ERROR: ebook-convert not found. Install Calibre: https://calibre-ebook.com/download",
                file=sys.stderr,
            )
            sys.exit(1)


def convert_to_epub(input_path: pathlib.Path, tmpdir: pathlib.Path) -> pathlib.Path:
    out_epub = tmpdir / (input_path.stem + ".epub")
    cmd = ["ebook-convert", str(input_path), str(out_epub)]
    print(f"Converting {input_path.name} -> EPUB ...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"ebook-convert stderr: {result.stderr[:500]}", file=sys.stderr)
        raise RuntimeError("ebook-convert failed")
    return out_epub


def extract_pdf(input_path: pathlib.Path) -> tuple[list[str], list[str]]:
    import fitz

    doc = fitz.open(str(input_path))
    pages = []
    for p in doc:
        pages.append(p.get_text("text"))
    doc.close()
    page_markers = [f"[[PAGE {i+1}]]" for i in range(len(pages))]
    return pages, page_markers


def extract_epub(input_path: pathlib.Path) -> tuple[list[str], list[str]]:
    import ebooklib
    from ebooklib import epub

    book = epub.read_epub(str(input_path), options={"ignore_ncx": True})
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    pages = []
    markers = []
    for idx, item in enumerate(items, 1):
        import lxml.html

        html_content = item.get_content()
        if isinstance(html_content, str):
            html_content = html_content.encode("utf-8", errors="replace")
        import re as _re
        html_content = _re.sub(rb'<\?xml[^?]*\?>', b'', html_content)
        tree = lxml.html.fromstring(html_content)
        text = tree.text_content().strip()
        if text:
            pages.append(text)
            markers.append(f"[[CHAPTER {idx}]]")
    return pages, markers


def build_full_text(pages: list[str], markers: list[str]) -> str:
    parts = []
    for marker, text in zip(markers, pages):
        parts.append(f"{marker}\n\n{text}")
    return "\n\n".join(parts)


def detect_chapters_pdf(pages: list[str], total_pages: int) -> list[dict]:
    toc_entries = []
    toc_patterns = [
        re.compile(r"^(\d+)\s{2,}(.+)$"),
        re.compile(r"^(Chapter|CHAPTER)\s+(\d+)\b\s*(.*)$"),
        re.compile(r"^(\d+)\s{2,}(.+?)\s{2,}\d+$"),
    ]

    scan_end = min(20, len(pages))
    for page_idx in range(min(5, scan_end), scan_end):
        for line in pages[page_idx].splitlines():
            s = line.strip()
            if not s:
                continue
            for pat in toc_patterns:
                m = pat.match(s)
                if m:
                    if pat is toc_patterns[1]:
                        num = int(m.group(2))
                        title = m.group(3).strip() if m.group(3) else ""
                    else:
                        num = int(m.group(1))
                        title = m.group(2).strip()
                    if 1 <= num <= 50 and len(title) > 3:
                        toc_entries.append({"num": num, "title": title, "toc_line": s})
                    break
        if len(toc_entries) >= 3:
            break

    if len(toc_entries) < 2:
        return _detect_chapters_pdf_body(pages, total_pages)

    seen = set()
    unique = []
    for e in toc_entries:
        key = (e["num"], e["title"][:30])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    body_starts = []
    for entry in unique:
        search_phrase = entry["title"]
        if len(search_phrase) < 4:
            continue
        matches = []
        for page_idx in range(len(pages)):
            for line in pages[page_idx].splitlines():
                s = " ".join(line.strip().split())
                if not s:
                    continue
                num_str = str(entry["num"])
                if s.startswith(num_str + " ") and len(s) > len(num_str) + 1:
                    remainder = s[len(num_str):].strip()
                    if remainder and search_phrase.lower() in remainder.lower():
                        matches.append(page_idx + 1)
                        break
        if len(matches) >= 2:
            body_starts.append(
                {"num": entry["num"], "title": entry["title"], "page": matches[-1]}
            )
        elif len(matches) == 1:
            body_starts.append(
                {"num": entry["num"], "title": entry["title"], "page": matches[0]}
            )

    if len(body_starts) < 2:
        return _detect_chapters_pdf_body(pages, total_pages)

    chapters = []
    for i, bs in enumerate(body_starts):
        start = bs["page"]
        if i + 1 < len(body_starts):
            end = body_starts[i + 1]["page"] - 1
        else:
            end = total_pages
        chapters.append(
            {"number": bs["num"], "title": bs["title"], "start_page": start, "end_page": end}
        )

    return chapters


def _detect_chapters_pdf_body(pages: list[str], total_pages: int) -> list[dict]:
    heading_patterns = [
        re.compile(r"^(\d+)\s{2,}([A-Z][A-Za-z ,:;\-'\u2019]{5,80})$"),
        re.compile(r"^(Chapter|CHAPTER)\s+(\d+)\s*[:.]?\s*(.*)$"),
    ]
    toc_skip = min(20, len(pages))
    candidates = []
    for page_idx in range(toc_skip, len(pages)):
        for line in pages[page_idx].splitlines():
            s = " ".join(line.strip().split())
            if not s:
                continue
            for pat in heading_patterns:
                m = pat.match(s)
                if m:
                    if pat is heading_patterns[0]:
                        num = int(m.group(1))
                        title = m.group(2).strip()
                    else:
                        num = int(m.group(2))
                        title = m.group(3).strip() if m.group(3) else f"Chapter {num}"
                    if 1 <= num <= 50 and len(title) > 3:
                        candidates.append(
                            {"number": num, "title": title, "page": page_idx + 1}
                        )
                    break

    seen_pages = set()
    unique = []
    for c in candidates:
        if c["page"] not in seen_pages:
            seen_pages.add(c["page"])
            unique.append(c)

    chapters = []
    for i, c in enumerate(unique):
        start = c["page"]
        if i + 1 < len(unique):
            end = unique[i + 1]["page"] - 1
        else:
            end = total_pages
        chapters.append(
            {"number": c["number"], "title": c["title"], "start_page": start, "end_page": end}
        )
    return chapters


def detect_chapters_epub(pages: list[str]) -> list[dict]:
    chapters = []
    for i, text in enumerate(pages, 1):
        first_line = ""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                first_line = stripped
                break
        title = first_line[:80] if first_line else f"Section {i}"
        chapters.append({"number": i, "title": title, "page": i})
    return chapters


def split_chapters(
    pages: list[str], chapters_meta: list[dict], markers: list[str], is_pdf: bool
) -> list[dict]:
    results = []
    for ch in chapters_meta:
        if is_pdf:
            start_idx = ch["start_page"] - 1
            end_idx = ch["end_page"]
            ch_pages = pages[start_idx:end_idx]
            ch_markers = markers[start_idx:end_idx]
        else:
            page_num = ch.get("page", ch["number"]) - 1
            if page_num < len(pages):
                ch_pages = [pages[page_num]]
                ch_markers = [markers[page_num]]
            else:
                ch_pages = []
                ch_markers = []

        text = "\n\n".join(f"{m}\n{t}" for m, t in zip(ch_markers, ch_pages))
        char_count = len(text)
        slug = slugify(ch["title"])
        filename = f"chapter-{ch['number']:02d}-{slug}.txt"

        results.append(
            {
                "number": ch["number"],
                "title": ch["title"],
                "start_page": ch.get("start_page", ch.get("page", ch["number"])),
                "end_page": ch.get("end_page", ch.get("page", ch["number"])),
                "char_count": char_count,
                "source_file": f"chapters/{filename}",
                "text": text,
                "filename": filename,
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(description="Extract text and chapters from a book")
    parser.add_argument("input", help="Path to book file (PDF/EPUB/MOBI/AZW3)")
    parser.add_argument("--outdir", help="Output directory", default=None)
    args = parser.parse_args()

    input_path = pathlib.Path(args.input).resolve()
    if not input_path.exists():
        print(f"ERROR: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    fmt = detect_format(input_path)
    check_dependencies(fmt)

    book_slug = slugify(input_path.stem)
    outdir = pathlib.Path(args.outdir) if args.outdir else pathlib.Path.cwd() / "extracted" / book_slug
    outdir.mkdir(parents=True, exist_ok=True)
    chapters_dir = outdir / "chapters"
    chapters_dir.mkdir(exist_ok=True)

    is_pdf = fmt == "pdf"

    if fmt in ("mobi", "azw3"):
        with tempfile.TemporaryDirectory() as tmp:
            epub_path = convert_to_epub(input_path, pathlib.Path(tmp))
            pages, markers = extract_epub(epub_path)
        is_pdf = False
    elif fmt == "epub":
        pages, markers = extract_epub(input_path)
    else:
        pages, markers = extract_pdf(input_path)

    full_text = build_full_text(pages, markers)
    (outdir / "full_text.txt").write_text(full_text, encoding="utf-8")
    print(f"full_text.txt: {len(pages)} pages, {len(full_text)} chars")

    if is_pdf:
        chapters_meta = detect_chapters_pdf(pages, len(pages))
    else:
        chapters_meta = detect_chapters_epub(pages)

    if not chapters_meta:
        print("WARNING: No chapters detected. Writing full_text.txt only.", file=sys.stderr)
        (outdir / "chapters.json").write_text("[]", encoding="utf-8")
        sys.exit(0)

    split = split_chapters(pages, chapters_meta, markers, is_pdf)

    json_out = []
    for ch in split:
        ch_path = chapters_dir / ch["filename"]
        header = f"Chapter {ch['number']}: {ch['title']}\n"
        if is_pdf:
            header += f"PDF pages {ch['start_page']}-{ch['end_page']}\n"
        header += "\n"
        ch_path.write_text(header + ch["text"], encoding="utf-8")
        json_out.append(
            {
                "number": ch["number"],
                "title": ch["title"],
                "start_page": ch["start_page"],
                "end_page": ch["end_page"],
                "char_count": ch["char_count"],
                "source_file": ch["source_file"],
            }
        )
        print(f"  {ch['number']}|{ch['title']}|pages {ch['start_page']}-{ch['end_page']}|{ch['char_count']} chars")

    (outdir / "chapters.json").write_text(
        json.dumps(json_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nDone. {len(json_out)} chapters extracted to {outdir}")


if __name__ == "__main__":
    main()

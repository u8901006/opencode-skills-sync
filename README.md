# opencode-skills-sync

Backup and sync of custom opencode skills (`~/.config/opencode/skills/`).

## Contents

| Skill | Description |
|-------|-------------|
| book-worm | Convert books (PDF/EPUB/MOBI/AZW3) into Traditional Chinese public-health articles |
| book-worm-auto-optimize | Book-to-articles + full optimize-article pipeline in one run |
| optimize-article | Full SEO article optimization pipeline (diagnose, citations, Sugarman, humanize) |
| papers-to-blog | Convert research PDFs into categorized blog articles |
| seo-article-checker | 10-point SEO article audit checklist |
| nlm-skill | NotebookLM CLI and MCP server guide |
| llama-index | LlamaIndex RAG pipeline skill |
| gsap-core | GSAP core API skill |
| gsap-frameworks | GSAP for Vue/Svelte frameworks |
| gsap-performance | GSAP performance optimization |
| gsap-plugins | GSAP plugin registration and usage |
| gsap-react | GSAP for React/Next.js |
| gsap-scrolltrigger | GSAP ScrollTrigger skill |
| gsap-timeline | GSAP timeline and sequencing |
| gsap-utils | GSAP utility functions |

## Sync on a new computer

### Using `gh` CLI (recommended)

```bash
gh repo clone u8901006/opencode-skills-sync ~/.config/opencode/skills
```

### Using plain git

```bash
git clone https://github.com/u8901006/opencode-skills-sync.git ~/.config/opencode/skills
```

> If the `skills` directory already exists (e.g. opencode created it),
> remove or back it up first, then clone.

### Windows (PowerShell)

```powershell
git clone https://github.com/u8901006/opencode-skills-sync.git "$env:USERPROFILE\.config\opencode\skills"
```

## Update skills from GitHub

```bash
cd ~/.config/opencode/skills
git pull
```

## Push local changes to GitHub

```bash
cd ~/.config/opencode/skills
git add -A
git commit -m "Update skills"
git push
```

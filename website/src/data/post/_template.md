---
# ─────────────── Required ───────────────
title: 'Your post title here'

# ─────────────── Identity ───────────────
publishDate: 2026-06-30T00:00:00Z
draft: true

# ─────────────── Listing & SEO ───────────────
excerpt: A one-sentence summary that shows up in lists, RSS, and meta description.
# category: Gloss
# tags:
#   - example
# image: /assets/images/your-image.webp

# ─────────────── Optional structured data ───────────────
# metadata:
#   canonical: https://werner.bisschoff.dev/notes/your-slug
#   description: Override the meta description.
#   openGraph:
#     images:
#       - url: /assets/images/og-image.png
#         width: 1200
#         height: 630
---

## Overview

One or two sentences setting up the problem or topic. This paragraph carries the
weight — readers decide to keep reading here.

## Section heading

Body content. Markdown features that work:

- **Bold**, _italic_, `inline code`
- [Internal link](/notes/other-post-slug) — use absolute paths
- > Blockquote for callouts

```typescript
// Fenced code blocks with language hints
function example(): void {
  const signal = 'syntax-highlighted';
}
```

1. Numbered
2. Lists

### Subsection

Closer detail, edge cases, or worked examples.

## Closing

Conclude with what's next, a related post, or a question for the reader.

<!--
────────────────────────────────────────────────────────────
Slug = filename (without .md). Drop into website/src/data/post/
and rename to your-slug.md.

Examples:
  intro-to-foo.md         → /notes/intro-to-foo
  why-x-matters.md        → /notes/why-x-matters

Checklist before publishing:
  [ ] Filename is the slug you want in the URL
  [ ] draft: false
  [ ] publishDate matches intended publish date
  [ ] excerpt is one short sentence
  [ ] Uncomment + fill in category if it fits an existing one
  [ ] Uncomment + set tags (existing slugs where possible)
  [ ] No leading # H1 — page H1 comes from `title:` frontmatter
────────────────────────────────────────────────────────────
-->

# Writings

Things written *about* the Agent Colony pattern, captured here as part of its evolution. Articles, blog posts, talks, interviews. Each entry preserves the canonical text alongside a link to where it was first published.

## Why preserve the text in the repo as well as linking to it?

Three reasons:

1. **Versioning.** Medium and other platforms can edit, unpublish, or reorganise. The version of the article in this folder is the version that reflects the state of the pattern at the time it was written. If the live URL changes, the in-repo copy still tells a future reader what was said when.
2. **Provenance.** When the next version of the pattern revises a claim, future contributors can trace what was published and what has since been changed. A live URL is a moving target; a file in git is not.
3. **Visibility.** Readers who land on the GitHub repo should be able to find the writings without leaving — both as on-ramps for new readers and as evidence of the pattern's evolution.

## Convention

Each file is dated and slug-named:

```
YYYY-MM-DD-short-slug.md
```

Each file starts with frontmatter capturing:

```yaml
---
title: [full title]
author: [author name]
date_published: YYYY-MM-DD
venue: [Medium / personal blog / conference / etc]
url: [canonical URL]
audience: [general / practitioner / academic / standards]
pattern_version_referenced: [v1.x.y or 'general — does not cite a specific version']
length: [approximate read time or word count]
---
```

## Current writings

| File | Date | Title | Venue | Audience |
|------|------|-------|-------|----------|
| [`2026-04-12-it-takes-a-village.md`](2026-04-12-it-takes-a-village.md) | 2026-04-12 | It takes a village — the Agent Colony definition | Medium | General |

## How writings relate to the rest of the knowledge base

| Folder | Direction of flow |
|--------|------------------|
| **`feedback/`** | Incoming — what other people said about the pattern |
| **`writings/`** | Outgoing — what the author said about the pattern |
| **`lessons/`** | Distilled — what was learned from both directions |
| **`references/`** | Inherited — what the pattern draws on from elsewhere |

Together the four cover the full conversation: the pattern speaks (writings), people respond (feedback), insights emerge (lessons), and the whole thing is anchored in the existing literature (references).

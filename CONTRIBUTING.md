# Contributing to Pattern & Post

Every submission goes through an automated Claude AI review before a human maintainer approves it.

---

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/DesignPatternsReviewSystem.git
cd DesignPatternsReviewSystem

# 2. Create a branch
git checkout -b add/my-observer-pattern

# 3. Add your file (see templates below)

# 4. Commit and push
git add _patterns/observer-pattern.md
git commit -m "Add Observer pattern"
git push origin add/my-observer-pattern

# 5. Open a pull request — the AI review starts automatically
```

---

## File Locations

| Content type   | Directory       | URL slug              |
|----------------|-----------------|------------------------|
| Design Pattern | `_patterns/`    | `/patterns/my-slug/`  |
| Blog Article   | `_posts/`       | `/blog/YYYY-MM-DD-my-slug/` |
| Tutorial       | `_tutorials/`   | `/tutorials/my-slug/` |

---

## Front Matter Templates

### Design Pattern — `_patterns/my-pattern-name.md`

```yaml
---
title: "Observer Pattern"
description: "One-sentence description shown in cards and SEO."
date: 2026-05-13
author: "Your Name"
pattern_type: "Behavioral"       # Creational | Structural | Behavioral
difficulty: "Intermediate"       # Beginner | Intermediate | Advanced
languages: ["Python", "Java"]    # code examples you include
also_known_as: "Event-Subscriber, Listener"   # optional
review_status: "pending"         # leave as pending — reviewer updates this
tags: ["behavioral", "events"]
---
```

### Blog Article — `_posts/YYYY-MM-DD-my-title.md`

```yaml
---
title: "Your Article Title"
description: "One-sentence description."
date: 2026-05-13
author: "Your Name"
category: "Software Design"      # optional
reading_time: 8                  # estimated minutes
review_status: "pending"
tags: ["design-patterns", "architecture"]
---
```

### Tutorial — `_tutorials/my-tutorial-slug.md`

```yaml
---
title: "How to Implement X"
description: "One-sentence description."
date: 2026-05-13
author: "Your Name"
level: "Beginner"                # Beginner | Intermediate | Advanced
reading_time: 15
prerequisites: ["Basic Python", "OOP fundamentals"]
review_status: "pending"
tags: ["python", "patterns"]
---
```

---

## Content Guidelines

### Design Patterns must include
- **Intent** — one paragraph explaining what it solves
- **Problem** — the recurring scenario
- **Solution** — how the pattern addresses it
- **Code example** — at least one working, runnable snippet
- **When to use / When to avoid**
- **Pros & Cons**

### Blog Articles must include
- A clear thesis stated in the first paragraph
- Concrete examples or code that support the argument
- A conclusion with a practical takeaway

### Tutorials must include
- Clear prerequisites in front matter
- Step-by-step instructions (numbered or clearly headed)
- Working code at each step
- A summary of what was learned

---

## Code Style

- All code blocks must specify the language: ` ```python `, ` ```java `, etc.
- Show complete, runnable snippets — avoid `...` placeholders unless unavoidable
- Include a brief comment only when the *why* is non-obvious

---

## AI Review Process

When you open a PR touching `_patterns/`, `_posts/`, or `_tutorials/`, the `AI Content Review` GitHub Action runs automatically and posts a comment like this:

```
✅ _patterns/observer-pattern.md — Design Pattern
Overall score: 9/10  ██████████
Verdict: APPROVED
```

The review scores five dimensions: **Technical Accuracy**, **Code Quality**, **Clarity**, **Structure**, and **Completeness**.

- **approved** (score ≥ 8, no required changes) → maintainer can merge immediately
- **needs_revision** → address the required changes and push a new commit; the action re-runs
- **rejected** → significant rework needed; the CI check fails

---

## Setting Up the Secret

Maintainers must add `ANTHROPIC_API_KEY` as a repository secret before the review action works:

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY` — Value: your key from [console.anthropic.com](https://console.anthropic.com)

---

## Enabling GitHub Pages

1. Go to **Settings → Pages**
2. Source: **GitHub Actions**
3. Push to `main` — the `Deploy to GitHub Pages` action builds and publishes automatically

---

## Commit Message Convention

```
Add <Pattern/Article/Tutorial title>
Fix <what was fixed>
Update <what was updated>
```

---

## License

By submitting, you agree your content will be published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

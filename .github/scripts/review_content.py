#!/usr/bin/env python3
"""
AI content review script for the Pattern & Post review system.
Called by the GitHub Action on every PR that touches _patterns/, _posts/, or _tutorials/.
Posts a structured review as a PR comment via the GitHub API.
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path

import anthropic


CONTENT_DIRS = {"_patterns", "_posts", "_tutorials"}

SYSTEM_PROMPT = """You are a senior software engineer and technical writer reviewing community-submitted content
for a design patterns and engineering blog. Your reviews are constructive, specific, and actionable.

You evaluate content across five dimensions and return ONLY valid JSON — no markdown fences, no extra text."""

REVIEW_PROMPT = """Review the following {content_type} submission.

--- FRONT MATTER ---
{front_matter}

--- CONTENT ---
{body}

Return a JSON object with exactly this shape:
{{
  "score": <integer 1-10>,
  "verdict": "approved" | "needs_revision" | "rejected",
  "summary": "<2-3 sentence overall assessment>",
  "dimensions": {{
    "technical_accuracy": {{
      "score": <1-10>,
      "notes": "<specific finding>"
    }},
    "code_quality": {{
      "score": <1-10>,
      "notes": "<specific finding — or 'N/A' if no code>"
    }},
    "clarity": {{
      "score": <1-10>,
      "notes": "<specific finding>"
    }},
    "structure": {{
      "score": <1-10>,
      "notes": "<specific finding>"
    }},
    "completeness": {{
      "score": <1-10>,
      "notes": "<specific finding>"
    }}
  }},
  "required_changes": ["<actionable item>", ...],
  "suggestions": ["<optional improvement>", ...],
  "front_matter_issues": ["<missing or incorrect front matter field>", ...]
}}

Scoring guide:
- 9-10: Excellent, ready to publish
- 7-8:  Good, minor polish needed
- 5-6:  Acceptable but needs work
- 3-4:  Significant issues
- 1-2:  Major rework required

Verdict guide:
- approved       → score >= 8 AND required_changes is empty
- needs_revision → score 5-7 OR required_changes non-empty
- rejected       → score <= 4 OR factually incorrect / harmful content
"""

CONTENT_TYPE_LABELS = {
    "_patterns":  "Design Pattern",
    "_posts":     "Blog Article",
    "_tutorials": "Tutorial",
}

REQUIRED_FRONT_MATTER = {
    "_patterns":  {"title", "description", "date", "author", "pattern_type"},
    "_posts":     {"title", "description", "date", "author"},
    "_tutorials": {"title", "description", "date", "author", "level"},
}


def get_changed_content_files() -> list[Path]:
    """Return changed Markdown files in the content directories from the current PR."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True, text=True, check=True
        )
        files = result.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        # Fallback: diff against HEAD~1 for the first commit
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, check=True
        )
        files = result.stdout.strip().splitlines()

    content_files = []
    for f in files:
        path = Path(f)
        if path.suffix == ".md" and path.parts and path.parts[0] in CONTENT_DIRS:
            if path.exists():
                content_files.append(path)
    return content_files


def parse_front_matter(raw: str) -> tuple[dict, str]:
    """Split YAML front matter from body. Returns (front_matter_dict, body)."""
    if not raw.startswith("---"):
        return {}, raw

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw

    fm_raw = parts[1].strip()
    body = parts[2].strip()

    fm = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")

    return fm, body


def review_file(client: anthropic.Anthropic, file_path: Path) -> dict:
    """Send one file to Claude for review and return the parsed result."""
    content_dir = file_path.parts[0]
    content_type = CONTENT_TYPE_LABELS.get(content_dir, "Article")
    required_fields = REQUIRED_FRONT_MATTER.get(content_dir, set())

    raw = file_path.read_text(encoding="utf-8")
    front_matter, body = parse_front_matter(raw)

    # Check front matter completeness before sending to Claude
    missing_fields = required_fields - set(front_matter.keys())

    prompt = REVIEW_PROMPT.format(
        content_type=content_type,
        front_matter=json.dumps(front_matter, indent=2),
        body=body[:8000],  # guard against very long docs
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_json = message.content[0].text.strip()
    # Strip accidental markdown fences
    raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json)
    raw_json = re.sub(r"\s*```$", "", raw_json)

    result = json.loads(raw_json)

    # Merge any front-matter issues detected locally
    if missing_fields:
        existing = result.get("front_matter_issues", [])
        result["front_matter_issues"] = existing + [
            f"Missing required field: `{f}`" for f in sorted(missing_fields)
        ]

    result["file"] = str(file_path)
    result["content_type"] = content_type
    return result


def verdict_emoji(verdict: str) -> str:
    return {"approved": "✅", "needs_revision": "⚠️", "rejected": "❌"}.get(verdict, "❓")


def score_bar(score: int) -> str:
    filled = round(score / 10 * 10)
    return "█" * filled + "░" * (10 - filled)


def format_comment(reviews: list[dict]) -> str:
    lines = [
        "## 🤖 Claude AI Content Review",
        "",
        "> Automated review powered by [Claude](https://www.anthropic.com/claude). "
        "A maintainer will make the final merge decision.",
        "",
    ]

    for r in reviews:
        verdict = r.get("verdict", "unknown")
        score = r.get("score", 0)
        emoji = verdict_emoji(verdict)

        lines += [
            f"---",
            f"### {emoji} `{r['file']}` — {r['content_type']}",
            f"",
            f"**Overall score:** `{score}/10` &nbsp; `{score_bar(score)}`  ",
            f"**Verdict:** `{verdict.upper()}`",
            f"",
            f"> {r.get('summary', '')}",
            f"",
            "#### Dimension Breakdown",
            "",
            "| Dimension | Score | Notes |",
            "|---|---|---|",
        ]

        dims = r.get("dimensions", {})
        for dim_key, label in [
            ("technical_accuracy", "Technical Accuracy"),
            ("code_quality",       "Code Quality"),
            ("clarity",            "Clarity"),
            ("structure",          "Structure"),
            ("completeness",       "Completeness"),
        ]:
            dim = dims.get(dim_key, {})
            s = dim.get("score", "—")
            n = dim.get("notes", "—")
            lines.append(f"| {label} | `{s}/10` | {n} |")

        lines.append("")

        if r.get("front_matter_issues"):
            lines.append("#### Front Matter Issues")
            for issue in r["front_matter_issues"]:
                lines.append(f"- {issue}")
            lines.append("")

        if r.get("required_changes"):
            lines.append("#### Required Changes")
            for change in r["required_changes"]:
                lines.append(f"- [ ] {change}")
            lines.append("")

        if r.get("suggestions"):
            lines.append("#### Suggestions (optional)")
            for sug in r["suggestions"]:
                lines.append(f"- {sug}")
            lines.append("")

    # Overall verdict summary
    verdicts = [r.get("verdict") for r in reviews]
    if all(v == "approved" for v in verdicts):
        lines += [
            "---",
            "### ✅ All files passed review — ready for maintainer approval.",
        ]
    elif any(v == "rejected" for v in verdicts):
        lines += [
            "---",
            "### ❌ One or more files were rejected. Please address the required changes and push a new commit.",
        ]
    else:
        lines += [
            "---",
            "### ⚠️ Revisions requested. Please address the required changes above and push a new commit.",
        ]

    return "\n".join(lines)


def post_comment(comment: str) -> None:
    """Post the review comment to the PR via the GitHub CLI."""
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        print("PR_NUMBER not set — printing review to stdout instead.\n")
        print(comment)
        return

    subprocess.run(
        ["gh", "pr", "comment", pr_number, "--body", comment],
        check=True,
    )
    print(f"Posted review comment to PR #{pr_number}")


def label_pr(reviews: list[dict]) -> None:
    """Apply a GitHub label based on the overall verdict."""
    pr_number = os.environ.get("PR_NUMBER")
    if not pr_number:
        return

    verdicts = [r.get("verdict") for r in reviews]
    if all(v == "approved" for v in verdicts):
        label = "ai-approved"
    elif any(v == "rejected" for v in verdicts):
        label = "ai-rejected"
    else:
        label = "needs-revision"

    subprocess.run(
        ["gh", "pr", "edit", pr_number, "--add-label", label],
        check=False,  # label may not exist yet; non-fatal
    )


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    files = get_changed_content_files()
    if not files:
        print("No content files changed — skipping review.")
        return

    print(f"Reviewing {len(files)} file(s): {[str(f) for f in files]}")

    reviews = []
    for f in files:
        print(f"  → Reviewing {f} ...")
        try:
            result = review_file(client, f)
            reviews.append(result)
            print(f"     Score: {result['score']}/10  Verdict: {result['verdict']}")
        except Exception as exc:
            print(f"     ERROR reviewing {f}: {exc}", file=sys.stderr)
            reviews.append({
                "file": str(f),
                "content_type": "Unknown",
                "score": 0,
                "verdict": "error",
                "summary": f"Review failed with error: {exc}",
                "dimensions": {},
                "required_changes": [],
                "suggestions": [],
                "front_matter_issues": [],
            })

    comment = format_comment(reviews)
    post_comment(comment)
    label_pr(reviews)

    # Exit 1 if any file was rejected so the CI check fails visibly
    if any(r.get("verdict") == "rejected" for r in reviews):
        sys.exit(1)


if __name__ == "__main__":
    main()

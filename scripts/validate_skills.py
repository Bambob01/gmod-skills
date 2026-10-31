#!/usr/bin/env python3
"""Checks every skills/<name>/SKILL.md for a valid Agent Skills frontmatter.

Runs automatically on every pull request. Run it yourself with:
    pip install pyyaml
    python3 scripts/validate_skills.py

Rules (from the Agent Skills format used by Claude and other agents):
  - SKILL.md starts with YAML frontmatter between two '---' lines
  - name: 1-64 chars, lowercase letters, numbers and hyphens only,
    no leading/trailing or double hyphens, must match the folder name,
    must not contain "anthropic" or "claude"
  - description: present, non-empty, at most 1024 characters
  - no XML/HTML tags in name or description
  - the markdown body after the frontmatter is not empty
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is missing. Install it with: pip install pyyaml")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
README = ROOT / "README.md"

SKIP = {"_template"}
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
RESERVED = ("anthropic", "claude")
TAG_RE = re.compile(r"<[^>]+>")
MAX_DESCRIPTION = 1024
RECOMMENDED_MAX_LINES = 500


def split_frontmatter(text: str):
    """Return (frontmatter_text, body) or raise ValueError."""
    text = text.lstrip("﻿")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file must start with a '---' line (YAML frontmatter)")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    raise ValueError("frontmatter is not closed with a second '---' line")


def check_skill(folder: Path, readme_text: str):
    errors, warnings = [], []
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        return [f"missing SKILL.md (expected {skill_md.relative_to(ROOT)})"], warnings

    text = skill_md.read_text(encoding="utf-8")
    try:
        fm_text, body = split_frontmatter(text)
    except ValueError as e:
        return [str(e)], warnings

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        return [f"frontmatter is not valid YAML: {e}"], warnings
    if not isinstance(fm, dict):
        return ["frontmatter must be a set of 'key: value' lines"], warnings

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("'name' is missing or empty")
    else:
        if not NAME_RE.match(name):
            errors.append(
                f"name '{name}' must be 1-64 characters of lowercase letters, numbers and hyphens"
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append(f"name '{name}' must not start/end with a hyphen or contain '--'")
        for word in RESERVED:
            if word in name:
                errors.append(f"name '{name}' must not contain the reserved word '{word}'")
        if TAG_RE.search(name):
            errors.append("name must not contain XML/HTML tags")
        if name != folder.name:
            errors.append(f"name '{name}' must match the folder name '{folder.name}'")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("'description' is missing or empty")
    else:
        if len(desc) > MAX_DESCRIPTION:
            errors.append(
                f"description is {len(desc)} characters; the limit is {MAX_DESCRIPTION}"
            )
        if TAG_RE.search(desc):
            errors.append("description must not contain XML/HTML tags like <this>")
        if "use when" not in desc.lower() and "use this" not in desc.lower():
            warnings.append("description should say when to use the skill (e.g. 'Use when ...')")

    if not body.strip():
        errors.append("the instructions after the frontmatter are empty")
    else:
        n = len(body.splitlines())
        if n > RECOMMENDED_MAX_LINES:
            warnings.append(
                f"body is {n} lines; consider moving detail into extra .md files in the folder"
            )

    if readme_text and f"skills/{folder.name}" not in readme_text:
        warnings.append("not listed in the README skills table yet")

    return errors, warnings


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print("No skills/ folder found.")
        return 1

    readme_text = README.read_text(encoding="utf-8") if README.is_file() else ""
    folders = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and p.name not in SKIP)
    if not folders:
        print("No skills found in skills/.")
        return 1

    failed = 0
    for folder in folders:
        errors, warnings = check_skill(folder, readme_text)
        rel = folder.relative_to(ROOT)
        if errors:
            failed += 1
            print(f"FAIL  {rel}")
            for e in errors:
                print(f"        - {e}")
        else:
            print(f"ok    {rel}")
        for w in warnings:
            print(f"        warning: {w}")

    print()
    if failed:
        print(f"{failed} of {len(folders)} skill(s) have problems. See CONTRIBUTING.md for the rules.")
        return 1
    print(f"All {len(folders)} skills look good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Quick validation script for skills - validates SKILL.md format and structure

Usage:
    python scripts/quick_validate.py <skill_directory>
    python scripts/quick_validate.py skills/  # validates all skills in directory
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Validate compatibility field if present (optional)
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    return True, "Skill is valid!"


def validate_all_skills(skills_dir):
    """Validate all skills in a directory"""
    skills_dir = Path(skills_dir)
    if not skills_dir.exists():
        print(f"❌ Directory not found: {skills_dir}")
        return False

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

    if not skill_dirs:
        print(f"⚠️  No skills found in {skills_dir}")
        return True

    all_valid = True
    for skill_dir in sorted(skill_dirs):
        valid, message = validate_skill(skill_dir)
        status = "✅" if valid else "❌"
        print(f"{status} {skill_dir.name}: {message}")
        if not valid:
            all_valid = False

    return all_valid


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/quick_validate.py <skill_directory>")
        print("       python scripts/quick_validate.py skills/  # validates all skills")
        sys.exit(1)

    target = sys.argv[1]
    target_path = Path(target)

    if target_path.is_dir() and (target_path / "SKILL.md").exists():
        # Single skill validation
        valid, message = validate_skill(target)
        print(message)
        sys.exit(0 if valid else 1)
    elif target_path.is_dir():
        # Directory with multiple skills
        all_valid = validate_all_skills(target)
        sys.exit(0 if all_valid else 1)
    else:
        print(f"❌ Path not found: {target}")
        sys.exit(1)

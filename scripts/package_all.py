#!/usr/bin/env python3
"""
Package all skills in the skills directory

Usage:
    python scripts/package_all.py
    python scripts/package_all.py --output ./dist
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.package_skill import package_skill


def main():
    parser = argparse.ArgumentParser(description="Package all skills")
    parser.add_argument("--output", "-o", default="./dist", help="Output directory for .skill files")
    parser.add_argument("--skills-dir", default="./skills", help="Directory containing skills")
    args = parser.parse_args()

    skills_dir = Path(args.skills_dir)
    output_dir = Path(args.output)

    if not skills_dir.exists():
        print(f"❌ Skills directory not found: {skills_dir}")
        return 1

    # Find all skill directories
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

    if not skill_dirs:
        print(f"⚠️  No skills found in {skills_dir}")
        return 0

    print(f"📦 Found {len(skill_dirs)} skill(s) to package\n")

    success_count = 0
    for skill_dir in sorted(skill_dirs):
        print(f"{'=' * 50}")
        result = package_skill(skill_dir, output_dir)
        if result:
            success_count += 1
        print()

    print(f"{'=' * 50}")
    print(f"📊 Summary: {success_count}/{len(skill_dirs)} skills packaged successfully")

    return 0 if success_count == len(skill_dirs) else 1


if __name__ == "__main__":
    exit(main())

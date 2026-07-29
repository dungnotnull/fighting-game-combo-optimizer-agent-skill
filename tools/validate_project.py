"""
validate_project.py — Skill 253: fighting-game-combo-optimizer
Production-grade validator for the 8-File Contract. Verifies required files,
frontmatter, sections, and project structure compliance with SKILL-STANDARD.md.
Exits with code 0 on pass, non-zero on failures.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

checks_passed = 0
checks_failed = 0
failures = []

def ok(label, detail=""):
    global checks_passed
    checks_passed += 1

def fail(label, detail=""):
    global checks_failed
    checks_failed += 1
    failures.append(f"{label}: {detail}")

def require(cond, label, detail=""):
    (ok if cond else fail)(label, detail)

def read(p):
    return Path(p).read_text(encoding="utf-8") if Path(p).exists() else ""

# ---- 1. 8-File Contract: required files ----
REQUIRED_FILES = [
    "CLAUDE.md",
    "PROJECT-detail.md",
    "PROJECT-DEVELOPMENT-PHASE-TRACKING.md",
    "README.md",
    "SECOND-KNOWLEDGE-BRAIN.md",
    "skills/main.md",
    "tools/knowledge_updater.py",
    "tools/test_knowledge_updater.py",
    "tools/run_test_scenarios.py",
    "tests/test-scenarios.md",
    "tests/TEST_RESULTS.md",
    "requirements.txt",
    ".gitignore"
]

for f in REQUIRED_FILES:
    require((ROOT / f).exists(), f"required file present: {f}")

# ---- 2. skills/*.md frontmatter check ----
FM_PATTERN = re.compile(r"^---\s*\n(.*?\n)---", re.S)
skill_files = list(SKILLS.glob("*.md"))

for skill_file in skill_files:
    content = read(skill_file)
    m = FM_PATTERN.search(content)
    require(bool(m), f"{skill_file.name}: has frontmatter")
    if m:
        fm_content = m.group(1)
        require("name:" in fm_content, f"{skill_file.name}: frontmatter has 'name'")
        require("description:" in fm_content, f"{skill_file.name}: frontmatter has 'description'")

# ---- 3. skills/main.md Quality Gate table ----
main_content = read(ROOT / "skills/main.md")
require("Quality Gates" in main_content, "main.md: has Quality Gates section")
require("| Gate |" in main_content or "## Quality Gates" in main_content, "main.md: has quality gate table")
require("Graceful Degradation" in main_content or "degradation" in main_content.lower(), "main.md: has graceful degradation")

# ---- 4. knowledge_updater.py KNOWLEDGE_CONFIG ----
ku_content = read(ROOT / "tools/knowledge_updater.py")
require("KNOWLEDGE_CONFIG" in ku_content, "knowledge_updater.py: has KNOWLEDGE_CONFIG block")
require("sha256" in ku_content, "knowledge_updater.py: has SHA256 dedup")
require("score_entry" in ku_content, "knowledge_updater.py: has scoring function")

# ---- 5. PROJECT-detail.md sections ----
pd_content = read(ROOT / "PROJECT-detail.md")
require("## Executive Summary" in pd_content or "Executive Summary" in pd_content, "PROJECT-detail.md: has Executive Summary")
require("## Harness Architecture" in pd_content or "Harness Architecture" in pd_content, "PROJECT-detail.md: has Harness Architecture")
require("## Idea (Vietnamese)" in pd_content or "Idea (Vietnamese)" in pd_content, "PROJECT-detail.md: has Idea (Vietnamese)")

# ---- 6. README.md required sections ----
readme_content = read(ROOT / "README.md")
require("## Features" in readme_content or "Features" in readme_content, "README.md: has Features section")
require("## Installation" in readme_content or "Installation" in readme_content, "README.md: has Installation section")
require("## Usage" in readme_content or "Usage" in readme_content, "README.md: has Usage section")
require("## License" in readme_content or "License" in readme_content, "README.md: has License section")

# ---- 7. Sub-skills count ----
sub_skills = list(SKILLS.glob("sub-*.md"))
require(len(sub_skills) >= 5, f"sub-skills: at least 5 sub-skills present (found {len(sub_skills)})")

expected_subs = {"sub-gather-requirements", "sub-evidence-collector", "sub-core-analysis",
                 "sub-knowledge-updater", "sub-advisor"}
got_subs = {s.stem for s in sub_skills}
require(got_subs >= expected_subs, f"sub-skills: expected set present")

# ---- 8. SECOND-KNOWLEDGE-BRAIN.md structure ----
brain_content = read(ROOT / "SECOND-KNOWLEDGE-BRAIN.md")
require("## 1. Core Concepts" in brain_content or "## 1." in brain_content, "SECOND-KNOWLEDGE-BRAIN.md: has Section 1")
require("## 2. Key Research Papers" in brain_content or "## 2." in brain_content, "SECOND-KNOWLEDGE-BRAIN.md: has Section 2")
require("## 4. Authoritative Data Sources" in brain_content or "## 4." in brain_content, "SECOND-KNOWLEDGE-BRAIN.md: has Section 4")
require("## 6. Self-Update Protocol" in brain_content or "## 6." in brain_content, "SECOND-KNOWLEDGE-BRAIN.md: has Section 6")
require("## 7. Knowledge Update Log" in brain_content or "## 7." in brain_content, "SECOND-KNOWLEDGE-BRAIN.md: has Section 7")

# ---- 9. CLAUDE.md required sections ----
claude_content = read(ROOT / "CLAUDE.md")
require("## Skill Identity" in claude_content or "Skill Identity" in claude_content, "CLAUDE.md: has Skill Identity")
require("## Sub-Skills" in claude_content or "Sub-Skills" in claude_content, "CLAUDE.md: has Sub-Skills table")
require("## Knowledge Sources" in claude_content or "Knowledge Sources" in claude_content, "CLAUDE.md: has Knowledge Sources")

# ---- 10. TEST_RESULTS.md exists ----
require((ROOT / "tests/TEST_RESULTS.md").exists(), "tests/TEST_RESULTS.md: exists")

# ---- Report ----
total = checks_passed + checks_failed
print(f"[validate_project] {checks_passed}/{total} checks passed")

if failures:
    print("\n[FAILURES]")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("[OK] all checks passed — 8-File Contract satisfied")
    sys.exit(0)

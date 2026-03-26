---
name: sync-context
description: Sync project context to CLAUDE.md + .claude/rules/ using the WHAT-WHY-HOW progressive disclosure pattern
---

# Sync Context Command

Analyzes the codebase and updates `CLAUDE.md` (root) + `.claude/rules/*.md` (scoped rules) following the progressive disclosure pattern.

## Usage

```bash
/sync-context                    # Full analysis and update
/sync-context --section rules    # Update only rules files
/sync-context --section root     # Update only root CLAUDE.md
/sync-context --dry-run          # Preview changes without saving
/sync-context --audit            # Check health: line count, rule coverage, stale content
```

---

## Architecture: Progressive Disclosure Pattern

The pattern splits project context across two tiers:

### Tier 1: Root CLAUDE.md (loaded EVERY session)

**Target: < 150 lines.** Only content that applies to ALL tasks.

Uses the WHAT-WHY-HOW framework:

| Section | Purpose | Update Mode |
|---------|---------|-------------|
| WHAT — Project Context | One-liner orientation + core mission | Preserve |
| WHAT — Stack | Technology table (language, frameworks, infra) | Replace |
| WHAT — Project Map | Directory tree with purpose annotations | Replace |
| WHY — Key Decisions | Architecture choices Claude would get wrong without | Preserve |
| HOW — Commands | Build, test, lint, deploy commands | Replace |
| HOW — Verification | Always-run verification command after changes | Preserve |
| HOW — Configuration | Pointer to configs/ with @imports | Replace |
| Scoped Rules Table | Index of .claude/rules/ with scope + content summary | Replace |
| Active Work | Current features in progress | Preserve |

### Tier 2: .claude/rules/*.md (loaded ONLY when working in matching paths)

Each rule file has YAML frontmatter with `paths:` globs. Claude loads them on-demand.

---

## Analysis Process

### Step 1: Audit Current State

```text
Read("CLAUDE.md")                           # Count lines, check structure
Glob(".claude/rules/*.md")                  # List existing rules
```

Flag issues:
- Root CLAUDE.md > 150 lines -> WARN: "too long, move content to rules"
- Root CLAUDE.md > 300 lines -> ERROR: "Claude will ignore instructions"
- Rules without paths: frontmatter -> WARN: "loads unconditionally"
- Content in root that only applies to specific paths -> WARN: "move to rules"

### Step 2: Scan for WHAT (Stack + Structure)

```text
Read("pyproject.toml")                      # Python version, dependencies
Glob("src/**/__init__.py")                  # Package structure
Glob("functions/*/template.yaml")           # Lambda functions
Glob("pipelines/**/*.yml")                  # Pipeline definitions
Glob("configs/*")                           # Config files
ls scripts/                                 # Available scripts
```

Generate: Stack table, Project Map tree

### Step 3: Scan for HOW (Commands)

```text
Read("pyproject.toml")                      # scripts section
Read("Makefile") if exists                  # make targets
Grep("^pytest", "pyproject.toml")           # test config
Glob("scripts/*.sh")                        # Shell scripts
Read("scripts/preflight-validate.sh")       # Pre-flight gates
```

Generate: Commands section, Verification section

### Step 4: Scan for Rules Content

```text
# Code patterns (-> code-quality.md)
Grep("@dataclass", "src/**/*.py")
Grep("mask_pii", "src/**/*.py")
Grep("Decimal", "src/**/*.py")

# Architecture (-> architecture.md)
Grep("from src", "src/**/*.py")             # Import structure
Read("scripts/build-copy-src.sh")           # Build pipeline

# Domain (-> domain.md, lakeflow.md)
Glob("reference/specs/*")                   # Domain specs
Glob("pipelines/src/**/*.sql")              # DLT notebooks

# Testing (-> testing.md)
Grep("def test_", "tests/**/*.py", count)   # Test count
Read("pyproject.toml")                      # Coverage config

# Config (-> configs.md)
Read("configs/aws-env.sh.example")          # AWS variables
Read("configs/databricks-env.sh.example")   # Databricks variables
```

### Step 5: Scan for Scoped Rules Index

```text
Glob(".claude/rules/*.md")                  # All rule files
# For each: extract name, paths, and description from YAML frontmatter
```

Generate: Scoped Rules Table in root CLAUDE.md

### Step 6: Apply Updates

For root CLAUDE.md:
- **Replace** sections: Stack, Project Map, Commands, Configuration, Scoped Rules Table
- **Preserve** sections: Project Context, Key Decisions, Verification, Active Work
- **Delete** sections that belong in rules (env var tables, agent tables, etc.)

For .claude/rules/*.md:
- **Update** content from scans
- **Preserve** YAML frontmatter paths (unless structure changed)
- **Create** new rule files if new domains detected

---

## The Include/Exclude Principle

For EVERY line in CLAUDE.md, ask: "Would removing this cause Claude to make mistakes?"

| Include in Root | Exclude from Root (move to rules or delete) |
|----------------|----------------------------------------------|
| Commands Claude can't guess | Anything Claude discovers by reading code |
| Architecture decisions that differ from defaults | Standard language conventions |
| Verification steps | Detailed API docs (link instead) |
| Common gotchas | File-by-file codebase descriptions |
| Config pointers (@imports) | Full env var tables |
| Active work context | Agent/command catalogs (auto-discovered) |

## Token Budget Check

After generating, verify:
- Root CLAUDE.md: count lines. MUST be < 150, WARN if > 100
- Each rule file: count lines. WARN if > 50 per file
- Total instruction count (root + average rules loaded): MUST be < 150

---

## YAML Frontmatter Template for Rules

```yaml
---
description: One-line description of what this rule covers
paths:
  - "src/core/parsers/**"
  - "tests/integration/**"
---
```

Rules WITHOUT `paths:` load unconditionally (same as putting content in root CLAUDE.md).

---

## Reusable Template (for new projects)

When running on a project WITHOUT an existing CLAUDE.md, generate this skeleton:

```markdown
# {Project Name}

## WHAT — Project Context
{One paragraph: what it does and why it exists}

## WHAT — Stack
| Layer | Technology |
|-------|-----------|
| Language | {detected} |
| Framework | {detected} |
| Testing | {detected} |
| Deployment | {detected} |

## WHAT — Project Map
{Auto-generated directory tree with annotations}

## WHY — Key Decisions
- {Non-obvious architectural choice #1}
- {Non-obvious architectural choice #2}

## HOW — Commands
{Build, test, lint, deploy commands}

## HOW — Verification
IMPORTANT: Always run after changes:
{single verification command}

## HOW — Configuration
{Pointer to config files with @imports}

## Scoped Rules
| Rule File | Scope | Content |
|-----------|-------|---------|
| {auto-generated from .claude/rules/} |

## Active Work
| Feature | Phase | Artifacts |
|---------|-------|-----------|
```

---

## Output

```text
SYNC CONTEXT
━━━━━━━━━━━━

Analyzing codebase...
✓ Scanned project structure
✓ Detected stack: Python 3.12, pytest, SAM, Databricks
✓ Found 6 rule files in .claude/rules/

Health check:
✓ CLAUDE.md: 105 lines (target: < 150) ✅
✓ Rules: 6 files, avg 35 lines each ✅
✓ Token budget: ~95 instructions (limit: 150) ✅
⚠ No verification section found → ADDED

Section updates:
• WHAT — Stack: REPLACED (dependency changes detected)
• WHAT — Project Map: REPLACED (new directories found)
• HOW — Commands: REPLACED (new scripts found)
• Scoped Rules Table: REPLACED (1 new rule file)
• WHY — Key Decisions: PRESERVED
• Active Work: PRESERVED

━━━━━━━━━━━━
CLAUDE.md + .claude/rules/ updated successfully
```

---

## Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without saving |
| `--section root` | Update only root CLAUDE.md |
| `--section rules` | Update only .claude/rules/ files |
| `--audit` | Health check: line counts, coverage, staleness |
| `--force` | Replace all sections (ignores preserve rules) |
| `--template` | Generate fresh skeleton for new project |

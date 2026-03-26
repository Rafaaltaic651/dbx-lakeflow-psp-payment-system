---
name: memory
description: Save valuable insights from the current session to storage
---

# Memory Command

Save session insights to `.claude/storage/` with **daily accumulation** - multiple sessions append to the same daily file.

## Usage

```bash
/memory                           # Save current session insights
/memory "specific note to save"   # Save with specific context
/memory --summary                 # View today's accumulated memories
```

---

## Daily Accumulation Logic

```text
┌─────────────────────────────────────────────────────────────────┐
│  memory-2026-02-02.md                                           │
├─────────────────────────────────────────────────────────────────┤
│  # Daily Memory: 2026-02-02                                     │
│  > 3 sessions captured                                          │
│                                                                 │
│  ## Daily Summary                                               │
│  - [09:15] Parser validation setup                              │
│  - [14:30] Field position fixes                                 │
│  - [16:45] Claude Code 100% configuration                       │
│                                                                 │
│  ---                                                            │
│                                                                 │
│  ## Session 1 - 09:15                                           │
│  > {session content}                                            │
│                                                                 │
│  ---                                                            │
│                                                                 │
│  ## Session 2 - 14:30                                           │
│  > {session content}                                            │
│                                                                 │
│  ---                                                            │
│                                                                 │
│  ## Session 3 - 16:45                                           │
│  > {session content}                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Process

When invoked:

```text
1. Check if .claude/storage/memory-{YYYY-MM-DD}.md exists:

   IF EXISTS:
     - Read existing file
     - Count existing sessions (## Session N pattern)
     - Increment session counter
     - Append new session section
     - Update Daily Summary with new entry

   IF NOT EXISTS:
     - Create new file with header
     - Start with Session 1

2. Scan current conversation for:
   - Decisions (look for "decided", "chose", "will use")
   - Patterns (look for reusable solutions)
   - Gotchas (look for "gotcha", "watch out", "careful")
   - Open items (look for "TODO", "later", "next time")
   - Files modified (extract from tool calls)

3. Compress to session block:
   - Max 5 decisions per session
   - Max 3 patterns per session
   - Max 3 gotchas per session
   - Include file list if significant changes

4. Write/Append to storage file
```

---

## Output Format

**New File (First Session of Day):**

```markdown
# Daily Memory: {YYYY-MM-DD}

> 1 session captured

## Daily Summary

| Time | Focus | Key Outcome |
|------|-------|-------------|
| {HH:MM} | {brief description} | {main result} |

---

## Session 1 - {HH:MM}

> {One-line summary}

### Decisions
| Decision | Rationale |
|----------|-----------|
| {what} | {why} |

### Patterns
- {pattern}: {application}

### Gotchas
- {gotcha}: {avoidance}

### Files Changed
- `{path}` - {what changed}

---
*Session saved: {timestamp}*
```

**Append (Subsequent Sessions):**

```markdown
---

## Session {N} - {HH:MM}

> {One-line summary}

### Decisions
| Decision | Rationale |
|----------|-----------|
| {what} | {why} |

### Patterns
- {pattern}: {application}

### Gotchas
- {gotcha}: {avoidance}

### Files Changed
- `{path}` - {what changed}

---
*Session saved: {timestamp}*
```

Also update the **Daily Summary** table at the top with the new session entry.

---

## Implementation Steps

```python
# Pseudocode for memory accumulation

def save_memory(context: str = None):
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M")
    storage_path = f".claude/storage/memory-{today}.md"

    # Scan conversation for insights
    insights = extract_insights(conversation)

    if file_exists(storage_path):
        # APPEND mode
        content = read_file(storage_path)
        session_num = count_sessions(content) + 1

        # Update daily summary
        content = update_daily_summary(content, time_now, context)

        # Append new session
        content += format_session(session_num, time_now, insights)

        # Update session count in header
        content = update_session_count(content, session_num)
    else:
        # CREATE mode
        content = create_daily_header(today)
        content += format_daily_summary(time_now, context)
        content += format_session(1, time_now, insights)

    write_file(storage_path, content)
    return f"Saved to {storage_path} (Session {session_num})"
```

---

## When to Use

**Good times to invoke /memory:**

- ✅ After completing a significant task
- ✅ When you've discovered something non-obvious
- ✅ Before ending a work session
- ✅ After fixing a tricky bug
- ✅ When making architecture decisions

**The command handles accumulation** - you don't need to worry about overwriting. Each invocation adds a new session block.

---

## Example: Multi-Session Day

```text
User: /memory "Completed data validation"

→ Checking .claude/storage/memory-2026-02-02.md...
→ Found 2 existing sessions
→ Scanning conversation...
→ Found: 3 decisions, 2 patterns, 1 gotcha

✅ Appended Session 3 to memory-2026-02-02.md

## Daily Summary (Updated)
| Time | Focus | Key Outcome |
|------|-------|-------------|
| 09:15 | Parser setup | Initial structure |
| 14:30 | Field fixes | Positions corrected |
| 16:45 | Data validation | All parsers verified |  ← NEW

## Session 3 - 16:45
> Completed data validation - all file types verified

### Decisions
| Decision | Rationale |
|----------|-----------|
| Field [567:579] for cash_back | Verified against source spec |
| Entity needs 6 prefixes | Added mapping to PREFIX_MAP |

### Patterns
- UUID-based context tracking for parsing
- Generator parsing for memory efficiency

### Gotchas
- Some formats have DUAL sign handling - don't assume single method
```

---

## Tips

| Do | Don't |
| -- | ----- |
| Run at natural breakpoints | Run after every message |
| Include context parameter | Leave summaries vague |
| Let it accumulate all day | Create multiple daily files |
| Review daily summary for gaps | Duplicate obvious info |

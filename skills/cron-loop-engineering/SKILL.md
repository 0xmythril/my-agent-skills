---
name: cron-loop-engineering
description: "Patterns and infrastructure for building self-improving, cross-run-state cron jobs and scheduled automation loops. Includes autonomous self-monitoring cron patterns."
category: devops
---

# Cron Loop Engineering

Patterns for building robust, scheduled automation loops with **cross-run state**, **change detection**, **intelligent alerting**, and **self-improvement**.

## Core Concepts

### 1. Self-Improving Cron Jobs

A cron loop that remembers what it learned across runs:

```python
# Cross-run state tracking
STATE_FILE = Path.home() / ".cron-state/my_job.json"

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run": None, "success_count": 0, "error_pattern": None}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def run():
    state = load_state()
    # Use previous error patterns to adjust behavior
    if state.get("error_pattern") == "rate_limit":
        time.sleep(60)  # Back off
    try:
        result = do_work()
        state["success_count"] += 1
        state["error_pattern"] = None
    except Exception as e:
        state["error_pattern"] = classify_error(e)
    state["last_run"] = datetime.now().isoformat()
    save_state(state)
```

### 2. Change Detection

Compare extracted data against stored hashes. Only act when something actually changed.

### 3. Intelligent Alerting

Build digests rather than spam:

```python
def should_alert(changes, state):
    if not changes:
        return False
    if len(changes) > 10:
        return f"{len(changes)} changes detected — sending digest"
    return True
```

### 4. State Machine Patterns

```
[Initialize] → [Fetch] → [Extract] → [Compare] → [Decide] → [Act] → [Store] → [Sleep]
     ↑                                                                |
     └────────────────────────────────────────────────────────────────┘
```

## The Four Pillars

1. **Reliability** — retries, timeouts, idempotency
2. **Observability** — logs, metrics, state snapshots
3. **Intelligence** — pattern matching, threshold tuning, noise filtering
4. **Adaptation** — learning from failures, adjusting check intervals

## Common Patterns

### Exponential Backoff for Unreliable Sources

```python
RETRY_DELAYS = [30, 60, 300, 900]  # seconds

def fetch_with_backoff(url, state):
    for attempt, delay in enumerate(RETRY_DELAYS):
        try:
            return requests.get(url, timeout=30)
        except Exception:
            if attempt < len(RETRY_DELAYS) - 1:
                time.sleep(delay)
    state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
    return None
```

### Graceful Degradation

When full extraction fails, fall back to simpler checks:

```python
def check_website(url):
    try:
        return parse_rich_content(url)
    except Exception:
        return check_status_code_only(url)  # Still useful
```

### Frequency Adaptation

```python
def adaptive_interval(state):
    if state["consecutive_failures"] > 5:
        return "6h"  # Slow down
    if state["changes_detected"] > 10:
        return "5m"   # Speed up
    return "1h"
```

## State Helper Utilities

Store state in JSON files with atomic writes. Track:
- Timestamps (`last_run`, `last_changed`)
- Counters (`success_count`, `change_count`, `consecutive_failures`)
- Error fingerprints for classification and backoff
- Rolling history arrays (trimmed to N most recent)

## Reproducible Build Patterns

For cron jobs that need to set up an environment before each run, use the digest-based reproducible pattern:
1. Write a `digest.json` with pinned versions of dependencies
2. Compare current environment against digest
3. If mismatch, apply changes and re-verify
4. Log what changed for debugging

See `references/digest-implementation-pattern.md` for a full worked example.

## Integration with Other Skills

- **`web-content-monitoring`** — use for content change detection patterns
- Replace polling with push/webhook events where possible
- Combine with calendar/ticket parsing when monitoring event-driven sources

## Full Example: Smart Website Monitor

```python
#!/usr/bin/env python3
import json, hashlib, requests, time
from pathlib import Path
from datetime import datetime

STATE_PATH = Path.home() / ".cron-state/smart_monitor.json"

def main():
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    last_hash = state.get("last_hash")
    response = requests.get("https://example.com", timeout=30)
    current_hash = hashlib.sha256(response.text.encode()).hexdigest()[:16]
    
    if current_hash != last_hash:
        state["last_hash"] = current_hash
        state["last_changed"] = datetime.now().isoformat()
        state["change_count"] = state.get("change_count", 0) + 1
        print(f"CHANGED: hash={current_hash}")
    else:
        state["no_change_count"] = state.get("no_change_count", 0) + 1
    
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))

if __name__ == "__main__":
    main()
```

## Pitfalls

### Timezone-Naive vs Aware Datetime Subtraction

Cron jobs often compare `datetime.now(tz)` against ISO timestamps stored in JSON state or fetched from APIs. Python raises `TypeError: can't subtract offset-naive and offset-aware datetimes` when mixing the two.

Always normalize before subtraction or comparison:

```python
from datetime import datetime, timezone, timedelta
hkt = timezone(timedelta(hours=8))
now = datetime.now(hkt)

created = datetime.fromisoformat(todo["created"])  # may be naive
created_hkt = (
    created.replace(tzinfo=hkt)
    if created.tzinfo is None
    else created.astimezone(hkt)
)
age_days = (now - created_hkt).days
```

### Inspect External JSON Schemas Before Assumption

Different sources may use `"created"`, `"created_at"`, or `"completed_at"`. Before computing staleness, read a sample of the actual JSON rather than assuming field names.

**Resilient accessor pattern** — use `dict.get()` with fallback chains rather than direct key access:

```python
title      = t.get("content") or t.get("title", "(no title)")
created    = t.get("created_at") or t.get("created", "")
due        = t.get("due") or t.get("due_date") or t.get("due_at")
duration   = t.get("estimated_duration", 30)  # minutes
source_tag = t.get("source", "")                # provenance tag
```

### Same-Day Re-Run Inflation of Rolling Averages

When debugging or iteratively refining a cron job, multiple runs in the same calendar day append duplicate entries to rolling history arrays. Fix: track `run_dates` and replace the last history entry when re-running on the same day:

```python
today_str = datetime.now().strftime("%Y%m%d")
old_hist = state.get("calendar_history", [])
if state.get("run_dates", [])[-1:] == [today_str]:
    old_hist = old_hist[:-1]  # pop today's earlier run
state["calendar_history"] = old_hist[-6:] + [today_count]
state["run_dates"] = state.get("run_dates", [])[-6:] + [today_str]
```

## Key Principles

1. **Cross-run state**: Always stateful. Jobs remember past decisions.
2. **State machines**: Explicit flow control beats nested `if` trees.
3. **Change detection**: Hash/diff before action. Avoid false positives.
4. **Intelligent alerting**: Digest, batch, and filter notifications.
5. **Self-monitoring**: Job tracks own health metrics (success rate, latency).
6. **Reproducible builds**: Pinned environments prevent "works on my machine".
7. **Adaptation**: Check intervals adjust to observed change velocity.

## References

- `references/digest-implementation-pattern.md` — reproducible build digests
- `references/streaming-ics-parser.md` — streaming ICS calendar parsing (large files)
- `scripts/state_helper.py` — utility module for cron state management

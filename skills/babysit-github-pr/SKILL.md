---
name: babysit-github-pr
version: 1.0.0
description: >-
  Monitor a GitHub PR in a polling loop, post visible status updates, and auto-fix
  actionable review or bot comments until the PR is mergeable, the time budget is
  exhausted, or progress stalls. Use when the user asks to babysit, monitor, triage,
  or keep a GitHub pull request merge-ready.
metadata:
  hermes:
    tags: [github, pull-request, ci, gh-cli, code-review]
    category: devops
    requires_toolsets: [terminal]
---

# Babysit a GitHub PR

Monitor a GitHub PR in a polling loop. Post visible status updates each cycle, and auto-fix actionable review/bot comments until the PR is mergeable, the time budget is exhausted, or progress stalls.

## Parse inputs from the user's message

Expected format (defaults in brackets):

- `pr_url` (required) — full GitHub PR URL
- `duration` [2h] — total wall-clock time budget
- `interval` [10m] — poll cadence between cycles
- `stop_after_unresolved_runs` [2] — consecutive cycles with unresolved comments AND no progress before halting
- `allow_force_push` [false]

If `pr_url` is missing, stop and ask the user for it.

## Prerequisites — check before starting

- `gh` CLI authenticated (`gh auth status`)
- PR branch checked out (`gh pr checkout <number>` if not)
- Working tree clean — if not, stop and tell the user

## Each cycle

Run every `interval`, up to `duration`.

### 1. Fetch state

```bash
gh pr view <pr_url> --json number,headRefName,mergeable,mergeStateStatus,statusCheckRollup,reviewDecision,state
gh pr view <pr_url> --json reviewThreads,comments
```

Identify: mergeability, CI status (and failing check names), unresolved review threads, new bot comments (Bugbot, CodeRabbit, Greptile) since last cycle.

### 2. Post status update as a new PR comment

```text
🤖 [babysit HH:MM UTC] — cycle N/M

• Mergeable: <yes | no | conflicting>
• CI: <green | red | pending> (<failing checks>)
• Unresolved comments: <count>
• Last action: <"fixed X and pushed <sha>" | "no actionable items" | "waiting on CI">
```

Always use the `🤖 [babysit ` prefix so prior babysit comments can be found.

### 3. Act on actionable comments

Classify each unresolved item:

- **Actionable**: names a file/line and requests a change, identifies a bug, flags failing logic, or is a bot's must-fix severity output
- **Non-actionable**: nits (`nit:`, `optional:`), questions, praise, human discussion threads, bot summaries/walkthroughs

For actionable items in this cycle:

1. Apply all fixes locally.
2. Commit as exactly ONE commit per cycle:

   ```bash
   git add -A
   git commit -m "address review feedback (babysit cycle N)

   - <fix 1>
   - <fix 2>"
   ```

3. Push. Never use `--force` unless `allow_force_push=true`:

   ```bash
   git push origin <headRefName>
   ```

4. Reply to each addressed thread: `Addressed in <sha>. <one-line explanation>.`
5. Do not resolve threads programmatically — leave that to the reviewer.

If CI is failing for unrelated reasons (flaky test, lint, build), fix in the same single commit.

### 4. Track between cycles

Keep in memory:

- `cycle_count`
- `start_time`
- `consecutive_unresolved_runs` — increment when cycle ends with unresolved comments AND no commit pushed; reset to 0 on commit or resolution

### 5. Stop conditions

Evaluate in priority order:

| Condition | Action |
| --- | --- |
| PR merged/closed | Post final summary, exit |
| Mergeable + CI green + 0 unresolved | Post final summary, exit |
| `consecutive_unresolved_runs >= stop_after_unresolved_runs` | Post final summary, exit |
| Elapsed >= `duration` | Post final summary, exit |
| Merge conflicts needing human judgment | Post final summary, exit |
| Otherwise | Sleep `interval`, continue |

## Final summary comment

Post with a distinct prefix:

```markdown
✅ [babysit final] — stopped after N cycles (<reason>)

**Commits pushed:**
- <sha>: <description>

**Threads addressed:**
- <link>: <fix summary>

**Remaining blockers:**
- <CI / unresolved / conflicts>

**Recommended next action:**
<one sentence>
```

## Rules

- **One commit per cycle.** Multiple fixes batch into one commit; multiple cycles produce multiple commits. Never amend or rebase across cycles.
- **Never force-push** unless explicitly allowed.
- **Don't resolve threads you didn't fix.** Reply, don't dismiss.
- **Skip non-actionable comments** — note in final summary.
- **Don't double-fix.** Before applying, check prior `🤖 [babysit ...]` comments in this session.
- **Dirty working tree at cycle start** → halt with status comment, don't risk committing unrelated changes.
- **Auth or push failure** → halt with status comment showing the error.
- When in doubt about whether a comment is actionable, **lean non-actionable** and note it in the summary.

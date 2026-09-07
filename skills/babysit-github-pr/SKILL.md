---
name: babysit-github-pr
version: 2.0.0
description: >-
  Monitor a GitHub PR in a polling loop, post visible status updates, and auto-fix
  actionable review or bot comments until the PR is merge-ready, the time budget is
  exhausted, or progress stalls. Use when the user asks to babysit, monitor, triage,
  or keep a GitHub pull request merge-ready.
metadata:
  hermes:
    tags: [github, pull-request, ci, gh-cli, code-review]
    category: devops
    requires_toolsets: [terminal]
    related_skills: [promote-branch-pr]
---

# Babysit a GitHub PR

Monitor a GitHub PR in a polling loop. Post a visible status update each cycle, and auto-fix actionable review/bot comments until the PR is merge-ready, the time budget is exhausted, or progress stalls.

Defaults are inline below; values parsed from the user's message override them per run.

`review_bots` defaults to `Bugbot`, `CodeRabbit`, `Greptile`.

GitHub access is via the `gh` CLI and `git` in a terminal.

## Parse inputs from the user's message

Expected format (defaults in brackets):

- `pr_url` (required) — full GitHub PR URL
- `duration` [2h] — total wall-clock time budget
- `interval` [10m] — poll cadence between cycles
- `stop_after_unresolved_runs` [2] — consecutive cycles ending with unaddressed actionable feedback and no commit pushed before halting (precise definition in step 4)
- `allow_force_push` [false]

If `pr_url` is missing, stop and ask the user for it.

## Prerequisites — check before starting

- `gh` CLI authenticated (`gh auth status`)
- PR branch checked out (`gh pr checkout <number>` if not)
- Working tree clean — if not, stop and tell the user

## Each cycle

Run every `interval`, up to `duration`.

**Cycle guard — before step 1, every cycle:** re-check the working tree is clean (`git status --porcelain`). If it is dirty, halt with a status comment per the Rules — do not risk `git add -A` bundling unrelated changes into the cycle commit. (Prerequisites only check this once; the guard enforces it on each iteration.)

### 1. Fetch state

```bash
# PR state + CI rollup — valid `gh pr view` fields
gh pr view <pr_url> --json number,headRefName,mergeable,mergeStateStatus,statusCheckRollup,reviewDecision,state

# Unresolved review threads WITH stable IDs — `gh pr view` has NO `reviewThreads` field; use GraphQL.
# Capture thread `id` (needed to resolve it in step 3) and each comment `databaseId` (for seen_comment_ids).
gh api graphql -f query='query($owner:String!,$repo:String!,$number:Int!,$after:String){
  repository(owner:$owner,name:$repo){ pullRequest(number:$number){
    reviewThreads(first:100, after:$after){ pageInfo{ hasNextPage endCursor } nodes{ id isResolved path line
      comments(first:100){ pageInfo{ hasNextPage endCursor } nodes{ databaseId author{login} body } } } } } } }' \
  -F owner=<owner> -F repo=<repo> -F number=<number>
# Page every connection: repeat with -F after=<endCursor> while pageInfo.hasNextPage — for reviewThreads
# (>100 threads) and for a thread's comments (>100 comments). A bot finding is a thread's first comment.

# Bot review summaries, inline findings, and issue-level comments — each with its stable `.id`
gh api --paginate repos/<owner>/<repo>/pulls/<number>/reviews   --jq '.[] | {id, author: .user.login, state, body}'                                 # → seen_review_ids
gh api --paginate repos/<owner>/<repo>/pulls/<number>/comments  --jq '.[] | {id, author: .user.login, path, line: (.line // .original_line), body}' # → seen_comment_ids
gh api --paginate repos/<owner>/<repo>/issues/<number>/comments --jq '.[] | {id, author: .user.login, body}'                                        # → seen_issue_comment_ids
```

Identify: mergeability (judge merge-readiness from `mergeStateStatus`/`reviewDecision`, not `mergeable` alone — see the note under step 5), CI status (and failing check names), and new bot findings (from the `review_bots` list — e.g. Bugbot, CodeRabbit, Greptile) since last cycle — *new* meaning an ID not yet in `seen_review_ids`/`seen_comment_ids`/`seen_issue_comment_ids` (step 4). Bot/human feedback arrives on **three** surfaces, all of which count: unresolved inline review threads (the GraphQL query), review summaries (`pulls/reviews`), and issue-level PR comments (`issues/<number>/comments`). Don't treat a clean thread list as "no feedback" while an actionable issue-level bot comment is still open. On busy PRs, page through every surface — `--paginate` on the REST calls and `after:` cursors past the GraphQL `first:100` — so feedback beyond the first page still enters `seen_*` tracking.

### 2. Post status update as a new PR comment

```text
🤖 [babysit HH:MM UTC] — cycle N/M

• Mergeable: <yes | no | conflicting>
• CI: <green | red | pending> (<failing checks>)
• Unresolved comments: <count>
• Last action: <"fixed X and pushed <sha>" | "no actionable items" | "waiting on CI">
```

Always use the `🤖 [babysit ` prefix so prior babysit comments can be found.

Post this **after** step 3's actions complete (or immediately, if there are no actionable items this cycle), so `Last action` and any review-summary acknowledgments reflect what actually happened. The step numbers are a logical grouping, not a strict clock — within a cycle the order is fetch → act → post status.

### 3. Act on actionable comments

Classify each unresolved item:

- **Actionable**: names a file/line and requests a change, identifies a bug, flags failing logic, or is a bot's must-fix severity output
- **Non-actionable**: nits (`nit:`, `optional:`), questions, praise, human discussion threads, bot summaries/walkthroughs

Record every non-actionable item's ID in the matching `seen_*` set (step 4) and skip it — note it in the final summary. Otherwise the same skipped bot output looks "new" every cycle.

For actionable items in this cycle:

1. Apply all fixes locally.
2. Commit as exactly ONE commit per cycle:

   ```bash
   git add -A
   git commit -m "address review feedback (babysit cycle N)

   - <fix 1>
   - <fix 2>"
   ```

3. Push. Never use `--force` unless `allow_force_push` is true:

   ```bash
   git push origin <headRefName>
   ```

4. Acknowledge every addressed item on **all three surfaces** with `Addressed in <sha>. <one-line explanation>.` — reply in-thread for inline review threads; reply to the comment for issue-level bot comments; note review-summary findings in the status comment. Record each acknowledged ID in the matching `seen_*` set (step 4) so the merge-ready check counts it as addressed.
5. **Resolve each inline bot review thread you fully addressed** (reply first), using the thread `id` from step 1:

   ```bash
   gh api graphql -f query='mutation($t:ID!){ resolveReviewThread(input:{threadId:$t}){ thread{ isResolved } } }' -F t=<thread_id>
   ```

   Inline bot threads otherwise stay unresolved forever, so this is required to reach merge-ready when the repo enforces conversation resolution. (Issue-level comments and review summaries are not resolvable threads — addressing them means fix + acknowledge + record the ID.) **Never resolve** threads you did not address, human-discussion threads, or anything ambiguous — reply and leave those for a human.

**A failing required check is itself an actionable item** — even with no review comment. Diagnose it (`gh pr checks <pr_url>`, `gh run view <run-id> --log-failed`), fix the cause, and include the fix in this cycle's single commit + push. If it is not something the skill can fix (needs secrets, infra flake, an external service), treat it as a blocker: note it in the status comment and let the stall/`duration` budget apply rather than spinning indefinitely.

### 4. Track between cycles

Keep in memory:

- `cycle_count`
- `start_time`
- `consecutive_unresolved_runs` — increment when a cycle ends with **unaddressed actionable feedback or a failing required check** AND no commit pushed; reset to 0 whenever you push a fix. Items left open only because they await human resolution or a still-running check are progress, not a stall, and must not increment this. (This is what stops a red check with no fix path from spinning to `duration`.)
- `seen_review_ids` / `seen_comment_ids` / `seen_issue_comment_ids` — IDs already processed for each of the three feedback surfaces (review summaries, inline review comments, issue-level comments). Step 1 computes the new-findings delta against these; add every ID you **either addressed or classified non-actionable**, so neither is re-evaluated as "new" next cycle.
- `last_checked_at` — UTC timestamp of the previous cycle's fetch, used as a fallback "since last cycle" boundary when an item carries no stable ID.

### 5. Stop conditions

Evaluate in priority order:

| Condition | Action |
| --- | --- |
| PR merged/closed | Post final summary, exit |
| `mergeStateStatus` is `CLEAN`, `reviewDecision` is not `CHANGES_REQUESTED`, CI green, and no unaddressed actionable feedback on any of the three surfaces | Post final summary (merge-ready), **exit and tell the user the PR is ready for them to merge** |
| Blocked **only** by causes the skill cannot fix — required approvals, a human `CHANGES_REQUESTED` review, or branch-protection config — and no actionable feedback remains on any surface | Post final summary (needs human), exit |
| `consecutive_unresolved_runs >= stop_after_unresolved_runs` | Post final summary, exit |
| Elapsed >= `duration` | Post final summary, exit |
| Merge conflicts needing human judgment | Post final summary, exit |
| Otherwise | Sleep `interval`, continue |

`mergeable: MERGEABLE` only means there are **no merge conflicts** — it does not mean the PR is unblocked. Judge true merge-readiness from `mergeStateStatus` (`CLEAN` = ready; `BLOCKED` = required reviews/checks or branch protection unmet; `BEHIND` = needs update; `DIRTY` = conflicts) together with `reviewDecision`. Never post `✅ [babysit final]` as merge-ready while `mergeStateStatus` is anything but `CLEAN`. If the repo enforces **conversation resolution**, `mergeStateStatus` stays `BLOCKED` until every review thread is resolved — so resolving the bot threads you addressed (step 3.5) is what makes `CLEAN` reachable. A `BLOCKED` state with **fixable** causes — unresolved bot threads (resolve them) or failing CI (fix it) — is not a "needs human" exit; keep looping until those clear or the stall/`duration` budget applies.

## Agent autonomy boundary

- **Monitor**, **fix**, and **report** only.
- **Never merge** the PR — even if it is fully green and approved. Leave that decision to the user.
- **Never push to the target/base branch** directly — only to the PR head branch.

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
- **Resolve bot threads you fully addressed** (reply first, then `resolveReviewThread`) so the PR can reach merge-ready under required conversation resolution. **Never resolve** threads you didn't address or human-discussion threads — reply and leave those for a human.
- **Skip non-actionable comments** — note in final summary.
- **Don't double-fix.** Before applying, check prior `🤖 [babysit ...]` comments in this session.
- **Dirty working tree at cycle start** → halt with status comment, don't risk committing unrelated changes.
- **Auth or push failure** → halt with status comment showing the error.
- When in doubt about whether a comment is actionable, **lean non-actionable** and note it in the summary.

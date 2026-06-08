---
name: writing-article-0xmythril
description: "Writing articles for 0xMythril's social media: execution-vs-management framing, succinct, honest about skill gaps."
version: 1.0.0
author: 0xMythril
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [writing, social-media, article, 0xmythril]
    category: creative
---

# 0xMythril Article Writer

Writing style and workflow for 0xMythril's social media articles — concise, opinionated, and focused on human skill gaps in a world of AI tools.

## Voice

- **Direct and succinct.** No fluff. Each section earns its place.
- **Honest about human limitations.** Not "users are lazy" or "tools are broken." The honest read: our systems trained us for one job and now ask us to do another.
- **Avoid preachy change narratives.** Don't end with "here's how to fix it" unless explicitly asked. Explain the phenomenon. Let readers sit with it.
- **No wealth/class framing.** Skill gaps are systemic, not economic. Everyone is affected.
- **Thread-friendly structure.** Sections are digestible and naturally breakable into Twitter/X threads.

## Core Framing

### Execution vs. Management

The default 0xMythril thesis: We are culturally trained for **execution excellence**, not **management and delegation**. When AI agents arrived, they exposed this gap. Most people don't fail with agents because they're stupid or the tools are bad. They fail because managing another intelligence — human or artificial — is a distinct skill they were never taught.

Key phrases/assets to deploy:
- "You were trained to execute, not to manage."
- "The tool assumes a skillset our culture simply does not prioritize."
- "Making the assistant artificial did not make the management any less real."
- "The spark didn't die from hype. It died from a thousand tiny friction points that added up to 'not worth it.'"
- "Your agent becomes a tool you technically own but don't really use."

### The Erosion Narrative

The spark doesn't die dramatically. It fades through accumulated micro-friction:

1. **Honeymoon**: Initial setup + first tasks feel magical
2. **Friction accumulation**: Each correction, re-explanation, and edge case erodes trust
3. **The math**: Explaining takes longer than doing → you just do it yourself
4. **Reversion**: You stop reaching for the agent. It becomes idle.
5. **The quiet end**: Not an uninstall. Just a default.

### The Managerial Tax

Delegation doesn't remove work. It transforms it from *doing* to *managing the doing*:
- Scope → explain → verify → correct → re-explain
- The break-even point is higher than marketing claims
- Agents don't learn your preferences holistically; you pay the explanation tax every session

## Structure Template

```
# Title

[Hook — the universal starting point everyone recognizes]

But [the pivot — the thing nobody warned you about]

## Section 1: The Skill Nobody Taught You
[Execution training, systemic neglect of delegation, the hidden prerequisite]

## Section 2: The Daily Friction
[Concrete examples. Show, don't just tell. Numbers help: "30 seconds to write yourself, 4 minutes via agent"]

## Section 3: The Reversion
[The quiet default. No rage-quit, just gradual abandonment]

## Section 4: The Skill Mismatch
[Extend the thesis. "You were trained to... You were not trained to..." pattern]

## Section 5: Why the Spark Dies
[The accumulation narrative. Specific moments that add up]

## Conclusion
[Restate the core thesis without being repetitive. End on a clean observation, not a call to action]
```

## Anti-Patterns to Avoid

1. **"Wealthy people have this skill" framing** — ban. Skill gaps are systemic, not class-based.
2. **"The solution is X" preachiness** — unless explicitly asked to suggest improvements, explain the phenomenon and stop.
3. **Verbose AI slop** — no "at its core," "the real question is," "in today's rapidly evolving landscape" type filler.
4. **Over-sectioning with single-paragraph sections** — each section needs substance. Aim 3-6 paragraphs per section.
5. **Metaphor overuse** — one strong metaphor per article max. Prefer concrete examples.
6. **Generic positive conclusions** — don't end with "exciting times lie ahead." End with an observation.
7. **Corporate-speak** — "maximize," "leverage," "unlock potential," "drive value" — all banned.

## Editing Checklist

Before calling an article done, run through:
- [ ] Is every section earning its word count?
- [ ] Can any sentence be cut without losing meaning?
- [ ] Are the examples concrete and specific, not generic?
- [ ] Does the framing blame systems, not people or tools?
- [ ] Is the conclusion an observation, not a sermon?
- [ ] Would I actually post this, or does it feel performative?

## Example: Why Your AI Agent Stopped Being Useful

This skill was distilled from the iterative drafting of this article. The final version demonstrates:
- The execution-vs-management thesis applied to AI agents
- The erosion narrative with specific friction examples
- The "just do it myself" mathematical logic
- Succinct, punchy prose without filler

See the full draft at `articles/why-ai-agent-stopped-being-useful.md` (or wherever 0xMythril stores published articles).

## User Steering Style

0xMythril steers with short, direct corrections:
- *"The direction of this is wrong"
- *"I don't like referencing this to [X]"*
- *"I want this to focus on [Y]"*
- *"Not quite right although the general idea is okay"*

### What Works
- **Skeleton first:** Offer headers + bullets, write full draft only after user confirms direction.
- **Graceful reversion:** When user rejects a rewrite and prefers an earlier version, revert without resistance.
- **Succinct > verbose:** User explicitly stated: *"I like the previous version before humanizer as it was more succinct and to the point."* Fluffy rewrites are a regression.

## Pitfalls (Session-Learned)

### Humanizer: Skip It
The `humanizer` skill produces longer, "friendlier" prose that 0xMythril explicitly rejected for being less succinct. The baseline voice is already clean. Only humanize if user specifically asks.

### Asset Phrases
See `references/asset-phrases.md` for battle-tested quotes and thesis statements that have survived user revision rounds.

### Iteration History
See `references/iteration-notes.md` for documented patterns from session-2026-06-09 ("Why Your AI Agent Stopped Being Useful"), including framing corrections and validated structure.

## Workflow

1. **User provides direction** — concept, angle, target length, tone notes
2. **Draft skeleton** — section headers + bullet points for each section
3. **User steers direction** — typically 1-2 revision rounds on framing
4. **Write full draft** — following the structure template and voice guidelines
5. **Self-edit** — run the editing checklist
6. **User final review** — minor tweaks, then ship

## Output

Default save location: `~/articles/<slug>.md`

For social media threading, the article should be sectionable with clear break points (horizontal rules or explicit "Thread N/X" markers if requested).

---

"Making the assistant artificial did not make the management any less real."

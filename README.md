# my-agent-skills

Personal [Agent Skills](https://agentskills.io/) (portable `SKILL.md` workflows) for **Cursor**, **Claude Code**, and **Hermes**. Each skill lives in `skills/<skill-name>/SKILL.md`.

## Layout

```text
skills/
└── babysit-github-pr/
    └── SKILL.md
```

Add new skills the same way: one directory per skill, exactly one `SKILL.md` entrypoint.

## Install

### Cursor

Symlink (or copy) the skill into your personal skills folder:

```bash
ln -sf "$(pwd)/skills/babysit-github-pr" ~/.cursor/skills/babysit-github-pr
```

Skills load from `~/.cursor/skills/<name>/` (see Cursor “Agent Skills” docs).

### Claude Code

Symlink (or copy) into Claude’s personal skills directory:

```bash
ln -sf "$(pwd)/skills/babysit-github-pr" ~/.claude/skills/babysit-github-pr
```

Then invoke with `/babysit-github-pr` or rely on auto-discovery from the `description` in frontmatter.

### Hermes

**Option A — external directory (good for git clones):** in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/my-agent-skills/skills
```

Hermes merges skills from that tree with `~/.hermes/skills/`. Use an absolute path (or `${MY_AGENT_SKILLS}/skills` if you set that env var).

**Option B — copy/symlink into Hermes:** Hermes’s primary tree is `~/.hermes/skills/` (often grouped by category). You can symlink this repo’s skill, for example:

```bash
mkdir -p ~/.hermes/skills/devops
ln -sf "$(pwd)/skills/babysit-github-pr" ~/.hermes/skills/devops/babysit-github-pr
```

Then use `/babysit-github-pr` in Hermes.

## Frontmatter conventions

Each `SKILL.md` starts with YAML frontmatter:

- **`name`** — stable id (matches the directory name).
- **`description`** — third-person, includes **what** and **when** (used for discovery across tools).
- **`version`** — optional; Hermes-friendly semver string.
- **`metadata.hermes`** — optional Hermes hints (`tags`, `category`, `requires_toolsets`, etc.). Other agents ignore this block.

Extra keys are included only when they help a specific runtime and are safe for others to ignore.

## Skills in this repo

| Skill | Summary |
| --- | --- |
| [babysit-github-pr](skills/babysit-github-pr/SKILL.md) | Poll a GitHub PR, post cycle comments, fix actionable review/CI issues until merge-ready or limits hit. |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add skills, frontmatter rules (Cursor / Claude Code / Hermes), and a pre-merge checklist.

## License

MIT — see [LICENSE](LICENSE).

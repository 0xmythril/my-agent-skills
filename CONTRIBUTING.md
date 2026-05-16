# Contributing

Quick reference for adding or changing skills in this repo. Skills follow the [Agent Skills](https://agentskills.io/) shape so they work in **Cursor**, **Claude Code**, and **Hermes**.

## Add a new skill

1. **Create a directory** under `skills/`:

   ```text
   skills/<skill-name>/
   └── SKILL.md          # required entrypoint
   ```

2. **Name rules**

   - **Directory name** = **`name` in YAML frontmatter** (lowercase, hyphens, no spaces).
   - Keep it specific (e.g. `babysit-github-pr`, not `helper`).

3. **`SKILL.md` frontmatter** (YAML between `---` lines)

   | Field | Required | Notes |
   | --- | --- | --- |
   | `name` | yes | Same as directory name; stable id. |
   | `description` | yes | Third person. Include **what** it does and **when** to use it (triggers/tools/situations). |
   | `version` | optional | Semver string; helps Hermes and humans track iterations. |
   | `metadata.hermes` | optional | Hermes-only hints (see below). Safe for other tools to ignore. |

   **Hermes hints** (optional block):

   ```yaml
   metadata:
     hermes:
       tags: [topic1, topic2]
       category: devops          # or mlops, etc.
       requires_toolsets: [terminal]   # when the skill needs a shell/gh/docker, etc.
   ```

   Use `requires_toolsets` / `requires_tools` / `fallback_for_*` only when discovery should depend on available tooling (see [Hermes skills docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)).

4. **Body**

   - Short **title** then **steps**, **rules**, **stop conditions**, **templates** — whatever the agent must follow.
   - Prefer linking **`reference.md`** or **`examples.md`** in the same folder if the main file grows large (keep `SKILL.md` scannable).

5. **Wire it up for yourself**

   Symlink or add `external_dirs` as in [README.md](README.md), then load the skill once in each tool you use.

6. **Register in the catalog**

   Add a row to the **Skills in this repo** table in [README.md](README.md).

## Change an existing skill

- Bump **`version`** when behavior or triggers change in a meaningful way.
- If you split content into new files, link them from `SKILL.md` (one level deep is easiest for agents to follow).

## PR / git workflow

- Branch from **`main`**, open a PR when you want review (solo maintainers can push directly if you prefer).
- Keep commits scoped: one skill added or one logical update per commit when possible.
- Do **not** commit secrets, `.env*`, or machine-specific absolute paths inside `SKILL.md` (use placeholders and env var names).

## Review checklist (before merge)

- [ ] `skills/<name>/SKILL.md` exists; folder name matches `name:` in frontmatter.
- [ ] `description` is third-person and names **what** + **when**.
- [ ] No secrets or one-off local paths.
- [ ] README table updated for new skills.
- [ ] Optional: tested via symlink / Hermes `external_dirs` on your machine.

## License

By contributing, you agree your contributions are under the same [LICENSE](LICENSE) as the repo (MIT).

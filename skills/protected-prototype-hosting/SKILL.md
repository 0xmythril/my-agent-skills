---
name: protected-prototype-hosting
description: Publishes and updates static web prototypes at stable Cloudflare HTTPS URLs protected by a shared password. Use when sharing prototypes across devices or with reviewers, or maintaining their password gate.
---

# Protected prototype hosting

Host a reviewable static prototype on Cloudflare Workers with server-side HTTP Basic authentication. The default username is `moca`. Keep the password outside repositories and load it from a separately provisioned secret file. This viewing gate is independent of any login or consent flows simulated inside the prototype.

## Scope and defaults

- Support static build output, including plain HTML prototypes. For an app with an existing backend or authentication system, adapt its established deployment; do not silently replace it with a static site.
- A request to publish or update a hosted prototype authorizes that site's deployment. An advice-only question or an unrelated local edit does not authorize publishing. Respect an existing requested audience and provider.
- Default username: `moca` (non-secret; safe in configuration).
- Runtime password binding: `PREVIEW_PASSWORD`.
- Default local secret file: `~/.config/moca-skills/secrets/prototype-hosting.env`.
- Optional override: `MOCA_PROTOTYPE_SECRETS_FILE` points to a separately provisioned file outside the project and skills repositories. It contains `PREVIEW_PASSWORD` in dotenv format. Never interpret the path as shell code or source the file.
- No password value or password default belongs in the skill, repo config, template, test fixture, example, command argument, commit, PR, or published asset. Do not print a secret file to discover its contents.
- Reuse the external credential when present. On another machine, request secure provisioning through a hidden terminal prompt or secret manager. Never invent a replacement password or publish without protection when it is absent.
- Updating a shared credential locally does not update other deployed Workers. Rotate only sites in the user's requested scope.

## Prepare the deployment

1. Read the project's instructions and inspect its existing hosting configuration. Reuse its Worker and account when applicable; otherwise identify an authenticated account and a new project-specific Worker name. Do not overwrite an unrelated site.
2. Read current Cloudflare docs for the options being used. If available, use the `cloudflare`, `wrangler`, and `workers-best-practices` skills. This skill does not require an MCP connector.
3. Check Wrangler authentication with `npx wrangler whoami`. For remote-device login, use a version supporting `npx wrangler@latest login --device --browser=false`; the operator approves the displayed URL/code on their own device. Do not ask them to send Cloudflare tokens in chat.
4. Produce a reviewed output directory containing only the intended web assets. Never upload the workspace root, the skills registry, source credentials, or internal notes unless the user explicitly wants those notes shared with reviewers. For plain HTML, copy an explicit file allowlist into a dedicated output directory.
5. Use a project-local, pinned Wrangler dependency and `wrangler.jsonc`. Set a current supported compatibility date and `nodejs_compat` when using Node crypto APIs. Keep the asset binding named `ASSETS` and username variable named `PREVIEW_USERNAME`.

Essential config fields (merge with existing configuration):

```json
{
  "workers_dev": true,
  "preview_urls": false,
  "assets": {
    "directory": "./dist",
    "binding": "ASSETS",
    "run_worker_first": true
  },
  "vars": { "PREVIEW_USERNAME": "moca" },
  "secrets": { "required": ["PREVIEW_PASSWORD"] },
  "observability": { "enabled": true, "head_sampling_rate": 1 }
}
```

## Authentication invariants

Authenticate every request before `env.ASSETS.fetch(request)`. `run_worker_first: true` is essential: otherwise static asset routing can bypass the password gate. Keep version preview URLs disabled by default; protect any existing custom domains and aliases too. Do not leave an unprotected origin or Pages copy serving the same private assets.

- Missing or empty username/password configuration returns `503` without fetching assets.
- Missing, malformed, oversized, or incorrect Basic credentials return `401` with `WWW-Authenticate: Basic realm="Prototype Preview", charset="UTF-8"`.
- Decode credentials defensively; compare fixed-length SHA-256 digests with a timing-safe comparison, not direct password equality. Test Unicode decoding if supported.
- Fetch assets only after authentication, strip the Authorization header before forwarding to the asset binding, and allow only GET/HEAD for a static prototype.
- Mark all responses `Cache-Control: private, no-store`; authenticated content must never populate a public response cache. Add `X-Robots-Tag: noindex, nofollow, noarchive` and `X-Content-Type-Options: nosniff`.
- Use HTTPS for the shared URL. A JavaScript password overlay or a password embedded in the HTML is not access protection.
- Do not log credentials or Authorization headers. If authentication errors, fail closed rather than forwarding to assets.

## Secret handling and deployment

Provision the secret outside all repositories with owner-only file permissions (`0600`) and a private containing directory. Use a hidden prompt rather than putting the password in shell history, shell command text, or source files. Keep any project-local dotenv files ignored; prefer the external file for this workflow.

For the default credential path, deploy code and secret together after building and validating:

```bash
npx wrangler deploy --dry-run
npx wrangler deploy --secrets-file "$HOME/.config/moca-skills/secrets/prototype-hosting.env"
```

If `MOCA_PROTOTYPE_SECRETS_FILE` is configured, use that validated path instead, with proper shell quoting. The password value must never be interpolated into command text. A later `wrangler deploy` preserves the remote password; changing usernames and rotating passwords should be explicitly reflected in the same authorized deployment.

Do not blindly retry a deployment failure: inspect the error and remote version status first. After a successful deployment, use the returned URL, not a guessed hostname. If login or secret provisioning needs the operator, finish all independent preparation and identify that remaining step.

## Verification and handoff

Run appropriate type/config checks and test the security boundary before publishing. Use synthetic test credentials, never the real shared password in test source. Verify the deployed URL too:

- Anonymous requests to `/`, a known asset, and a direct HTML path return `401`.
- Incorrect or malformed credentials return `401`.
- Correct credentials return the expected prototype and linked assets.
- An anonymous request after an authenticated one still returns `401`.
- Workspace credential/config files are absent from uploaded assets, even after successful authentication.
- The same checks cover any active alternate public hostname; a disabled version preview is not advertised as usable.

Read test credentials inside the verification process; output only status results. Scan the proposed repository files and deployment output for the configured secret without printing matching content.

Return the working HTTPS link, username, verification result, and where the user can retrieve the secret securely. Do not repeat the password in chat by default. Explain that a shared credential grants access to anyone who receives it; recommend identity-based access only when the user needs individual access control. Browser Basic Auth may cache credentials, so use a fresh private window when checking a rotated login.

## Current references

- [Worker-first asset routing](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/)
- [Worker secrets and secrets-file deployment](https://developers.cloudflare.com/workers/configuration/secrets/)
- [Basic authentication example](https://developers.cloudflare.com/workers/examples/basic-auth/)
- [Remote-device Wrangler login](https://developers.cloudflare.com/workers/wrangler/commands/general/)

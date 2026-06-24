# Web-Amplified STORM Playbook

**Skill:** storm-research-workflow  
**When to use:** Deep research on fast-moving competitive landscapes (payment rails, AI protocols, regulatory frameworks) where parametric knowledge is stale or incomplete.

---

## Workflow Summary

1. **Phase 0 — Parallel Evidence Gathering**
   - Run `web_search` on 3–5 targeted queries in parallel
   - Run `web_extract` on 5–8 key URLs
   - Synthesize a bullet-list evidence memo (hard numbers, direct quotes, contradictions)

2. **Phase 1 — Prompt 1 with Evidence Ingestion**
   - Paste evidence memo into the persona prompt before the 5-perspective simulation
   - Forces personas to ground claims in current data

3. **Phases 2–4 — Standard STORM**
   - Contradiction map, synthesis briefing, peer review
   - Treat real-time metrics as claims to be verified in peer review

4. **Phase 5 — Strategic Stack Map**
   - Draw a 6-layer competitive architecture (application → orchestration → authorization → wallet → settlement → asset)
   - Annotate where each player sits
   - Identify whitespace based on your own capabilities

5. **Phase 6 — Build / Partner / Buy Matrix**
   - Row = component/layer
   - Cols = Action (build/partner/buy), Rationale, Owner/90-day deliverable

---

## Evidence Memo Template (Copy → Paste → Fill)

```
TOPIC: _______________
DATE OF SEARCH: _______

### Key Metrics (with source)
- [e.g., $24M volume / 75.4M txns last 30d — x402.org metrics page]

### Player Moves (chronological)
- [Date + Company + Action + URL]

### Regulatory / Compliance Signals
- [Act/deadline/ruling + implication]

### Contradictory Claims
- [Source A claims X; Source B claims not-X]

### Definitions That Collide
- [e.g., "tokenization" = network tokenization vs blockchain tokenization]

### Blind Spots / No Mention Of
- [e.g., "Nobody addresses cross-rail accounting reconciliation"]
```

---

## Pitfall Checklist

- [ ] Did I include at least one TradFi/regulatory query to balance crypto-native sources?
- [ ] Did I extract from authoritative sources (network press releases, SEC/regulatory PDFs, academic arXiv) and not just blog summaries?
- [ ] Did I surface naming collisions (same word, two technical meanings)?
- [ ] Did I check if metrics come from the same ecosystem vendor (self-reported) vs neutral third party?
- [ ] Did I map players across the full stack, not just the settlement layer?

---

## Useful Tool Combinations

| Goal | Tools |
|---|---|
| Gather current adoption data | `web_search` (parallel x3) → `web_extract` |
| Read regulatory PDFs | `web_extract` handles PDF conversion directly |
| Capture truncated paywalled pages | `browser_navigate` → `browser_snapshot` |
| Academic grounding | `web_search` with `site:arxiv.org` + `web_extract` |
| Multi-protocol comparison | Search "[Protocol A] vs [Protocol B]" comparison articles |
|
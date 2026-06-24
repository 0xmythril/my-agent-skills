---
name: storm-research-workflow
description: >
  A 4-prompt multi-perspective research workflow derived from Stanford STORM
  (NAACL 2024) to generate deep, nuanced research briefs and surface blind
  spots before writing or decision-making.
category: research
---

# STORM 4-Prompt Deep-Research Workflow

**Source:** Stanford OVAL Lab — *STORM: Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking* (NAACL 2024).  
**Distillation:** Nav Toor / @heynavtoor — "The Stanford STORM Method" X article.

## When to use

- Before writing a long-form article, essay, or strategic memo where you need nuance, not surface-level consensus.
- Before making a high-stakes product or investment decision where you suspect hidden assumptions.
- When you want to stress-test a narrative — find what Everyone Agrees On (likely true) and what Nobody Talks About (the blind spot).
- When you want a self-editing / peer-review layer on an existing draft.

## What you'll get (in ~5 minutes)

1. **5 expert perspectives** (Practitioner, Academic, Skeptic, Economist, Historian) with core claims and unique evidence.
2. A **contradiction map** — direct conflicts, the strongest evidence, blind spots, and consensus points.
3. A **synthesis briefing** — CEO-level summary, ranked findings, hidden connections, actionable insight, frontier question.
4. A **self-peer-review** — confidence scores, bias audit, missing angles, overall grade.

## Prerequisites

- An LLM interface (Claude, ChatGPT, Hermes Agent with a strong model, etc.).
- A topic string you want to research.
- Sequential prompting — the prompts build on each other and must be run in order.

## Workflow

### Step 1 — Prompt 1: Multi-Perspective Scan

Paste into the LLM, replacing `[YOUR TOPIC]`:

```text
I need to research [YOUR TOPIC].
Simulate 5 different expert perspectives on this topic:

1. THE PRACTITIONER: works with this daily.
What do they know that academics miss?
What practical realities are usually ignored?

2. THE ACADEMIC: has studied this for years.
What does the peer reviewed evidence actually say?
Where does the evidence contradict popular belief?

3. THE SKEPTIC: thinks the mainstream view is wrong.
What is the strongest counterargument?
What evidence do proponents conveniently ignore?

4. THE ECONOMIST: follows the money.
Who profits from the current narrative?
What financial incentives shape the research?

5. THE HISTORIAN: has seen similar patterns before.
What historical parallels exist?
What can we learn from how those played out?

For each perspective give me:
- Their core position in 2 sentences
- The strongest evidence supporting their view
- The one thing they would tell me that no other perspective would
```

**Expected output:** Five distinct, complementary lenses with specific evidence and unique takeaways.

### Step 2 — Prompt 2: Contradiction Map

Using the output from Prompt 1, paste:

```text
Based on the 5 perspectives above, map the contradictions:

1. Where do two or more perspectives directly contradict each other? List each conflict with the specific claims that clash.

2. Which perspective has the strongest evidence? Which has the weakest? Why?

3. What is the one question that, if answered, would resolve the biggest contradiction?

4. What does EVERY perspective agree on?
(This is likely true. Even opponents confirm it.)

5. What topic did NONE of the perspectives address?
(This is the blind spot in the whole field. Often the most valuable finding.)
```

**Key rule:** If all 5 agree, it is almost certainly true. If nobody mentions a topic, you have found a field-wide blind spot.

### Step 3 — Prompt 3: Synthesis Briefing

Paste:

```text
Synthesize everything from the 5 perspectives and the contradiction map into a research briefing:

1. THE ONE PARAGRAPH SUMMARY: explain this topic as if briefing a CEO who has 60 seconds and needs nuance, not just the headline.

2. THE 5 KEY FINDINGS: most important things I now know, ranked by reliability. For each, note which perspectives support it and which challenge it.

3. THE HIDDEN CONNECTION: one non obvious link between findings that only shows up when you look at all 5 perspectives together.

4. THE ACTIONABLE INSIGHT: based on all the evidence, what should someone in [YOUR ROLE] actually DO differently? Be specific.

5. THE FRONTIER QUESTION: the one question that, if answered, would change everything about how we understand this topic.
```

**Expected output:** A single integrated brief that surfaces connections no single-angle prompt would catch.

### Step 4 — Prompt 4: Peer Review (Red Team)

Paste:

```text
Now peer review your own research briefing:

1. CONFIDENCE SCORES: rate each of the 5 key findings on a 1 to 10 scale for reliability. Explain each score.

2. WEAKEST LINK: which claim are you least confident in? What specific info would you need to verify it?

3. BIAS CHECK: which perspective might be overrepresented in your synthesis? Did one voice dominate?

4. MISSING PERSPECTIVE: is there a 6th angle I should have included that would change the conclusions?

5. OVERALL GRADE: if a Stanford professor reviewed this briefing, what grade would they give and why? What would they tell me to fix?
```

**Expected output:** A rigorous audit that flags overconfidence, missing angles, and bias overrepresentation.

## Pro tips / Pitfalls

1. **Be specific with the topic.** Vague topics → vague personas → generic output. Include domain, geography, or timeframe if possible.
2. **Don't skip Prompt 2.** The contradiction map is the highest-value step — true understanding lives in the disagreements, not the consensus.
3. **Swap personas if needed.** The default set (Practitioner, Academic, Skeptic, Economist, Historian) works for most domains. For technical topics you might swap in *Security Researcher* or *Regulator*; for creative topics, *Critic* or *Consumer*.
4. **No live web search.** These prompts rely on the model's parametric knowledge. If you need real-time citations or post-cutoff facts, run the official open-source `knowledge-storm` pipeline (DSPy-backed, litellm-compatible) instead.

## Variation: Web-Amplified STORM for Emerging Standards & Competitive Landscapes

See `references/web-amplified-storm-playbook.md` for the full procedure, evidence-memo template, and pitfall checklist. See `templates/competitive-stack-matrix.md` for the strategic output format that translates research into a build/partner/buy action plan.

When the topic is fast-moving (payment protocols, AI tooling standards, regulatory frameworks), parametric knowledge is often stale or generic. Use this hybrid workflow:

### Phase 0 — Parallel Evidence Gathering (before Prompt 1)
1. Run **3–5 targeted `web_search` queries** in parallel covering:
   - The standard/protocol name + adoption/volume metrics
   - Competing standards and comparison articles
   - Enterprise/integration announcements (Stripe, Visa, etc.)
   - Compliance/regulatory angles (PCI, ISO, EU acts)
2. Immediately run **`web_extract`** on the 5–8 most promising URLs to pull structured text (not just summaries — extraction captures tables, quotes, and specific metrics).
3. **Synthesize a raw evidence memo**: bullet-list of hard numbers, direct quotes, key player moves, and contradictory claims.

### Phase 1 — Prompt 1 with Evidence Ingestion
Feed the evidence memo into the persona prompt:
```text
I need to research [TOPIC].
Use the following real-time evidence gathered from current sources: [PASTE EVIDENCE MEMO]
Simulate 5 expert perspectives... [rest of standard Prompt 1]
```
This forces the personas to ground claims in current data rather than generic knowledge.

### Phase 2–4 — Proceed Normally
Run contradiction map, synthesis briefing, and peer review as usual. The real-time citations show up as data points the perspectives must reconcile, making the contradiction map richer.

### Phase 5 — Strategic Stack Map (Post-Peer Review)
For product/strategy research, add a final synthesis artifact:
1. **Competitive Stack Map**: Map players by layer (infrastructure → protocol → application). Identify where you are and where the open white-space sits.
2. **Build / Partner / Buy Matrix**: For each layer, recommend whether to build (differentiated), partner (commodity), or buy (urgent gap).
3. **Concrete 90-Day Horizon**: Translate the matrix into 3–4 specific builds or integrations with clear owners.

### Pitfalls
- **Search-query bias**: If all queries are crypto-native, the synthesis skews anti-incumbent. Deliberately include TradFi/regulatory queries.
- **URL decay**: Web-extracted content can be truncated. For paywalled or critical sources, use `browser_navigate` + `browser_snapshot` to capture the full page.
- **Conflicting definitions**: Terms like "tokenization" mean entirely different things in PCI vs blockchain contexts. Surface these definitional collisions explicitly in the contradiction map.
5. **Temperature matters.** Use a creative temperature (~1.0) for Prompt 1 so personas diverge; use a lower temperature (~0.3) for Prompt 4 so the audit is strict.

## Variations

- **6–8 perspectives:** For ultra-high-stakes decisions, add a *Regulator* and a *Technologist* in Prompt 1, then feed all into Prompt 2.
- **Programmatic STORM:** Use the `knowledge-storm` Python package (`pip install knowledge-storm`) to automate the full pipeline with live web retrieval, hierarchical outline generation, and citation insertion. See <https://github.com/stanford-oval/storm>.
- **Draft audit:** Already have a written draft? Paste it into the LLM and append **Prompt 4** to red-team it before publishing.

## Verification

- Did the model surface at least one claim that surprised you or contradicted the mainstream view? If not, the personas may not have been pushed hard enough — raise the temperature or refine the topic.
- Does the blind-spot question in Prompt 2 identify a gap you had not considered? If the answer is "nothing," the topic is likely too narrow or too broad.
- Do confidence scores in Prompt 4 average >8? If yes, push harder on the skeptic and weakest-link questions.

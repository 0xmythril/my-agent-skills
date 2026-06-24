# Competitive Stack Map + Build/Partner/Buy Matrix

**Use after:** Web-Amplified STORM Phase 5–6  
**Purpose:** Translate deep research into a product strategy artifact the user can act on immediately.

---

## Part 1: 6-Layer Stack Map

Map competitors, incumbents, and emerging protocols across the agent payment / infrastructure stack. Annotate your own position (👤) and whitespace (⬜).

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 6: APPLICATION / MERCHANT                                      │
│ [Player A] [Player B] [Player C]                                   │
├─────────────────────────────────────────────────────────────────────┤
│ LAYER 5: ORCHESTRATION / ROUTING / GATEWAY                           │
│ [Player D] [Player E]                                              │
├─────────────────────────────────────────────────────────────────────┤
│ LAYER 4: AUTHORIZATION / IDENTITY / TRUST / COMPLIANCE  ◄── SWEET SPOT?│
│ [Player F] 👤 (you?) [Player G]                                    │
├─────────────────────────────────────────────────────────────────────┤
│ LAYER 3: WALLET / SMART ACCOUNT / CUSTODY                            │
│ [Player H] [Player I]                                              │
├─────────────────────────────────────────────────────────────────────┤
│ LAYER 2: SETTLEMENT / PAYMENT RAIL                                   │
│ [Rail J] [Rail K] [Rail L]                                          │
├─────────────────────────────────────────────────────────────────────┤
│ LAYER 1: MONEY / ASSET REPRESENTATION                              │
│ [Asset M] [Asset N] [Asset O]                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Variations:**
- For infra research: use a 4-layer (interface → protocol → middleware → base layer).
- For B2B SaaS: use a 3-layer (application → integration → infrastructure).

---

## Part 2: Strategic Decision Matrix

Transpose the stack map into action items.

| Layer / Component | Current State | Action | Rationale | Partner Target (if Action = Partner) | 90-Day Deliverable | Owner |
|---|---|---|---|---|---|---|
| L4 Identity | No on-chain agent identity | **Build** | Core moat — game-native reputation has no generic equivalent | n/a | Agent DID contract + SDK | Alex |
| L2 Settlement | Only USDC on Base | **Use** | Commodity rail | Coinbase, Circle | Deploy on Solana too | n/a |
| L3 Wallet | EOAs only | **Partner** | ERC-4337 infra is commoditized | Pimlico / ZeroDev | Moca Agent Wallet SDK | Beth |
| L6 Merchant | No merchant onboarding | **Partner** | Don't build Stripe | Stripe / BVNK / Bridge | Fiat off-ramp integration for Japan/Korea | Chris |
| L4 Dispute/Arb | No recourse mechanism | **Build** | Nobody has shipped this | n/a | Reputation-conditional escrow contract | Alex |

---

## Part 3: The Line in the Sand

Draw a 2x2 positioning diagram using the two axes that matter most to the user's ecosystem:

```
          Consumer Trust / Fiat
                 │
    Incumbents   │   Stripe / Visa / Mastercard
                 │
  ──────────┼──────────
                 │
    M2M / Crypto │   x402 / Base / Solana
                 │
          Programmability / Crypto Trust
```

Annotate where the user should position and what whitespace exists between the incumbents and the crypto-natives.

---

## Tips

- **Don't** put the user in the top-right (institutional trust / fiat). That's the incumbents' turf.
- **Don't** put them in the bottom-left (pure crypto programmability) unless they have zero institutional relationships.
- **Do** look for the diagonal: programmable trust + compliant-enough settlement where neither pure-TradFi nor pure-crypto players have a complete offer.
- **Do** define the customer segment that makes this diagonal valuable (e.g., "game studios already using NFTs" or "APAC merchants needing PIX + USDC").

---

## How to Integrate with STORM Output

After Prompt 4 (Peer Review), review the "confidence scores" for each finding. Components scoring ≥8/10 become **Build** or **Use** candidates. Components scoring ≤6/10 become **Partner** candidates (let someone else resolve the uncertainty). Components scoring 7–8/10 and adjacent to your core domain become **Build** with a 90-day validation window.

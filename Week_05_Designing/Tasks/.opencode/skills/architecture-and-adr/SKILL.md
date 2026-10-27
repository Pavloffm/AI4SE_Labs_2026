---
name: architecture-and-adr
description: Turn project requirements into compared architecture options, facilitate a grounded decision, and create or revise an Architecture Decision Record.
---

# Architecture Proposals and ADRs

Use this workflow when asked to propose system architectures, choose one with the user, or write/revise an ADR. Keep user-facing discussion conversational; do not make consequential product or architecture decisions on the user's behalf.

## 1. Establish the evidence

1. Read the task instructions and the assigned requirements/source documents. Identify the project's actors, capabilities, quality attributes, constraints, and explicit exclusions.
2. Separate stated facts from assumptions and unknowns. Ask focused questions where an answer could change the architecture (for example, scale, availability, clients, integrations, privacy, or budget).
3. Keep notes in a conversation record when requested. Record the important alternatives, user choices, rationale, trade-offs, and remaining questions; it need not be verbatim.

## 2. Propose and compare architectures

1. Present at least three materially different architectures when the task asks for alternatives. Tailor them to the requirements rather than listing patterns by name. For each, explain:
   - components, boundaries, data ownership, and request/data flows;
   - fit to the requirements and important quality attributes;
   - operational and implementation burden, including difficult low-level work;
   - failure modes, security/privacy implications, scaling limits, and likely costs;
   - what would make this option preferable and what would make it painful.
2. Compare alternatives on the same criteria. State a recommendation and its rationale, but preserve the user's authority to choose.
3. Challenge mismatches respectfully. In particular, distinguish a preference from a justified decision, and test claims such as “scale later” or “horizontal database scaling” against concrete workloads and mechanisms.
4. Ask one or a few high-value questions at a time. Update the comparison as answers arrive. Keep unresolved decisions visibly unresolved; do not convert a tentative preference into a settled fact.
5. Explain evolutionary paths and simpler alternatives. Avoid premature microservices or infrastructure unless requirements justify their added cost and distributed-systems complexity.

## 3. Create or revise the ADR

Use the repository's existing ADR convention if one exists. Otherwise create a concise Markdown ADR with:

- title/identifier, status, and date if known;
- context: requirements and forces that drive the decision;
- decision: selected architecture, boundaries, interactions, and data ownership;
- alternatives considered, including reasons rejected;
- consequences: benefits, costs, risks, operational responsibilities, and migration/evolution path;
- a diagram and/or comparison table when they improve comprehension;
- explicit open questions and assumptions.

Ground every decision in the source requirements or an explicit user choice. Make trade-offs concrete (for example, cache staleness, cross-service failure behavior, session revocation, data consistency, and deletion/retention). Do not claim availability, privacy, security, or scalability without naming the mechanism and its limits. Distinguish normal cache TTL from outage fallback freshness, and distinguish anonymization from reversible pseudonymization. Avoid inventing implementation details that the discussion did not settle.

When revising, inspect the existing ADR and apply the user's feedback surgically. Preserve valid material, update affected diagrams/tables and consequences together, and retain unresolved questions rather than silently answering them. Summarize what changed and what remains open.

## 4. Review and verify

Before handing off, check that:

- each requirement relevant to architecture is addressed or marked open;
- alternatives are genuinely distinct and fairly compared;
- the selected design matches the user's latest explicit choices;
- diagrams, tables, prose, and service/data boundaries agree;
- consequences and failure behavior follow from the decision;
- no assumption is presented as a fact, and no open question is hidden.

If asked to compare work with and without this skill, use actual records as evidence. Separate observed process/artifact differences from measured time or quality claims. If no post-skill session or timing data exists, label any replay as a qualitative exercise and do not fabricate measurements.

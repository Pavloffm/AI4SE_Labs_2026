# Task 3 — Skill and Comparison Report

## Deliverables

- Reusable OpenCode skill: [`.opencode/skills/architecture-and-adr/SKILL.md`](.opencode/skills/architecture-and-adr/SKILL.md)
- Before-skill Task 1 record: [`Conversation_Record.md`](Conversation_Record.md)
- Before-skill Task 2 record: [`Conversation_Record_2.md`](Conversation_Record_2.md)
- After-skill repeat session: [`Conversation_Record_3.md`](Conversation_Record_3.md)
- Resulting ADR: [`ADR-001-onesport-architecture.md`](ADR-001-onesport-architecture.md)

The skill captures the workflow demonstrated by those records: extract requirements and unknowns; compare at least three tailored options; probe user goals and trade-offs; distinguish preferences from decisions; then draft and iteratively revise an ADR with concrete consequences and explicit open questions.

## Comparison

| Dimension | Before skill (recorded sessions) | After skill (recorded repeat session) |
| --- | --- | --- |
| Architecture exploration | The first session compared three architectures and explored detailed implementation trade-offs. The discussion gradually moved from the initially favored SPA/modular monolith to microservices, then into service boundaries, gateway, storage, and failure handling. | Record 3 also compares three architectures, identifies missing requirements and inherited assumptions, and weighs first-release simplicity against independent scaling. The user chose a server-rendered monolith for the first release. |
| Decision clarity | Many decisions were elicited over a long sequence; the initial preference changed more than once, and the eventual microservices choice required extensive follow-up to qualify its cost and scope. | The repeat explicitly distinguished the user's focus on an option from a final decision. It documented the rationale for choosing the monolith and kept inherited assumptions and unresolved policies visible. |
| ADR work | The ADR discussion included revisions for shared PostgreSQL and Supabase Auth, and retained open questions such as token flow and account recovery. | The ADR was revised to match the selected monolith, then updated with request/data flows, deployment and trust boundaries, comparison criteria, and reworded open questions. The user confirmed it as a proposed decision. |
| Efficiency evidence | The original recordings show extensive discussion and multiple decision turns. No elapsed-time measurements are recorded. | A second, recorded completion is now available. It appears more structured and reaches a proposed architecture in the recorded exchange, but no comparable duration or effort measurements exist, so faster completion cannot be established. |

## Assessment

The repeat session demonstrates the skill being applied to the same requirements while reaching a different, user-selected architecture. The record supports a qualitative comparison: the workflow makes alternatives, decision rationale, inherited assumptions, and ADR review steps explicit. It does not establish a time saving because neither session has reliable duration data. The two sessions also made different choices, so this is a comparison of process and recorded outcomes, not a controlled test of architecture quality.

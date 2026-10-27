# OneSport — Conversation Record 2

## ADR drafting session

**User:** “@Task_2.md let's start making it. Write our converstation to Conversation_Record_2 We will discuss architecure from @Conversation_Record.md”

**Assistant:** I will use `Conversation_Record.md` as the architecture source, create a reviewable ADR, and record this ADR-writing session in `Conversation_Record_2`. I will preserve unresolved choices as open points rather than inventing decisions.

**Assistant:** I reviewed the Task 2 instructions and the Task 1 conversation record. The source describes a final preference for three microservices (identity, content, and user-features), with an API gateway, managed containers, service-owned databases on a shared managed DB cluster, HTTP communication, gateway sessions, and the cost/scaling/failure-handling trade-offs. A few issues are still unresolved, notably whether 90-day retention permits account recovery, friendship data deletion, and concrete scaling thresholds.

**Assistant:** I created `ADR-001-onesport-architecture.md` as a proposed decision, not a silently finalized record. It includes the decision context, component overview table, Mermaid architecture diagram, alternatives, reliability and security policies, consequences, rollout checks, and open questions. The account-recovery question is explicitly highlighted because a reversible undo window is pseudonymization, not full anonymization.

**Assistant:** Please inspect the first draft. Is the amount of detail and structure useful? In particular, should the diagram/table be simpler, should anything be removed or added, and do you agree the unresolved questions should remain visible rather than being resolved by assumption? I will revise the ADR based on your feedback and record each iteration here.

## Architecture revision: shared PostgreSQL service

**User:** “I want you to modify @ADR-001-onesport-architecture.md. I want to use my custom architecture. It looks strange to separate databases so let's use PosgreSQL as different service and we can latter just scale up it in horizont. Create it as new modified architecture.”

**Assistant:** I revised the architecture to use one dedicated PostgreSQL service shared by the three domain services, instead of separate database services. The ADR now shows PostgreSQL in the component table and diagram, and calls for separated schemas/tables and least-privilege roles. Domain services should access another domain's data through its owning service API rather than directly querying its tables.

**Assistant:** I also documented the scaling caveat: PostgreSQL can be scaled as a service, but horizontal scaling is not automatic. Read replicas can help eligible read workloads; write scaling may require partitioning/sharding or a different design. The ADR says to measure first and consider query/index improvements, vertical capacity, connection pooling, and read replicas before taking on that complexity. This keeps the requested architecture while avoiding a promise that adding nodes alone will scale every PostgreSQL workload.

## Authentication provider choice

**Assistant:** I compared managed identity providers, Supabase Auth, self-hosted Keycloak, and custom authentication. The recommendation was managed authentication because the user wants to avoid personally operating authentication infrastructure. Supabase Auth was presented as a good fit if adopting its platform is acceptable, while noting that the gateway, authorization, OneSport account data, and deletion workflows remain OneSport responsibilities.

**User:** “Supabase Auth”

**Assistant:** I recorded Supabase Auth as the selected authentication provider. The ADR now assigns email/password authentication and managed verification/recovery to Supabase Auth; OneSport's identity service retains profile/account mapping and deletion orchestration, and does not store passwords. The ADR also notes that Supabase account deletion does not itself delete OneSport data or gateway sessions.

**Assistant:** The gateway-session choice from the earlier architecture discussion still needs a concrete integration decision: (1) use the gateway as a BFF that handles provider tokens and issues an opaque app session, or (2) let the SPA present Supabase access tokens to the gateway for validation. I added this as an open question rather than assuming the earlier “gateway sessions” preference determines the token flow. The 90-day undo-window/account-recovery question remains open as well.

# OneSport — Conversation Record 3

## Task 1: Architecture comparison

### Sources and scope

- `data/OneSport.txt` describes accounts, login/logout, profile settings and credential changes, account deletion, news browsing and country filtering, saved news and ticket links, friend requests, friendship management, user lookup, and saved-list views.
- `ADR-001-onesport-architecture.md` is prior context, not a binding choice for this repeat discussion. It includes additional decisions not stated in `OneSport.txt`: Supabase Auth, admin-managed news/events, no ticket payments, shared PostgreSQL, and 90-day retention.
- Traffic, availability targets, budget, client/platform constraints, content-ingestion source, and implementation team capacity are not specified in the requirements.

### Initial comparison presented

| Architecture | Components and data ownership | Fit and trade-offs |
|---|---|---|
| Server-rendered monolith | One web application serves pages and handles identity, content, saved items, and social features; one relational database owns application data. | Lowest deployment complexity and straightforward transactions for account deletion, saved items, and friend requests. Server rendering reduces client complexity. Application concerns and scaling remain coupled; interactive app-like behavior may take more implementation. |
| SPA + modular monolith | Browser SPA calls one backend application. Identity, content, and user features are separate internal modules sharing one relational database. | App-like interaction with simple deployment and transactional consistency; module boundaries can support later extraction. News-heavy traffic generally scales the whole backend unless optimized separately; boundaries require discipline and can erode. |
| SPA + microservices | SPA calls an API gateway routing to independently deployed identity, content, and user-feature services. The prior ADR proposes shared PostgreSQL infrastructure with isolated schemas/roles. | Content can scale independently, but network calls, gateway availability, service authentication, cross-service account deletion, partial failures, monitoring, and operational cost increase. Shared PostgreSQL remains a capacity/failure coupling; adding nodes does not automatically scale writes. |

Initial assistant recommendation: modular monolith unless there is a concrete need for independent content scaling/deployment.

**User choices (via question function):** Keep all three architectures in contention; focus further exploration on B, SPA + modular monolith. Keep Supabase Auth, shared PostgreSQL, and 90-day retention. These are constraints for the comparison, while unresolved implementation and policy details remain open. No final architecture choice has been made.

**Assistant response:** The modular monolith is the current focus, not a settled choice. Account-deletion and recovery details under 90-day retention remain open.

The next comparison should examine concrete component boundaries/data flows, failure and scaling behavior, and operational/implementation effort for all three, with added detail on the modular monolith. The assistant will ask the user about the trade-off that would change the architecture choice before drafting/revising the ADR.

**Assistant comparison:** Described A's browser-to-server-rendered-app-to-PostgreSQL flow, B's SPA-to-single-backend with internal identity/content/user-feature modules, and C's SPA-to-gateway-to-services flow. Compared initial operations, transaction simplicity, app-like interaction, independent content scaling, failure surface, and likely difficult work. Explained that shared PostgreSQL does not inherently scale writes horizontally and that 90-day recoverable retention is not necessarily anonymization. Asked whether near-term independent content scaling or first-release simplicity should carry more weight.

**User choice (via question function):** Simplicity should carry more weight for the first release. This weighs against microservices absent a concrete independent-scaling need, but does not yet settle between server-rendered monolith (A) and SPA + modular monolith (B), nor select an architecture.

**Assistant:** Explained that A is operationally simplest, while B retains one backend/database but fits an app-like SPA experience. The requirements do not specify client experience, so asked the user to choose or leave A/B open.

**User choice (via question function):** Choose server-rendered monolith (A) for the first release. This is the architecture decision for the ADR draft. Supabase Auth, shared PostgreSQL, and the prior 90-day retention choice remain constraints. The assistant will revise ADR-001 to match, preserve other inherited assumptions as labeled, and leave unresolved security, recovery, and operational details explicit for user review.

### ADR revision 1

**Assistant:** Revised `ADR-001-onesport-architecture.md` to select a server-rendered monolith with one PostgreSQL service and Supabase Auth. Removed the gateway and service deployment decisions, added a server-rendered request/data-flow diagram, and compared the server-rendered monolith, SPA + modular monolith, and microservices on benefits and costs. Preserved the user's 90-day retention choice and marked recovery/relationship handling open. Labeled admin-managed content and no payment processing as inherited assumptions, not requirements confirmed in this discussion. Kept cache behavior, auth/session flow, hosting, and availability/scaling thresholds explicit as open questions.

**Assistant:** Requested user inspection of the revised ADR's accuracy, structure, trade-offs, inherited assumptions, and open questions. Awaiting review before making further revisions.

**User review (via question function):** The draft looks accurate. The user asked to expand the diagram/table and adjust open questions, without yet specifying which visual details or question wording should change.

**Assistant:** Asked for specificity so the next revision reflects the user's intent rather than inventing architecture details: which interactions or boundaries to show, and which open-question topics to add/remove/reword.

**User direction (via question function):** Expand the overview for request/data flows, deployment view, trust boundaries, and comparison criteria. The user did not answer which open-question topics to adjust. The assistant will retain the current unresolved questions rather than silently changing their substance.

### ADR revision 2

**Assistant:** Expanded the component table with browser and trust/deployment boundaries; updated the Mermaid diagram to show external actors, managed identity, logical in-process modules, PostgreSQL ownership, and optional cache; added a flow table for sign-in, browsing, saving, social actions, and deletion; expanded the architecture comparison to cover request/data consistency, scaling/failure behavior, implementation/operations, and selection rationale. Left open questions intact because the requested changes to them were unspecified.

**Assistant:** Requested another review to confirm the expanded overview is useful and whether the unresolved-question section needs any specific additions or wording changes.

**User review (via question function):** The expanded diagram and comparison table meet expectations. The user asked to reword the existing open questions, not to resolve them.

**Assistant:** Changed ADR status to indicate the architecture is selected while implementation questions remain. Rephrased all eight open questions for clarity without deciding them. The ticket-payment question now explicitly notes the difference between the system-description overview (which mentions purchasing tickets) and the user stories (viewing/saving tickets), and preserves the previous ADR's no-payment scope as unconfirmed context.

**Assistant:** Asked for final confirmation that the reworded open questions preserve the intended unknowns and that the ADR is ready as a proposed decision.

**User confirmation (via question function):** The reworded open questions are accurate, and ADR-001 is ready as a proposed decision.

## Task 2: ADR revision

ADR-001 has been revised based on the user's architecture choice and review iterations. The user confirmed the final proposed decision and wording. Implementation and policy questions in the ADR remain open by design.

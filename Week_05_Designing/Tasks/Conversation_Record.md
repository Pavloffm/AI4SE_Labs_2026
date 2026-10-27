# OneSport — Conversation Record

## Requirements reviewed

**Assistant:** I read `data/OneSport.txt`. OneSport needs user signup/login/logout, profile and credential updates, account deletion, recent news and upcoming sporting tickets filtered by country, saved news/tickets, and user search/friend requests/friend lists. The specification says tickets can be collected “to purchase them later,” but does not specify payment processing or the sources of news and event data. Those are open questions, not assumptions to silently bake into the design.

## Three architectural proposals

**Assistant:** I proposed three architectures with different operational and implementation trade-offs:

1. **Server-rendered modular monolith.** A single application serves pages and implements account, content, saved-list, and social functionality. A relational database stores application state; provider adapters isolate external news/event sources. This is the simplest to deploy and lets operations such as accepting a friend request and creating a friendship run in one database transaction. The trade-offs are less client-side interactivity by default and the risk of modules becoming tangled if boundaries are not maintained. External-provider latency may affect page requests.

2. **SPA plus modular backend API.** A browser client calls a JSON API; one backend deployment contains account, news/events, saved-item, and social modules. The database remains the source of truth, and provider adapters keep third-party details out of the client. This gives a clean client/server boundary and can support additional clients later. The costs are additional API and UI plumbing, client loading/error states, authentication/session design, and the need to avoid duplicating business rules in the client. The server must enforce access controls—for example, a user may only edit their own saved lists.

3. **Microservices with asynchronous integration.** Accounts, content ingestion, collections, and social connections are separate deployable services, potentially communicating through a broker for updates and events. Teams can deploy and scale services independently, and ingestion can retry without blocking account functions. However, this adds substantial operational complexity: service-to-service authentication, broker operations, observability, retries, duplicate-message handling, and partial failures. A flow such as sending and accepting a friend request crosses service boundaries, making consistency more difficult than in a single database transaction.

**Assistant:** My initial recommendation was the SPA plus modular backend if an interactive client or additional client types matter; otherwise the server-rendered monolith is the simpler starting point. I would not choose microservices without a concrete scaling or team-ownership reason. I asked which option seems most appropriate and what its biggest trade-off is, and whether ticket purchase means saving links or processing payment. Those questions are still open in the conversation.

## Cost-conscious scaling goal

**User:** “I want to make project in way that it will be possible to scale up it when there will be more users, but first version must be economic and use aall resources in intelegent way.”

**Assistant:** That goal favors an **evolutionary modular monolith** for the first version rather than starting with microservices. Keep domain boundaries clear (accounts, content, saved items, social features), so parts can be separated later if a real need appears. Start with one application deployment and a managed relational database sized for initial demand; keep the app stateless so multiple instances can later run behind a load balancer. This avoids spending early effort on service discovery, message-broker operations, and distributed consistency before usage justifies them.

The important caveat is that “scale-ready” does not mean designing for unlimited scale on day one. Likely pressure points should be measured: database queries and indexes, external sports/news provider rate limits and latency, and any media or content-fetching work. If those become bottlenecks, scale the specific part—for example, cache frequently requested public content, move provider refreshes to a background worker, or add application instances—rather than splitting every feature into a service preemptively. Each optimization has a cost: caching creates freshness/invalidation decisions, background jobs need retries and duplicate-safe processing, and more app instances do not fix a saturated database.

**Assistant:** I asked where the news and event content should come from: external API, admin entry, both, or undecided.

**User:** “Admin entry.”

**Assistant:** Admin-entered content avoids a third-party API dependency, its possible usage fees, and rate limits for the first version. It does mean building an admin workflow and access controls, and it shifts the operational work of keeping content current to the project team. For this scale-conscious first release, admin entry makes the ingestion architecture simpler; public content can still be served efficiently from the application/database, and an external provider can be considered later if manual updates become the bottleneck.

**Assistant:** I asked what “collect tickets to purchase later” means in the first version: saving ticket links, selling tickets with payment checkout, or leaving it undecided.

**User:** “Save ticket links.”

**Assistant:** That keeps OneSport out of payment processing initially. The system needs event/ticket records and each user’s saved-ticket collection, but not payment credentials, order state, refunds, or payment-provider integration. The application should make clear that purchase happens elsewhere. This keeps the first release smaller and cheaper while leaving actual ticket sales as a separate future product decision.

**Assistant:** I asked whether the first version should use email/password, external sign-in, or leave authentication undecided.

**User:** “Email + password.”

**Assistant:** Email/password fits the existing signup, login, credential-change, and account-deletion stories without an identity-provider dependency. The low-level security work is not optional: passwords must be stored using a password-hashing function (never as plaintext or reversible encryption), credential changes should verify the current user, and sessions must be invalidated appropriately on logout, password change, and account deletion. Account deletion also needs a defined policy for related saved items and friend relationships. This approach avoids provider fees but means OneSport owns password recovery and account security.

**Assistant:** I asked whether first-release priority should be lowest operating cost, high availability, or a balance.

**User:** “Balanced.”

**Assistant:** A balanced launch can use one stateless application deployment and a managed relational database with automated backups, plus basic health/error monitoring. Keep the app capable of running multiple instances, but defer redundant app instances and advanced infrastructure until uptime requirements or measured traffic justify them. A single app instance still creates an availability risk; backups protect data recovery, not uninterrupted service. The choice is to accept that limited risk initially while preserving a straightforward scale-out path.

**Assistant:** I asked what should be prioritized as usage grows: more app instances, news/event traffic, social features, or measuring first.

**User:** “More app instances.”

**Assistant:** That is a workable scale-out target if the application is stateless: any instance should be able to handle any request. The low-level implication is that sessions cannot exist only in one instance’s memory; otherwise a request routed to another instance may lose the login. Options include a shared session store or signed, stateless tokens, each with security and invalidation trade-offs. The database and any local file storage also need to be shared rather than tied to one instance. Adding app copies improves request capacity only while shared dependencies can keep up.

**Assistant:** I asked which session approach was preferable for multiple instances: a shared session store, signed tokens, or asking for a recommendation.

**User:** “Shared session store.”

**Assistant:** A shared session store is a reasonable fit because logout and session revocation are direct: delete or invalidate the server-side session. It adds a shared dependency that needs availability and backup/expiry considerations, and each authenticated request needs a session lookup. To keep the first version economical, we should use a session store only if the chosen hosting setup does not already provide an appropriate shared mechanism; avoid adding a separate service prematurely. Regardless, secure cookie settings and session ID rotation after login are important.

**Assistant:** I asked what should happen to saved news, saved tickets, and friend connections when an account is deleted.

**User:** “Keep anonymized content.”

**Assistant:** That requires separating content that belongs to OneSport from identifying account data. News and event records are public/admin-managed content and generally should not be deleted just because a user account is removed. User-owned saved-list entries and friendship/request records contain user relationships; we need to decide whether to remove them or replace identity references with a non-identifying deleted-user marker. “Anonymize” must be defined carefully: removing a display name alone may not remove identifying email, profile fields, or linkable identifiers. We should preserve only data needed for product integrity, avoid retaining credentials/contact details, invalidate sessions immediately, and document a retention policy. In a relational database, this can mean a deliberate account-deletion transaction/job and foreign-key rules rather than indiscriminate cascading deletes.

**Assistant:** I asked why anonymized information should be retained: public content, relationship history, user collections, or an undecided purpose.

**User:** “Keep user collections.”

**Assistant:** Then the intent is to retain a deleted user’s saved-news and saved-ticket collection without retaining a link to their identity. We should question whether that has product value if the former user cannot access it and it is not needed for aggregate reporting. If retained, a design might remove the account’s identifying fields and detach or pseudonymize the collection owner, but pseudonymous IDs can still be linkable and therefore may not be truly anonymous. The policy should name the purpose and retention period; otherwise deleting those private collection rows may be simpler and more privacy-preserving.

**Assistant:** I asked who should be able to view retained collections after deletion: no one, friends, the public, or delete the collections.

**User:** “No one.”

**Assistant:** If nobody can view them, retaining private collection records has limited user-facing value and increases privacy/storage burden. I asked whether to delete them, retain temporarily, or retain indefinitely.

**User:** “Retain temporarily.”

**Assistant:** That means account deletion should remove identifying data and revoke sessions immediately, while placing detached collection data on a defined deletion schedule. A scheduled cleanup can delete expired records in batches. Low-level concerns include ensuring the detached rows cannot be looked up through the deleted account, handling failures/retries safely, and making backups’ retention policy consistent with the promise. We still need to choose the retention duration and a concrete reason for keeping the collections during that window; without a reason, immediate deletion is simpler.

**Assistant:** I asked how long to retain anonymized collections before automatic deletion.

**User:** “90 days.”

**Assistant:** I recorded a 90-day retention window as the current decision. Before implementation, the product should still document why the temporary retention is needed, what fields are removed at deletion time, and how backup expiry aligns with the 90-day promise. A cleanup job must reliably remove expired collection rows; a daily idempotent batch job is likely sufficient at first, rather than a separate service.

**Assistant:** I asked what client should be supported first: responsive website, website plus mobile apps, or undecided.

**User:** “Responsive website.”

**Assistant:** That keeps the initial client scope focused. It does not by itself require a separate SPA and API: a server-rendered modular monolith can provide a responsive website with fewer moving parts, while an API can still be introduced for specific interactive needs or future clients. The architectural decision should be driven by the desired interaction model, not by responsiveness alone.

**Assistant:** I asked whether the responsive website should use simple page flows, an app-like interface, or a recommendation.

**User:** “App-like interface.”

**Assistant:** That makes a SPA client with a modular backend API a better fit than simple server-rendered pages. We can still keep the backend as one deployable modular monolith; choosing an SPA does not force microservices. The extra cost is frontend/API coordination and client-side loading, error, and authentication states. This is a deliberate interaction-quality trade-off against the lower complexity of server-rendered pages.

**Assistant:** I asked what privacy rule should apply when users search by email and see another user’s details.

**User:** “Minimal public profile.”

**Assistant:** Then email should be used as a lookup key but not returned as profile data. Search results should expose only an explicitly approved minimal set (for example, display name and perhaps avatar), and every lookup must be authorized on the server. We should also consider rate limiting and generic responses so the endpoint cannot be abused to enumerate which email addresses have accounts. This is a privacy and abuse-control requirement, not just a UI choice.

**Assistant:** I asked whether accepting a friend request should create a mutual friendship or a one-way follow.

**User:** “Mutual friendship.”

**Assistant:** With mutual friendship, acceptance must make both users appear in each other’s lists. In the initial relational database, this can be represented as one canonical friendship row with a uniqueness rule on the normalized user pair, rather than two unrelated rows that could get out of sync. Accepting the request should atomically mark the pending request accepted and create that friendship. Database constraints and a transaction protect against duplicate requests or two near-simultaneous acceptance attempts. This is one reason the social feature is simpler to implement inside a single modular backend than across separate services.

**Assistant:** Based on the choices so far, I asked which architecture to use: SPA plus modular monolith, server-rendered monolith, or microservices.

**User:** “SPA + modular monolith.”

**Assistant:** This fits the app-like responsive UI while keeping deployment and data consistency simple. Version one can have a SPA calling one backend API deployment, logically divided into account, content/admin, saved collections, and social modules, backed by a relational database. Make the API instances stateless and use a shared session store so they can later be replicated behind a load balancer. Avoid microservices initially; split a module only if measured scaling, reliability, or team-ownership needs justify the added distributed-systems burden.

**Assistant:** I asked what the main reason is to start with one modular backend instead of microservices, offering less operations overhead and easier transactions as the trade-offs.

**User:** “Let's use microservices.”

**Assistant:** The user has changed the architecture preference to microservices. This is recorded as a preference, not assumed to be a settled decision: it conflicts with the stated goal of an economical first version and introduces more operations and distributed consistency work. I will clarify what concrete benefit is motivating the change before recommending service boundaries or deployment details.

**Assistant:** I asked for the main motivation: independent scaling, independent deployment, a learning goal, or future-proofing.

**User:** “Independent scaling.”

**Assistant:** Independent scaling can be valuable when one workload genuinely grows much faster than others. For OneSport, public news/event browsing may be read-heavy, while social writes and admin content entry may be comparatively light. But separate service deployments do not automatically make the system cheaper: each service has a baseline footprint, and shared database capacity or provider constraints can remain the bottleneck. We should identify which workload is expected to dominate and whether caching or additional stateless instances of a modular backend would address it more economically.

**Assistant:** I asked which workload is expected to need more capacity: news/events, social features, all features equally, or unknown.

**User:** “News and events.”

**Assistant:** That is the strongest candidate for a separate scaling boundary because browsing is likely read-heavy. Before splitting it into a service, consider whether a CDN/cache for public listings, suitable database indexes, and scaling the web/API instances would meet the need with less operational cost. If a separate content service is still justified, keep it focused on admin-managed news/events and public read APIs; do not split account, collections, and social features merely to claim a microservices architecture. Be aware that the content service still needs its own deployment, health monitoring, and data ownership rules, and saved-ticket/news references must remain stable across services.

**Assistant:** I asked whether to cache first, separate the content service, or defer the choice until after launch.

**User:** “Cache first.”

**Assistant:** That matches the cost-conscious goal and leaves microservices as a possible later step rather than a day-one requirement. Since admins enter the content, the main cache trade-off is freshness: an edit may remain invisible until its cache entry expires unless the admin update also invalidates that entry. A short time-to-live is simpler but permits brief staleness; explicit invalidation is fresher but adds coordination and failure cases. Cache only public/read-heavy data first, measure hit rate and database load, and avoid caching user-specific collections in a shared public cache.

**Assistant:** I asked how fresh admin-edited listings must be: within minutes, immediately, or undecided.

**User:** “Within minutes.”

**Assistant:** A short cache TTL is sufficient for that requirement and avoids coupling every admin write to cache invalidation. The trade-off is bounded staleness: users may briefly see the old listing after an edit. The initial cache policy should state the TTL and be revisited if the editorial requirement changes. Cache-hit rate, response latency, and database load can show whether the cache is helping.

**Assistant:** I asked which cost the short-TTL cache accepts.

**User:** “Brief stale results.”

**Assistant:** Correct. The short TTL trades immediate freshness for simpler caching; a listing may remain stale for a few minutes, then refresh automatically. The cache should not be treated as the source of truth—the relational database remains authoritative.

**Assistant:** I asked which data store seemed safer for accounts, saved lists, and friendships, but the user redirected the discussion to architecture.

**User:** “Let's go to discuss architecture.”

**Assistant:** I offered to return to comparing the modular monolith, SPA with modular backend, and microservices.

**User:** “mircoservices” (microservices).

**Assistant:** I acknowledged microservices as the architecture the user wants to explore, while leaving the final implementation decision open until its concrete decomposition and trade-offs are understood.

**Assistant:** I outlined identity/account, content, collections, and social services behind an API gateway. I explained that saved content must reference IDs owned by another service, so database foreign keys cannot enforce those references, and asked whether each service should own its database or share one.

**User:** “Database per service.”

**Assistant:** This is consistent with genuine microservice ownership: account data stays with identity, news/events with content, saved references with collections, and requests/friendships with social. The trade-off is that a single SQL join cannot produce a user's saved-ticket list with full event details. The collections service can return saved content IDs, then the API layer can request details from content; this adds a network call and requires behavior for deleted/unavailable content. Cross-service reports likewise need API composition or asynchronously maintained read models. Friend-request acceptance remains easier because request and friendship state belong together in the social service and can be updated in its local transaction.

**Assistant:** I asked how services should communicate: HTTP APIs, a message broker, or both.

**User:** “HTTP APIs.”

**Assistant:** HTTP request/response is the simpler initial integration pattern: the SPA/API gateway can call the responsible service and receive a result immediately. Its painful edge is availability coupling. If the collections endpoint calls content to expand saved IDs and content is down or slow, the page may be delayed or fail. Calls need timeouts and bounded retries (not endless retries), and the API should decide whether to return saved IDs with missing details or fail the whole response. HTTP does not provide a transaction across services; keep operations such as friendship acceptance inside one owning service. A broker can be considered later for non-immediate work, but is not required solely to call these services.

**Assistant:** I asked what to do if content is temporarily unavailable while loading saved items.

**User:** “Use cached details.”

**Assistant:** This improves availability, but the cache must have an owner and a freshness rule. A content-service cache (or shared edge cache for public content) can serve public news/event details while the content database/service is unavailable. Keep the user's private saved IDs in the collections service and do not put personalized collection responses into a shared public cache. Cached details can be stale, and an event may have been edited or removed; responses should indicate or tolerate stale/missing details rather than treating the cache as authoritative.

**Assistant:** I asked how the UI should handle stale cached event details.

**User:** “Hide stale data.”

**Assistant:** Then cached details should only be served as a fallback while they remain within a defined freshness window. Beyond that window, hide the stale detail rather than presenting it as current. This protects users from outdated event information but reduces the availability benefit during longer outages; the saved item may need a neutral “details temporarily unavailable” state so the user can distinguish a hidden detail from a deleted saved item. The exact freshness window still needs a decision.

**Assistant:** I asked for the cache freshness window during a content outage.

**User:** “15 minutes.”

**Assistant:** I recorded that cached details may be shown for up to 15 minutes during an outage, then hidden as stale. This is a separate policy from the normal cache TTL for reflecting admin edits; the two may be aligned or separately configured, but their meanings should not be confused.

**Assistant:** I explained that account deletion spans independently owned databases, so HTTP calls cannot make it one atomic transaction. I asked how to handle an unavailable service during deletion.

**User:** “Track and retry.”

**Assistant:** The identity service will own the deletion workflow. It disables login and revokes sessions immediately, persists progress, and calls collections/social cleanup operations that are safe to retry. Persisting progress matters: if the service restarts during an outage, a worker can resume instead of losing the workflow state.

**Assistant:** I proposed three deployables (identity, content, combined collections/social) versus four (separate collections and social) and asked which to explore.

**User:** “Three services.”

**Assistant:** The current candidate split is therefore **identity**, **content**, and **user features** (saved collections plus friend requests/friend lists), each with its own database. This reduces deployments and network boundaries compared with four services. The user-features service now owns both saved-item and social rules; keep these as internal modules with clear tables/API boundaries so they can be split later if measurements show different scaling needs. The API gateway is an entry/routing layer, not necessarily a domain service or a fourth data-owning service.

**Assistant:** I asked whether to deploy the three services on one small host or use managed containers.

**User:** “Managed containers.”

**Assistant:** Managed containers support independent service replicas and avoid managing the host/cluster yourself, but usually have more baseline cost and platform configuration than one small host. Each service needs health checks, resource limits, logs, secrets, and deployment configuration. Independent scaling is useful only if the platform permits the services to scale separately and their databases/caches can keep up. A low-cost initial setup could run one small replica per service, then add replicas for content after measuring read load; single replicas still mean each service can be temporarily unavailable during a failure or deployment.

**Assistant:** I asked whether each service should have a separate database instance or separate databases on one shared managed cluster.

**User:** “Shared DB cluster.”

**Assistant:** This keeps service-level data ownership while reducing infrastructure cost: use distinct databases (or at least distinct schemas) and credentials per service on the same managed cluster. The compromise is shared CPU/storage and a shared failure domain; a noisy workload can affect the others, and the cluster cannot scale identity/content independently. Enforce ownership by granting each service credentials only to its own database and making cross-service reads go through HTTP APIs, never direct table access. If content traffic later dominates, move its database to dedicated capacity without changing its service API.

**Assistant:** I asked how the SPA should authenticate to backend services.

**User:** “Gateway sessions.”

**Assistant:** The SPA can use a secure session cookie with the gateway. Identity authenticates the user and establishes/revokes the session; the gateway validates it and forwards a trusted user identity to internal services. The cookie should be Secure, HttpOnly, and appropriately SameSite; state-changing requests need CSRF protection if cookie authentication is used. Services should not trust user-ID headers from the public internet: they should only be reachable through the gateway/private network and/or authenticate gateway-to-service calls. The gateway is now security-critical and needs more than one replica for high availability when traffic grows.

**Assistant:** I asked where to compose a saved-list response across user-features and content services.

**User:** “Gateway composes.”

**Assistant:** The gateway can make one client-facing request, fetch saved IDs from user-features, fetch public details from content, and combine the result. This keeps the SPA simpler, but the gateway now owns response aggregation and partial-failure behavior. It must use bounded timeouts, avoid unbounded fan-out, and return a clear partial result if content details cannot be fetched or are beyond the 15-minute stale-data window. Keep domain rules in their owning services; the gateway should compose data, not decide friendship or collection policy.

**Assistant:** I asked what the main gateway-composition risk is.

**User:** “Gateway becomes critical.”

**Assistant:** Correct. All SPA API traffic depends on the gateway, so it is a critical path and potential bottleneck. Mitigations include keeping it stateless, running multiple replicas behind the platform's load balancer, health checks, and monitoring latency/error rates. That reduces single-instance failure risk but does not remove the gateway as a shared dependency; it also adds baseline cost for redundant replicas.

**Assistant:** I asked whether to start with one gateway replica, two, or autoscale later.

**User:** “One initially.”

**Assistant:** That minimizes first-release cost, but accepts gateway downtime if that replica fails or is redeployed. It is an explicit availability trade-off; use health checks and automatic restart, and add a second replica when the uptime requirement or observed traffic warrants it. Because the gateway is critical, this should be documented rather than mistaken for high availability.

**Assistant:** I asked where the public news/event cache should live once content has multiple replicas.

**User:** “Shared cache.”

**Assistant:** A shared cache means content replicas see the same entries and avoids repeating database reads independently. It adds another network dependency and operating cost, so it should only be introduced when caching is needed; set a short TTL to meet the “within minutes” freshness need. If the shared cache is unavailable, the content service should be able to fall back to its database with load protection, otherwise a cache outage itself becomes a content outage. The cache remains disposable: the database is authoritative.

**Assistant:** I asked whether content should fall back to its database during a cache outage.

**User:** “Yes, with limits.”

**Assistant:** That preserves availability while protecting the database from an unlimited traffic surge. The content service should cap concurrent fallback reads and monitor database load; requests beyond safe capacity may need a clear temporary error rather than overwhelming the database. This is another operational setting to tune with load testing, and it demonstrates that caching reduces load but also creates failure-mode behavior to implement and verify.

**Assistant:** I asked which microservices topic to explore next.

**User:** “Failure handling.”

**Assistant:** I described deadlines for service calls, bounded retries only when safe, cache fallback within the 15-minute freshness rule, and durable retries for account-deletion cleanup. I asked how the gateway should respond after a content request times out.

**User:** “One retry, then cache.”

**Assistant:** For idempotent content reads, one bounded retry is a reasonable compromise. If it still fails, use cached content only while it meets the 15-minute freshness limit; otherwise return an unavailable-details result. The retry should have a short timeout and not be applied indiscriminately to writes, because repeating a non-idempotent operation can create duplicate saved items or requests. During a broader outage, a circuit breaker can stop repeated calls temporarily, but it adds state/tuning and should be introduced only when needed.

**Assistant:** I asked how to prevent duplicate writes if a request is retried.

**User:** “Idempotent endpoints.”

**Assistant:** Good fit for these operations: saving an item can be an “ensure saved” operation backed by a unique constraint on `(user_id, content_id)`, so repeating it does not create duplicates. Removing an already-removed item can still succeed as the desired end state. Friend-request creation similarly needs a normalized sender/recipient pair and rules against duplicate or contradictory pending requests. The database constraint is important because application-level “check then insert” alone can race under concurrent requests.

**Assistant:** I asked what should happen if accepting and deleting the same friend request happen concurrently.

**User:** “First committed action wins.”

**Assistant:** The social/user-features service can implement this with a conditional update from `pending` to `accepted` or `deleted` inside a database transaction. Only one update succeeds; the other sees that the request is no longer pending and returns the current state or a conflict response. This keeps the concurrency rule local to one service and avoids distributed locking.

**Assistant:** I explained that saved lists store content IDs rather than duplicate content fields, and asked what should happen if an admin removes an event.

**User:** “Keep as unavailable.”

**Assistant:** That preserves the user's saved reference without making collections responsible for deleting content-owned records. The content service can return “not found/removed”; the gateway should render an unavailable tombstone and let the user remove the saved reference. This avoids cross-service cleanup coordination, at the cost of retaining stale IDs until users remove them or a later cleanup policy is added.

## Final architecture questions and decisions

**Assistant:** I asked five remaining questions about service-to-service security, normal content cache TTL, the purpose of 90-day collection retention, database recovery, and content-service scale triggers.

**User:**
- Service security: “Private network + credentials.”
- Content cache TTL: “5 minutes.”
- Retention purpose: “Undo window.”
- Database recovery: “Managed backups.”
- Scale trigger: “Measured thresholds.”

**Assistant:** These choices make the candidate design more concrete: keep services on a private network and authenticate internal calls; use a five-minute normal cache TTL, while the separate outage policy allows cached details up to 15 minutes; use managed database backups and tested restores; and add content replicas based on observed latency, errors, CPU, and database load rather than user-count guesses.

The “undo window” needs one important clarification before implementation: if account recovery is possible during the 90 days, the system must retain some secure way to reconnect the collections to the account. That is pseudonymization/reversible deletion, not full anonymization. The retention promise and account recovery behavior must be designed together and explained to users.

**Assistant:** This is the safer microservices approach. Disable the account and revoke sessions immediately; record a deletion workflow with per-service cleanup status; call collections and social with idempotent deletion/anonymization operations; and retry incomplete steps with bounded backoff until complete. Idempotence matters because a timed-out HTTP request may have succeeded even though the caller never received the response. The workflow must avoid logging sensitive data and must report completion only after required cleanup finishes. This is saga-like orchestration, and is notably more code and testing than a single-database account deletion transaction.

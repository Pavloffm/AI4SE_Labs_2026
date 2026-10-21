# Refined Software Requirements

Input corpus: `Task_1/data/corpus`

## Priority scale

- **Must**: explicitly mandatory/high priority, or clearly essential to critical operations.
- **Should**: supported by meaningful stakeholder need or operational impact, but not established as mandatory.
- **Could**: useful enhancement with comparatively lower urgency/impact.
- **Unspecified**: evidence is insufficient for a responsible priority assignment.
Inferred priorities are identified as such in each requirement’s basis.

## Requirements

### REQ-001: Management reporting scope and OPAC boundary

The system shall support management planning, evaluation, and oversight for collections, material use, branch capacity and distribution, patron demographics, staff productivity and workflow, and financial transactions. It shall exclude day-to-day patron-facing functions handled by the OPAC and circulation client and shall not constrain OPAC functionality or performance.

- **Priority:** Must — Formal scope and OPAC non-constraint statements use mandatory language.
- **Sources:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`
- **Evidence:** The requirements focus on management processes and exclude day-to-day patron-facing functions.; The reporting system must not constrain or slow the OPAC.

### REQ-002: Consortium-scale and multi-location operation

The system must support a consortium with 286 locations, approximately 17 million annual circulations, and purchasing or processing more than 900,000 items annually. Management processes operate centrally while accepting input from and serving multiple locations.

- **Priority:** Must — The stated scale uses must or shall language; centralized multi-location operation is an explicit assumption.
- **Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`
- **Evidence:** The system must support 286 locations, 17 million annual circulations, and more than 900,000 items processed annually.; Management Processes are consolidated centrally and serve multiple locations.

### REQ-003: Supported platforms, clients, accessibility, and HTML

The system must operate on Linux or Solaris and be accessible through a web browser or Windows-compatible client, including the specified legacy browser versions where applicable. It must support assistive technologies, Section 508 accessibility, and standards-compliant accessible HTML.

- **Priority:** Must — Platform, accessibility, and HTML requirements use mandatory language; Section 508 compliance is described as mandatory.
- **Sources:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`
- **Evidence:** The system must operate on Linux or Solaris.; It must support screen readers, screen magnification, and other assistive technology.; The system must produce standards-compliant HTML.

### REQ-004: Relational ILS and vendor data integration

The system must use and query the enterprise relational ILS, including acquisition, cataloging, item, patron, hold, and transaction data. It should interface with vendor systems through published APIs or standard-format files such as USMARC21 and EDIFACT, without assuming every library has every vendor data source. Reporting reads ILS and OPAC data rather than modifying acquisition, cataloging, or OPAC transaction data.

- **Priority:** Must — The relational backend is mandatory; integration and read-only boundaries are explicit dependencies and constraints.
- **Sources:** `early_draft_srs_galecia.txt`, `meeting_tech_subcommittee_2009-06-30.txt`
- **Evidence:** The system must use a fully relational database backend.; The reporting system reads, but does not manage or modify, acquisition, cataloging, or OPAC data.; Vendor interfaces may use APIs or standard-format files.

### REQ-005: Role- and group-based access control

The system must control rights through security groups and roles for individuals, workgroups, and arbitrary staff groups. Administrators should manage fine-grained permissions for reports, templates, queries, data sets, transfer functions, and purge functions, with permission changes manageable through role reassignment where applicable.

- **Priority:** Unspecified — The requirement itself is consistently supported, but the corpus conflicts on whether the overall priority is Must or Should.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`
- **Evidence:** Rights and privileges will be controlled through security groups and/or roles.; The permission system is described as essential.; Fine-grained permissions are requested for report creation, cloning, running, and data access.

### REQ-006: Staff authentication and audit identity

The system should support individual username/password login and may support an optional streamlined method such as employee-card swipe. Streamlined login must not be required or bypass individual authentication, and the system must identify the individual staff member for auditing.

- **Priority:** Must — Individual identity and auditability use mandatory language; streamlined login availability is explicitly optional.
- **Sources:** `early_draft_srs_galecia.txt`, `email_staff_login.eml`
- **Evidence:** The system must track which staff member is logged in for audit purposes.; Card login must not bypass individual authentication.; Traditional username/password login remains available as a fallback.

### REQ-007: Development, training, and production migration

The system must provide separate development and training environments and support migration of report templates, permissions, saved queries, and other configurations into production. Training must protect production data and permit safe experimentation.

- **Priority:** Unspecified — The corpus contains both shall or Must evidence and Should evidence for this requirement.
- **Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`
- **Evidence:** Development and training environments must support migration to production.; The training environment must not risk production data.; Export/import of templates, permissions, and saved queries is requested.

### REQ-008: Non-disruptive report execution

Searches and reports must run during open hours without disrupting live operations or slowing the OPAC. Queuing, background processing, a separate reporting database, or a read-only replica may be used, but no particular architecture is accepted by this requirement.

- **Priority:** Unspecified — OPAC non-constraint is mandatory, while open-hours non-disruption is described as highly desirable or Should.
- **Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`
- **Evidence:** Reports must not constrain the OPAC.; Reports should be processable during open hours without disrupting other functions.; Background processing and reporting replicas are proposed alternatives.

### REQ-009: Report construction, templates, queries, and reuse

The system should provide canned, on-demand, and open-template reporting; administrator-created templates that staff can run as-is or modify only within permitted filters and display fields; report cloning; saved and reusable queries; ad hoc querying across supported record types; Boolean and regular-expression filtering; and text-file filtering using barcode or TCN lists.

- **Priority:** Should — These capabilities are repeatedly requested without consistent mandatory wording.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`
- **Evidence:** Administrators should create templates that staff can run or modify.; Users need cloning and saved-query reuse.; Users should be able to use Boolean operators, regular expressions, and uploaded barcode or TCN lists.

### REQ-010: Report permissions and shared folders

Administrators should control who may create, clone, run, or modify reports and which filters, fields, tables, and data sets are available. Shared report folders should grant or restrict access to particular reports and ad hoc reporting.

- **Priority:** Should — Explicitly supported by specifications, interviews, and survey responses without consistent Must wording.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `survey_results_2009.txt`
- **Evidence:** Fine-grained permissions should distinguish report creation, cloning, running, and ad hoc access.; Shared folders should control report access.; Administrators should restrict editable filters and display fields.

### REQ-011: Report output and result transparency

Reports should support Excel, HTML, and CSV output. Results should display the report name and query selections or criteria used and include null and blank fields. Pivot tables, comparative columns, period-over-period percentages, and MARC fields on a single row remain requested presentation capabilities.

- **Priority:** Must — Output formats, criteria display, and null or blank inclusion have explicit mandatory evidence; additional presentation features have weaker support.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`
- **Evidence:** Excel, HTML, and CSV formats are required.; All nulls and blank fields must be included in results.; Query selections should be shown with results.

### REQ-012: Report scheduling and queue management

The system should support immediate and recurring report runs, configurable schedules including hourly through yearly intervals, simultaneous selection of multiple reports, queue position and status visibility, and prioritization of important reports. Cancellation of scheduled or running reports remains proposed but unconfirmed.

- **Priority:** Should — Scheduling, visibility, and prioritization are repeatedly supported; cancellation has conflicting evidence and is not asserted as settled.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`
- **Evidence:** Users need queue position, submission time, and waiting, running, completed, or failed status.; Reports should support immediate and recurring schedules.; Important reports should be able to move ahead in the queue.; Cancellation is requested and separately described as technically feasible.

### REQ-013: Historical and real-time reporting

The system should support current or real-time reports and historical reports for a specified date or date range, including historical bills and other historical values where supported by retained data. A reporting warehouse or equivalent may be needed, but the architecture is not settled.

- **Priority:** Should — Temporal reporting is repeatedly identified as a need; warehouse architecture is only proposed.
- **Sources:** `early_draft_srs_galecia.txt`, `evergreen_reference_2009.txt`, `meeting_tech_subcommittee_2009-06-30.txt`, `survey_results_2009.txt`
- **Evidence:** Reports must support real-time and historical data.; A snapshot bills report and historical values are requested.; A reporting warehouse is proposed for research, not approved.

### REQ-014: Online help and diagnostic feedback

The system must provide an online, hierarchical, cross-linked, searchable HTML help system that supports screen readers and describes system functions. It must provide high-level error reporting and low-level, query-specific administrator feedback identifying report failures where possible.

- **Priority:** Must — Formal specifications use must or shall language for help and error feedback.
- **Sources:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_tech_subcommittee_2009-06-30.txt`
- **Evidence:** The help system must be online, hierarchical, cross-linked, and in HTML.; Administrators need query-specific feedback rather than generic failure messages.

### REQ-015: Material volume reporting

The system should report material volume for a specified library and point in time, with date filtering for historical comparisons. Reports should separately count new acquisitions, items on shelf or checked in, items in circulation or checked out, and totals, with configurable category breakdowns such as total items, holds, adult fiction, and board books.

- **Priority:** Should — The corpus repeatedly identifies this capability but provides no explicit Must priority for the requirement as a whole.
- **Sources:** `conversations/conv_pines014_material_volume.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** Volume must be reportable at any point in time.; The report should distinguish acquisitions, shelf holdings, and circulating items.; Categories should be customizable.

### REQ-016: Branch capacity overview

The system should provide a high-level overview of branch capacity. The confirmed requirement does not define the capacity metric or commit to color coding, drill-down, trend analysis, CSV export, or particular sorting and filtering behaviors.

- **Priority:** Should — A system-wide capacity overview is explicitly stated; other interface details are tentative or unresolved.
- **Sources:** `conversations/conv_pines015_capacity_interface.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** The system should provide an interface showing the capacity of all branches.; The definition of capacity must be clarified before building.

### REQ-017: Collection use and shelf-space comparison

For each genre and format, the system should compare the percentage of total circulations, percentage of collection holdings, and percentage of total shelf space, with views for an individual library and the system as a whole. The comparison is accepted conceptually, but the method for estimating shelf space is unresolved.

- **Priority:** Should — Repeatedly specified collection-management report requirement without mandatory wording.
- **Sources:** `conversations/conv_pines016_shelf_space.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** The report compares circulation, collection, and shelf-space percentages by genre and format.; Views are required per library and per system.; Shelf space is not directly tracked and must be estimated.

### REQ-018: Uncataloged-material inventory and circulation

The system should track uncataloged materials as inventory, support quick distribution with minimal branch labor, identify their use, and count their transactions in circulation statistics and reports.

- **Priority:** Should — Repeatedly requested operational and reporting capability without mandatory wording.
- **Sources:** `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** Uncataloged material must be distributable with minimal labor.; Its use and transactions must be identifiable and reportable.

### REQ-019: Batch item transfer

The system should provide a batch transfer utility for moving selected items between branches or other locations. It should support candidate queries, saved queries, manual selection, location updates, pull lists, transfer history, role restrictions, efficient transaction-safe batching, undo, and preview before applying changes.

- **Priority:** Should — The core workflow and safeguards are explicitly requested; optional labels and alerts are separate.
- **Sources:** `conversations/conv_pines018_item_transfer.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** Staff need to query, select, preview, and move batches of items.; Transfers should be auditable, permission-controlled, transaction-safe, and efficient.; An undo function and pull-list generation are explicitly requested.

### REQ-020: Transfer reversion criteria

The transfer utility should support automatic reversion after a configured time period and may support event- or status-based criteria such as return status or checkout at the destination. Exact trigger semantics remain unresolved.

- **Priority:** Unspecified — Time-based and event/status-based reversion are explicitly requested, but exact automatic behavior is not finalized.
- **Sources:** `conversations/conv_pines018_item_transfer.eml`
- **Evidence:** Reversion is requested after a set period and/or based on other criteria.; Examples include status changes and checkout at the destination.

### REQ-021: Transfer delay and issue alerts

The item transfer utility should notify users if a transfer is delayed or encounters an issue. Notification conditions, recipients, and delivery channel remain unspecified.

- **Priority:** Could — Explicitly requested as an additional feature, but without operational details or broader confirmation.
- **Sources:** `conversations/conv_pines018_item_transfer.eml`
- **Evidence:** “If an item transfer is delayed or has issues, notify me.”

### REQ-022: Missing, damaged, and in-transit reports

The system should provide branch-level missing and damaged item reports and an in-transit report covering branch and system scopes. The in-transit report should combine transit-to and transit-from items and support a configurable age threshold.

- **Priority:** Unspecified — Missing/damaged reporting is repeatedly required; in-transit reporting is called critical in one source but is not consistently prioritized elsewhere.
- **Sources:** `conversations/conv_pines019_020_missing_intransit.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`
- **Evidence:** Missing and damaged reports are required per branch.; The in-transit report covers items older than configurable X days per branch and system.; Transit-to and transit-from must be merged into one report.

### REQ-023: Threshold configuration and defaults

Threshold-based reports shall allow configurable values for inactivity periods and in-transit age. The usual inactivity value may be 365 days, and a 7-day in-transit default was suggested, but these defaults are not confirmed.

- **Priority:** Should — Configurability is explicit; the example defaults are tentative and therefore not made normative.
- **Sources:** `conversations/conv_pines019_020_missing_intransit.eml`, `conversations/conv_pines024_inactive_patrons.eml`
- **Evidence:** The in-transit threshold should be configurable, probably with a 7-day default.; The inactive-patron threshold is configurable; 365 days is the usual value.

### REQ-024: Purge, status conversion, cleanup, and safeguards

The system should identify purge candidates using customizable and combinable criteria; provide read-only candidate reports and separate confirmation before deletion; support batch status conversion; and efficiently delete volumes with copies and records without items. Automatic scheduled purging is not confirmed.

- **Priority:** Should — Core purge and cleanup capabilities are repeatedly confirmed; scheduled automatic purging is only a proposal.
- **Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** Purge criteria must be customizable and combinable.; Candidate reports should be read-only with separate deletion confirmation.; Batch conversion and cleanup of itemless records are requested.

### REQ-025: Last-copy reporting

The system must provide a last-copy report at library-system scope to prevent deletion of the consortium's last copy and support catalog maintenance such as WorldCat updates. An individual-library or facility last-copy view is requested but not confirmed.

- **Priority:** Must — System-level last-copy reporting is explicitly called critical; local scope is unresolved.
- **Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** The last-copy report is called critical and must identify system last copies.; The report would assist catalogers editing WorldCat entries.

### REQ-026: Deletion tracking and audit reporting

The system should count and track item, patron, and other record deletions by location and system, retaining record type, timestamp, deleting user, and user location. It should provide reports grouped by period, location, system, user, and record type.

- **Priority:** Should — These tracking fields and report dimensions are explicitly specified.
- **Sources:** `conversations/conv_pines022_deletions.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** Required details include record type, timestamp, user, and user location.; Reports should summarize deletions by period, type, location, and user.

### REQ-027: Denied deletion-attempt tracking

The system may track deletion attempts that were denied, to support compliance and troubleshooting. Whether denied attempts are in scope is unresolved.

- **Priority:** Could — The capability is explicitly suggested as helpful but is not confirmed as a core requirement.
- **Sources:** `conversations/conv_pines022_deletions.eml`
- **Evidence:** A participant asks whether denied deletion attempts can also be tracked.; The summary describes this as helpful for compliance and troubleshooting.

### REQ-028: Patron-characteristic filtering and grouping

Queries and reports should filter and group by age range, ZIP code, county, home branch, patron type, and preferred language, supporting AND/OR combinations. Age ranges should be configurable per report and derived from birth date at query time. Missing optional characteristics should remain in results as null values.

- **Priority:** Should — Repeated consolidated requirement with explicit technical behavior and no consistent mandatory designation.
- **Sources:** `conversations/conv_pines023_patron_characteristics.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** The listed characteristics must support filtering and grouping.; Age brackets should be configurable and calculated from birth_date.; Null characteristic values should not be silently excluded.

### REQ-029: Inactive-patron reporting

The system should identify patrons with no circulation or defined electronic activity during a configurable number of days and support grouping by system, home library, county, and other levels. Electronic activity includes OPAC or account logins, online holds, and online renewals. Reports should separate patrons with outstanding fines, permit specified exclusions, support CSV export, and allow background processing.

- **Priority:** Should — The report and its principal dimensions are explicitly confirmed; digital-resource access, exact day-input constraints, and caching remain unresolved.
- **Sources:** `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** The inactivity period is configurable.; Specified electronic activity includes logins, holds, and renewals.; Fine separation, exclusions, CSV export, and background processing are requested.

### REQ-030: Inactive-patron mailing addresses

The inactive-patrons report should include current mailing addresses for outreach use.

- **Priority:** Should — The corpus explicitly requests mailing addresses.
- **Sources:** `conversations/conv_pines024_inactive_patrons.eml`
- **Evidence:** The report needs to include current mailing addresses.

### REQ-031: Transaction retention and reporting

The system should retain transaction history for a configurable number of days and retain monthly and annual aggregate information indefinitely, subject to applicable legal retention policies. It should report transactions by hour, terminal, branch, system, patron, library group, and county, with separate and cumulative counts for check-ins, check-outs, renewals, holds, and placement or service channels.

- **Priority:** Should — The retention and reporting rules are explicit; legal data-class retention constraints remain qualified.
- **Sources:** `early_draft_srs_galecia.txt`, `survey_results_2009.txt`
- **Evidence:** Transaction history is maintained for configurable X days while monthly and annual aggregates are maintained indefinitely.; Reports distinguish transaction types and support organizational and time groupings.

### REQ-032: Privacy-preserving demographic and transaction archives

Archived transaction data and demographic statistics must protect patron privacy and exclude personally identifiable information while retaining useful aggregate statistics. Retention must comply with applicable state law and audit policies; any statutory duration not specified by the sources remains unresolved.

- **Priority:** Must — Anonymization and legal privacy compliance use mandatory language.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `survey_results_2009.txt`
- **Evidence:** Demographic statistics must be anonymized.; Transaction archives must protect privacy while supporting demographic statistics.; State law requires retention for an unspecified number of years.

### REQ-033: Financial reporting and account queries

The system should report patron balances by patron, home library, and system; fines and charges by period, branch, and charge type; waived fines by period and branch; and payments by period, branch, payment method, and tender type. It should support balance-threshold queries, joins between patron and item financial data, easy updates, and immediate reflection of front-desk payments.

- **Priority:** Should — These capabilities are repeatedly requested without consistent mandatory wording.
- **Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`
- **Evidence:** Financial reports require the listed balance, fine, waiver, and payment dimensions.; Financial data attached to patron and item records must be joinable.; Front-desk changes should appear immediately.

### REQ-034: Payment audit ledger

The system must maintain a payment ledger linking each patron payment to the specific charge or charges it settled, to support reconciliation.

- **Priority:** Must — The payment ledger is explicitly mandatory and critical.
- **Sources:** `early_draft_srs_galecia.txt`, `email_financial_reports.eml`
- **Evidence:** The system must identify which charges each payment was applied to.; The financial audit trail is called critical.

### REQ-035: Board, executive, operational, data-quality, and expanded reports

The system should provide predefined board and executive reports, annual-report statistics, circulation and hold activity with required cross-tabulations, data-quality reports, and representative operational reports. Report coverage should expand to the additional gaps identified in the reference analysis, including circulation, bibliographic, patron, collection, survey, hold, inactive-patron, aged-debt, and last-copy reports.

- **Priority:** Should — The corpus explicitly identifies these report families and calls for expanded coverage without assigning a universal Must priority.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `evergreen_reference_2009.txt`, `meeting_minutes/meeting_2009-03-15_minutes.txt`
- **Evidence:** Predefined board reports must include required annual-report statistics.; Data-quality and operational report examples are explicitly listed.; The reference conclusion calls for expanding available report types to cover identified gaps.

### REQ-036: Shelf-space estimation method

A method for estimating shelf space must be selected before implementing shelf-space comparisons. Candidate methods include item dimensions or item count as a proxy, but the corpus does not approve either method.

- **Priority:** Unspecified — The need to estimate shelf space is explicit, but the method is an unresolved implementation decision.
- **Sources:** `conversations/conv_pines016_shelf_space.eml`
- **Evidence:** Shelf space is not directly tracked in the database.; The discussion proposes item dimensions or item count as a proxy and assigns investigation.

## Discarded candidates

- **Duplicate-free report exports:** Unsupported as a settled requirement; the source documents a reported problem without specifying when duplicates are erroneous or how uniqueness should be defined. 
  Sources: `survey_results_2009.txt`

## Review status

**needs_human_review**

Outstanding findings:
- Several key request-level requirements from the conversation corpus are missing from the provided requirement set or are only partially represented:
- Transfer utility: “generate pull lists” and “change records … to new location” are implied but the requirement set does not explicitly include pull-list generation as a deliverable (and does not explicitly include transit labels).
- Transfer utility: role restriction is present broadly, but the requirement set does not explicitly enumerate the roles/permission control requested (managers/admins/transfer coordinators) nor the “preview before making changes” as an explicit pre-commit workflow.
- Transfer utility: “undo” is mentioned in the requirement set as part of the transfer utility, but the corpus also requests “Mechanisms: … generating pull lists” and “Printable transit labels” and “Transfer delay alerts” as separate requested features—some are either partially omitted or too vague.

- Missing/damaged & in-transit reports: the corpus requests configurable threshold X (and a suggested default of 7 days) plus front-line sorting by due date for in-transit items. The requirement set includes “threshold configuration” and “configurable X” but does not include an explicit “sort by due date/oldest first” requirement and does not reflect that X default as even “example default” (it is noted as unresolved defaults, but the due-date sorting is fully absent).

- Inactive patrons: the corpus explicitly asks to exclude certain patrons (do not disturb flags, VIP, staff, opted-out communications). The requirement set includes exclusions only implicitly (“permit specified exclusions”) but does not explicitly list these exclusion categories as requirements.

- Patron characteristics reporting: the corpus explicitly asks that age ranges be configurable per report and that the system support both LIMIT and GROUP BY plus combine demographic filters with AND/OR logic; the requirement set includes most of this, but it is missing “LIMIT and GROUP BY” as a distinct capability and does not preserve the null-handling requirement as an explicit output expectation (it does say null included, but this is critical and may be under-specified vs the conversation emphasis).

- Material volume report: the corpus includes “holds count” and “maybe other categories too” and explicitly “at any point in time” including “not just total count, but broken down by categories.” The requirement set covers category breakdown but uses lower priority (Should). The source corpus does not clarify priority, but your reconciliation flagged priority conflicts elsewhere; here you did not preserve that volume report is treated “as a key requirement” in the summary email (katherine). That “key requirement” language is not reflected in priority basis.

- Deletions tracking: the requirement set includes denial-tracking as uncertain. However, the corpus also requests “possibly why (status before deletion?)” and “where they were located (which branch)”—while location is included, “status before deletion” is not. This should be captured as unresolved rather than silently omitted.

- Staff login: the requirement set correctly captures optional card swipe, but does not explicitly include “streamlined login must not be required” (it does) and also does not include “system needs to determine permissions by role after login” as part of the requirement (it is not present).

- Demographics: the corpus requires “Preferred language” and “Patron type” and combines filters; the requirement set includes these fields, but again missing explicit “both LIMIT and GROUP BY” and the “configurable age brackets” is present—still, the requirement set does not clearly indicate that age brackets must be configurable per report.

- Capacity interface: the requirement set only includes “high-level overview” but the conversation summary includes explicit must-have features: drill down, sorting/filtering, trend data, export to CSV, and (optional) color coding. Your requirement set likely under-represents drill-down/trends/export.

- Shelf space report: your requirement set includes comparison and unresolved estimation method, but it does not explicitly include the ability to run per library and per system AND include comparison view side-by-side (requested as “comparison view that shows each library's breakdown side by side”). That feature is absent.

- Query tool/interface: the provided requirements set has general reporting authoring capabilities, but the conversation corpus includes “ability to export to CSV” for capacity and inactive patron report; those CSV specifics are missing in those respective requirements.

- Purging/weeding: the corpus includes “revert status conversion report” and “scheduled purging” is proposed but not accepted in your requirement set (OK), but the “quick effective method of deleting volume entries along with copy entries” is captured only at a high level. Missing is the explicit coupling “delete volume entries along with copy entries, and delete records with no items attached” as distinct cleanup behaviors.

2) Priority/priority-basis incompleteness / traceability gaps:
- You marked “Role- and group-based access control” priority as Unspecified due to a corpus conflict. In the provided source, the Galecia/meeting/technical subcommittee text uses mandatory language (e.g., “User rights and privileges will be controlled through security groups and/or roles” and “must” appears for the general architecture). Your justification for Unspecified is weak because you did not show any explicit “Should” contrary evidence for the same item. This is an actionable traceability issue: either set the priority to Must (if all sources align) or keep Unresolved with explicit conflicting quotes.

- Similarly, “Development, training, and production migration” is stated as “must” in the Galecia draft (“must provide separate… environment… with ability to migrate”), and in technical minutes it is discussed as required. Your uncertainty label (“both shall or Must evidence and Should evidence”) is not supported by concrete contrary evidence in the provided corpus.

- “Non-disruptive report execution” priority: the OPAC non-constraint is clearly Must; the open-hours desirability is “highly desirable.” This should be represented as Must+Should or Must for OPAC and Should for open-hours; your merged requirement has an unresolved priority for the whole.

3) Reconciliation findings are not fully re-audited against the original corpus requirements content:
- “Report cancellation” cancellation is described as requested and also “technically feasible” in Evergreen gaps analysis, but your reconciliation says not consistently confirmed as accepted. The Galecia doc includes “Ability to cancel a report…” explicitly as a fine-grained reporting requirement (in Appendix B/15.5) and survey results mention it. That makes it more than “proposed”; it is supported as a requirement. Your reconciliation remains actionable: update the requirement to include cancellation as included with supported evidence, or move the unresolved finding to something else.
- “Historical and real-time reporting”: you removed an unsupported linkage to historical shelving-location snapshots, but the corpus does request historical reporting “based on a given date or date range” and “historical comparisons” as well as “snapshot bills report.” Your requirement set may still be over-general; missing details include the “snapshot bills report going back in time” and “ability to cancel” already noted.

4) Omission of explicit “branch capacity” metrics definition conflict: your requirement set states “definition must be clarified before building,” but the corpus does offer explicit candidate metrics questions (items vs shelf space, configured limit, circulation vs processing). Since it’s an unresolved decision, you should mark the requirement as uncertain but still record those candidate metrics to preserve traceability.

5) “Complete=true” cannot be set because the provided requirements list still omits multiple concrete deliverables and constraints stated in the conversation corpus (pull lists, transit labels, due-date sorting for in-transit, exclusions for inactive patrons, drill-down/trend/CSV for capacity, shelf-space side-by-side comparison view).
- missing_candidates not included in requirements set (actionable)
- missing_candidates_type_check_error: missing_candidates is required by schema but empty; providing concrete missing candidates below. 
- missing_candidates
- REQ-030: missing name or paragraph-length explanation
- 11 candidate requirement(s) still require reconciliation

## Unresolved candidate requirements

- **Transfer utility: pull list generation:** The item transfer utility must generate pull lists (printable lists) for the selected items to support staff physically locating items for transfer. (Sources: `conversations/conv_pines018_item_transfer.eml`)
- **Transfer utility: printable transit labels:** The item transfer utility must generate printable transit labels (printable barcodes/labels) for items being transferred. (Sources: `conversations/conv_pines018_item_transfer.eml`)
- **Transfer utility: preview-before-commit workflow:** Before applying changes during a batch transfer, the utility must provide a preview/confirmation step showing what will be moved so the user can confirm before changes are executed. (Sources: `conversations/conv_pines018_item_transfer.eml`)
- **Transfer utility: permission roles for transfers:** Transfer actions must be restricted to appropriate roles (e.g., managers/admins/transfer coordinators), and not all staff should be able to transfer items between branches. (Sources: `conversations/conv_pines018_item_transfer.eml`)
- **In-transit items: configurable sort order by due date/oldest first:** The in-transit items report must allow sorting by due date so staff can chase the oldest items first. (Sources: `conversations/conv_pines019_020_missing_intransit.eml`)
- **Capacity interface: drill-down, sorting/filtering, trend data, CSV export, (optional) color coding:** The system capacity interface must support drill-down into individual branches, sorting and filtering (e.g., by region/type/load), trend data (growth/shrink patterns), and CSV export; optional color-coding may be used to indicate under/at/over capacity. (Sources: `conversations/conv_pines015_capacity_interface.eml`)
- **Shelf-space report: side-by-side comparison view across libraries:** The shelf-space report must provide a comparison view that shows each library’s genre/format breakdown side by side to spot outliers easily. (Sources: `conversations/conv_pines016_shelf_space.eml`)
- **Inactive patrons: explicit exclusion categories:** The inactive patrons report must support excluding certain patron categories from results, including at least patrons with do-not-disturb flags, VIP patrons, staff accounts, and patrons who opted out of communications. (Sources: `conversations/conv_pines024_inactive_patrons.eml`)
- **Staff login: permissions determined by role after login:** After any staff login method (card swipe or username/password), the system must apply the user’s permissions based on their assigned security group/role. (Sources: `email_staff_login.eml`)
- **Deletion audit: capture pre-deletion status as ‘why’:** The deletion tracking should optionally capture the status of the record before deletion (used as a proxy for ‘why’) to support auditing/troubleshooting. (Sources: `conversations/conv_pines022_deletions.eml`)
- **Weeding/purging cleanup: delete volume entries with copy entries and delete records with no items attached:** The purging/weeding utilities must provide a quick effective method to delete volume entries together with copy entries, and also delete records with no items attached (orphaned). (Sources: `conversations/conv_pines021_item_purging.eml`, `interview_cataloging_2009-05-08.txt`)

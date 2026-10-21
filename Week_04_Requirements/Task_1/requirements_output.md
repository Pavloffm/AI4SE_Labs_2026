# Refined Software Requirements

Input corpus: `Task_1/data/corpus`

This is a source-reviewed revision of the network-generated draft. The unmodified network output is preserved in `requirements_output.raw.md`; its terminal status was `needs_human_review`. Editorial corrections below do not constitute stakeholder approval or a new successful graph run. Source paths are relative to the input corpus. Priority is distinct from source modality: a Must priority does not make every optional clause in a combined requirement mandatory.

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

- **Priority:** Must — CO-4 in the draft explicitly marks role/group access control High Priority. Ease of role reassignment is a supporting usability request, not evidence against the required access control.
- **Sources:** `early_draft_srs_galecia.txt`, `email_report_features.eml`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`
- **Evidence:** Rights and privileges will be controlled through security groups and/or roles.; The permission system is described as essential.; Fine-grained permissions are requested for report creation, cloning, running, and data access.

### REQ-006: Staff authentication and audit identity

The system should support individual username/password login and may support an optional streamlined method such as employee-card swipe. Streamlined login must not be required or bypass individual authentication, and the system must identify the individual staff member for auditing. After either login method, permissions should follow the assigned group or role as specified in REQ-005.

- **Priority:** Must — Individual identity and auditability use mandatory language; streamlined login availability is explicitly optional.
- **Sources:** `early_draft_srs_galecia.txt`, `email_staff_login.eml`
- **Evidence:** The system must track which staff member is logged in for audit purposes.; Card login must not bypass individual authentication.; Traditional username/password login remains available as a fallback.

### REQ-007: Development, training, and production migration

The system must provide separate development and training environments and support migration of report templates, permissions, saved queries, and other configurations into production. Training must protect production data and permit safe experimentation.

- **Priority:** Must — Draft CO-3 requires a development/training environment with migration, and the July minutes restate it using shall. The technical meeting confirms separation and production-data safety.
- **Sources:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`
- **Evidence:** Development and training environments must support migration to production.; The training environment must not risk production data.; Export/import of templates, permissions, and saved queries is requested.

### REQ-008: Non-disruptive report execution

Searches and reports must not constrain OPAC functionality or performance. Running reports during open hours without disrupting other live operations is highly desirable and should be supported. Queuing, background processing, a separate reporting database, or a read-only replica are possible approaches; no architecture is selected here.

- **Priority:** Must — OPAC non-constraint is mandatory; the distinct open-hours objective retains Should modality rather than being promoted to a mandatory commitment.
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

The system should support immediate and recurring report runs, configurable schedules including hourly through yearly intervals, simultaneous selection of multiple reports, queue position and status visibility, and prioritization of important reports. It should allow cancellation of both scheduled reports and reports already running; execution-level cancellation mechanisms remain an implementation detail.

- **Priority:** Should — Scheduling and queue controls are supported requests. Cancellation is explicitly listed in draft section 15.5 (lines 651–653), requested in the survey, and considered feasible in technical minutes (lines 172–174).
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

The system should provide a high-level overview of branch capacity, with drill-down into individual branches, sorting and filtering, trend data showing growth or shrinkage, and CSV export. Color coding is an optional presentation proposal. The definition of capacity remains open: item counts versus shelf space or configured limits, and circulation versus processing capacity, have not been resolved.

- **Priority:** Should — The conversation's consolidated summary requests the overview, drill-down, sorting/filtering, trends, and CSV export (lines 86–95); it does not resolve the capacity metric.
- **Sources:** `conversations/conv_pines015_capacity_interface.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** The consolidated summary lists drill-down, sorting/filtering, trend data, and CSV export. Capacity alternatives appear at lines 57–62; color coding is introduced as “Maybe” at lines 38–42.

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

The system should provide a batch transfer utility for moving selected items between branches or other locations. It should support candidate queries, saved queries, manual selection, location updates, pull lists, transfer history, efficient transaction-safe batching, undo, and preview before applying changes. Transfer actions should be permission-controlled for managers and administrators; a transfer-coordinator role is also requested in the discussion, subject to the local role policy.

- **Priority:** Should — The core workflow and safeguards are explicitly requested in the consolidated transfer summary. Printable labels and delay alerts are separately identified requests (REQ-037 and REQ-021).
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

The system should identify purge candidates using customizable status-, time-, and activity-based criteria that can be combined, including the requested AND conditions; provide read-only candidate reports and separate confirmation before deletion; support batch status conversion; and efficiently delete volume entries with copy entries and records without attached items. OR combinations and automatic scheduled purging are not confirmed.

- **Priority:** Should — Core purge and cleanup capabilities are repeatedly confirmed; scheduled automatic purging is only a proposal.
- **Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** Purge-conversation lines 55–61 and 94–100 request combined status/time/activity criteria, including AND examples. Candidate reports should be read-only with separate deletion confirmation; batch conversion and cleanup of itemless records are requested.

### REQ-025: Last-copy reporting

The system must provide a last-copy report at library-system scope to prevent deletion of the consortium's last copy and support catalog maintenance such as WorldCat updates. An individual-library or facility last-copy view is requested but not confirmed.

- **Priority:** Must — System-level last-copy reporting is explicitly called critical; local scope is unresolved.
- **Sources:** `conversations/conv_pines021_item_purging.eml`, `early_draft_srs_galecia.txt`, `interview_cataloging_2009-05-08.txt`
- **Evidence:** The last-copy report is called critical and must identify system last copies.; The report would assist catalogers editing WorldCat entries.

### REQ-026: Deletion tracking and audit reporting

The system should count and track item, patron, and other record deletions by location and system, retaining record type (`record_type`), record identifier where available (`record_id`), timestamp (`deleted_at`), deleting user (`deleted_by`), and user/branch location (`location`). It should provide reports grouped by period, location, system, user, and record type. Capturing the pre-deletion status as an explanation is a separate optional proposal, not a required audit field.

- **Priority:** Should — These tracking fields and report dimensions are explicitly specified.
- **Sources:** `conversations/conv_pines022_deletions.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** The deletion conversation lists “record_type, record_id, deleted_by, deleted_at, location” at line 45; “possibly why (status before deletion?)” is tentative at line 28. Reports summarize deletions by period, type, location, and user.

### REQ-027: Denied deletion-attempt tracking

The system may track deletion attempts that were denied, to support compliance and troubleshooting. Whether denied attempts are in scope is unresolved.

- **Priority:** Could — The capability is explicitly suggested as helpful but is not confirmed as a core requirement.
- **Sources:** `conversations/conv_pines022_deletions.eml`
- **Evidence:** A participant asks whether denied deletion attempts can also be tracked.; The summary describes this as helpful for compliance and troubleshooting.

### REQ-028: Patron-characteristic filtering and grouping

Queries and reports should support both filtering or limiting results (LIMIT) and grouping results (GROUP BY) as independently usable capabilities for age range, ZIP code, county, home branch, patron type, and preferred language. Filters should support AND/OR combinations. Age ranges should be configurable per report and derived from birth date at query time. Missing optional characteristics should remain in results as null values.

- **Priority:** Should — Repeated consolidated requirement with explicit technical behavior and no consistent mandatory designation.
- **Sources:** `conversations/conv_pines023_patron_characteristics.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** The listed characteristics must support filtering and grouping.; Age brackets should be configurable and calculated from birth_date.; Null characteristic values should not be silently excluded.

### REQ-029: Inactive-patron reporting

The system should identify patrons with no circulation or defined electronic activity during a configurable number of days and support grouping by system, home library, county, and other levels. Electronic activity includes OPAC or account logins, online holds, and online renewals. Reports should separate patrons with outstanding fines, support configurable exclusions, export CSV, and run in the background. Suggested exclusion categories include do-not-disturb flags, VIP patrons, staff accounts, and communications opt-outs; these are examples rather than an exhaustive mandatory minimum.

- **Priority:** Should — The report and its principal dimensions are explicitly confirmed; digital-resource access, exact day-input constraints, and caching remain unresolved.
- **Sources:** `conversations/conv_pines024_inactive_patrons.eml`, `early_draft_srs_galecia.txt`
- **Evidence:** The inactivity period is configurable.; Specified electronic activity includes logins, holds, and renewals.; Fine separation, exclusions, CSV export, and background processing are requested.

### REQ-030: Inactive-patron mailing addresses

The inactive-patrons report should include current mailing addresses so staff can use the results for outreach to patrons identified by the configured inactivity criteria.

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

### REQ-037: Printable transfer labels

The transfer utility should generate printable transit labels for items selected for transfer, so staff can prepare the physical movement of materials alongside the pull-list and location-update workflow. Label layout and printer integration are not specified.

- **Priority:** Should — Requested as an additional feature in the consolidated transfer summary; not assigned mandatory priority.
- **Sources:** `conversations/conv_pines018_item_transfer.eml`
- **Evidence:** “Printable transit labels” appears in the additional features requested at line 171.

### REQ-038: In-transit report sorting

The in-transit report should support the requested due-date sort so front-line staff can investigate older outstanding transfers first. The meaning of due date and its relationship to transit departure time need clarification before defining the sort key.

- **Priority:** Should — Inferred conservatively from a direct operational request, not an explicit Must designation.
- **Sources:** `conversations/conv_pines019_020_missing_intransit.eml`
- **Evidence:** Lines 99–100 ask to sort by due date so staff can chase the oldest items first.

### REQ-039: Cross-library shelf-space comparison view

The collection-use and shelf-space report should offer a side-by-side view of each library's genre and format breakdown, complementing the individual-library and system-wide views in REQ-017. This allows comparison across libraries without selecting a shelf-space estimation method.

- **Priority:** Should — Inferred from a requested comparison view; not presented as an approved mandatory constraint.
- **Sources:** `conversations/conv_pines016_shelf_space.eml`
- **Evidence:** Lines 89–93 request library/system breakdowns and a comparison showing each library's breakdown side by side.

## Discarded candidates

- **Duplicate-free report exports:** Unsupported as a settled requirement; the source documents a reported problem without specifying when duplicates are erroneous or how uniqueness should be defined. 
  Sources: `survey_results_2009.txt`

## Review status

**needs_human_review**

The raw run stopped after two revision passes. This source-reviewed revision corrects known omissions and stale findings but has not been approved as an implementation baseline. It is not an exhaustive independent proof of completeness or semantic deduplication.

## Review dispositions

All 11 candidates listed in the raw output have been mapped; they are not 11 additional accepted requirements.

| Raw candidate                          | Disposition                                                                       |
|----------------------------------------|-----------------------------------------------------------------------------------|
| Pull-list generation                   | Already included in REQ-019; no duplicate added.                                  |
| Printable transit labels               | Added as REQ-037 with Should priority.                                            |
| Preview before commit                  | Already included in REQ-019.                                                      |
| Transfer permission roles              | Clarified in REQ-019; the local role mapping remains configurable.                |
| In-transit due-date sorting            | Added as REQ-038; sort-key semantics still need clarification.                    |
| Capacity UI capabilities               | Incorporated into REQ-016; capacity metric and optional color coding remain open. |
| Side-by-side shelf-space view          | Added as REQ-039; estimation remains open under REQ-036.                          |
| Inactive-patron exclusions             | Examples made explicit in REQ-029 without asserting an exhaustive mandatory list. |
| Permissions after staff login          | Clarified in REQ-006 and linked to REQ-005.                                       |
| Pre-deletion status                    | Retained as an optional proposal in REQ-026, not a required audit field.          |
| Coupled volume/copy and orphan cleanup | Already included in REQ-024; no duplicate added.                                  |

Other corrections: REQ-012 now retains cancellation; REQ-005 and REQ-007 have source-backed mandatory priorities; REQ-008 preserves the difference between mandatory OPAC protection and the desirable open-hours objective; REQ-030 has a paragraph-length explanation. Barcode/TCN filtering and pivot output are retained in REQ-009 and REQ-011. The raw review's schema-debug messages and claims of missing already-present capabilities are not retained as requirements.

## Open stakeholder decisions

| Decision | Affected requirements | Source and unresolved point |
|---|---|---|
| Capacity metric | REQ-016 | `conversations/conv_pines015_capacity_interface.eml`: choose item/shelf/configured-limit measures and clarify circulation versus processing capacity. |
| Shelf-space estimation | REQ-017, REQ-036, REQ-039 | `conversations/conv_pines016_shelf_space.eml`: dimensions and item-count proxies are proposals, not selected methods. |
| Historical semantics and architecture | REQ-013, REQ-015 | `meeting_tech_subcommittee_2009-06-30.txt` and `conversations/conv_pines014_material_volume.eml`: define retained attributes, historical scope, and architecture without assuming a warehouse is approved. |
| Transfer reversion | REQ-020 | `conversations/conv_pines018_item_transfer.eml`: destination checkout is proposed as a reversion trigger but another message says items checked out there should stay there. No trigger takes precedence here. |
| Optional deletion audit extensions | REQ-026, REQ-027 | `conversations/conv_pines022_deletions.eml`: decide whether to record pre-deletion status and denied attempts; required fields and access for these extensions are unspecified. |
| Retention scope | REQ-031, REQ-032 | `email_financial_reports.eml`: some data may require seven years, but affected data classes are not identified. Do not apply seven years universally. |
| MARC layout and duplicate rows | REQ-011 | `survey_results_2009.txt`: define row layout and when repeated rows are erroneous; null/blank inclusion remains supported independently. |
| Operational defaults and optional interfaces | REQ-016, REQ-021, REQ-023, REQ-029, REQ-038 | Relevant conversation files: confirm default thresholds, alert channels, exclusion policy, optional color coding, integrated digital activity, and the in-transit sort key. |

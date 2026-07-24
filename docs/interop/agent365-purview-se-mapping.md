# Agent 365 / Purview → SE envelope mapping (informative)

> **Status: informative - not normative.** Sources: Microsoft Learn [Agent 365 observability concepts](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability-concepts) and [attribute reference](https://learn.microsoft.com/en-us/microsoft-agent-365/developer/observability-attribute-reference) (dated 2026-07), [Purview for Agent 365](https://learn.microsoft.com/en-us/purview/ai-agent-365), [Audit Copilot / AI activities](https://learn.microsoft.com/en-us/purview/audit-copilot), Office 365 Management Activity API schema. Mapping uses AXES **working-draft** keys (Golden Trace / Module 01). Re-verify against Learn before customer contracts.
>
> **Lane:** Agent 365 / Purview are Microsoft **governance and observability** surfaces for the Microsoft estate. AXES is vendor-neutral **execution evidence**. ARBITR (implementation layer) may *import* Microsoft events into SE envelopes; AXES conformance never depends on Microsoft ingestion (REQ-STD-019).

## What Microsoft exports (two pipes)

| Pipe | Shape | Where it lands | Primary join keys |
|---|---|---|---|
| **Agent 365 observability** | OpenTelemetry spans: `invoke_agent`, `execute_tool`, `chat`, `output_messages` | Defender (`CloudAppEvents` / agent-activity), M365 admin center, Purview policy surfaces | `traceId` tree; `gen_ai.conversation.id`; `gen_ai.agent.id` (appId) |
| **Purview unified audit** | Audit records: `CopilotInteraction`, `ConnectedAIAppInteraction`, `AIAppInteraction`, Agent 365 activities, `AgentAdminActivity` | Purview Audit / DSPM Activity Explorer; Management Activity API / CSV export (`AuditData`) | `Id`, `CreationTime`, `UserId`, `Operation`, `RecordType`, `Workload` |

Both are valuable **inputs**. Neither is, by itself, board-grade portable execution evidence with commit boundaries, acknowledgment ladders, or independent existence bounds.

## Mapping table - Agent 365 OTel / CloudAppEvents → SE

| Microsoft attribute / RawEventData | Typical SE destination (working draft) | Notes |
|---|---|---|
| `gen_ai.operation.name` → `Operation` / `ActionType` (`InvokeAgent`, `InferenceCall`, `ExecuteTool*`) | `event_kind` | Map: invoke_agent → `execution_started` / agent invoke; execute_tool → `tool_invoked`; chat → `model_invoked`; no automatic commit kinds |
| `span.SpanId` / `ParentSpanId` / trace | `span_id`, `parent_span_id`, `trace_id` | Aligns with Trace Context posture (GAP-TECH-014) |
| `gen_ai.conversation.id` → `ConversationId` | `correlation_keys[]` (`conversation` / thread) and/or `lineage_id` | Primary Microsoft join key for a run |
| `microsoft.session.id` → `SessionIdentity` | `correlation_keys[]` (session) | Optional on Microsoft side |
| `gen_ai.agent.id` / name / blueprint | `actor.agent_id`, agent version/name fields (Module 02) | Entra **appId**, not always object ID |
| `microsoft.a365.agent.platform.id` + `gen_ai.agent.type` | `actor.*` + extension for non-Entra ids | Only when agent lacks Entra registration |
| `user.id` / `user.email` (caller) | `actor` human refs via **pseudonymous** subject keys (never embed UPN/email in open envelope) | Privacy-by-design; keep resolution out of band |
| `microsoft.channel.name` | `execution` context / channel extension | `msteams`, `outlook`, `web`, … |
| `gen_ai.execution.type` (`HumanToAgent`, `Agent2Agent`, `EventToAgent`) | `execution_mode` / topology hints | A2A caller fields → parent agent on topology module |
| `microsoft.a365.caller.agent.*` | Topology / lineage (Module 07); not full delegation receipt | Identifies calling agent; **not** CFO→agent authority AD-7844 depth |
| `gen_ai.tool.name` / `type` / `call.id` / args / result | `operation`, tool ids, artefact **refs+hashes** (not raw args/results in envelope) | Raw tool payloads stay referenced; AXES forbids secrets/raw dumps |
| `gen_ai.request.model` / `provider.name` / tokens | `actor.model_id` / provider; usage as derived or extension | |
| `gen_ai.input.messages` / `output.messages` | Artefact refs + hashes + redaction profile (Module 09/13) | Purview may store full text in mailbox/audit; SE must not embed prompts by default |
| `client.address` / `server.address` | Optional runtime/network extensions; often redacted | |
| `span.Status.*` | `result_status` / error fields | Error spans ≠ commit failure |
| `microsoft.tenant.id` | `org_id` / `tenant_id` | Tenant-scoped Microsoft estate |
| Time fields (`TimeGenerated`, start/end nanos) | `occurred_at`, `emitted_at` | Clock provenance still unknown unless enriched |

## Mapping table - Purview audit / CopilotInteraction → SE

| Purview / AuditData property | Typical SE destination | Notes |
|---|---|---|
| `Operation` (`CopilotInteraction`, …) | `event_kind` (interaction / model / tool cluster) | Admin ops (`UpdateTenantSettings`, …) → authority/config events or out of SE scope |
| `RecordType` / `Workload` | Profile / `extensions` (microsoft_purview.*) | Distinguishes Copilot vs ConnectedAIApp vs AIApp |
| `AppHost` / `AppIdentity` | Runtime / host surface | BizChat, Teams, Word, … |
| `CreationTime` | `occurred_at` | |
| `UserId` | Pseudonymous subject key for human actor | |
| `AccessedResources[]` (Id, SiteUrl, Type, Name, SensitivityLabelId, Action) | Target/resource refs (Module 05); sensitivity → Module 13 classification refs | Strong for M365 data lineage; weak for non-M365 systems of record |
| `AISystemPlugin` | Tool / plugin identity | e.g. BingWebSearch |
| `AgentID` / `AgentName` / `AgentType` (`AgentAdminActivity`) | `actor.agent_id` + type | Admin/governance of agents, not per-action commit evidence |
| Prompt / response text (DSPM / mailbox retention) | **Referenced artefacts only** in SE | Full-text retention is a Purview control; open SE stays pointers-and-hashes |

## Where AXES (and ARBITR on top of it) go beyond Microsoft capture

These are structural limits of the Microsoft control/observability plane - not "missing optional fields," and not gaps in AXES or ARBITR.

| Microsoft limit | Why AXES coverage matters for auditors |
|---|---|
| **Delegation-context depth** | Agent 365 binds Entra appId / blueprint / caller agent ids. It does not evidence *who delegated what capability, under which policy version, with which limits, valid when, revocable how* (AXES Module 03 / Golden Trace AD-7844 pattern). |
| **Commit boundary & consequence** | Spans describe invoke / tool / chat. They do not distinguish advisory activity from money movement, record change, or irreversible side effects, nor mechanism/impact/reversibility. |
| **Acknowledgment ladder** | No graded transport → protocol → business → settlement corroboration with counterparty authenticity basis. |
| **Cross-estate runs** | Telemetry and audit are **tenant-scoped Microsoft surfaces**. Journeys that leave M365 (bank rails, ERP, AWS, Salesforce, partner agents, x402 settlement) fall `outside_capture_boundary` unless separately evidenced. |
| **Non-M365 / non-registered agents** | Agents without Entra registration need alternate ids and may not use Agent 365 routes; third-party AI outside the tenant is a different RecordType with thinner enterprise binding. Estate-wide accountability needs emitters beyond Microsoft. |
| **Independent existence bound** | Logs live in Microsoft custody (Defender / Purview / Exchange). A Microsoft log of Microsoft-hosted agents is **not** independent evidence for an auditor who must not trust the respondent's cloud alone. AXES + external anchoring (SCITT / TSA / OTS / …) addresses that. |
| **Control re-evaluation** | DLP / IRM / communication compliance are Microsoft policy engines. They do not ship content-addressed control-context snapshots for third-party re-run (GAP-EXEC-021). |
| **Emission fail-posture / silence semantics** | Observability drop conditions (license, missing `invoke_agent`) are silent. AXES requires declared fail-closed/open and heartbeat meaning. |
| **Portable assurance reports** | Admin center and DSPM are product UIs. They are not open, regenerable board/audit/regulator packs with claim→field citation from a vendor-neutral bundle. |

## Independence argument (one sentence)

**A Microsoft-operated log of Microsoft-estate agents is necessary governance telemetry; it is not sufficient independent evidence that an autonomous action was authorised, committed, and corroborated across the whole operating estate.**

## Related

- ARBITR import backlog: BLD-031 in [`registers/requirements-register.md`](../../registers/requirements-register.md) (Magentix commercial battlecard is proprietary and not published in this repo)
- SCITT / anchoring: [`x402-and-anchoring.md`](x402-and-anchoring.md)
- Three-layer coverage: [`three-layer-evidence-coverage.md`](three-layer-evidence-coverage.md)

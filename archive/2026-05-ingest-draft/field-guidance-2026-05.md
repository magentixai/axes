> **Status: historical companion to the superseded ingest draft schema (see schema/README.md). Retained for early implementers; superseded by the field catalogue (docs/05) as it lands.**

# ARBITR SE v1 Field Guidance - Draft Contract

Status: Draft field guidance before formal JSON Schema  
Version: `se.v1.draft-2026-05-31`  
Purpose: Provide a workable in-house development contract for emitting, ingesting, storing, materialising, and exporting ARBITR Secure Execution envelopes.  
Audience: ARBITR engineering, connector builders, AI agent framework experimenters, product architecture, and evidence bundle design.

## 1. Summary

SE v1 is the proposed portable execution envelope used by ARBITR to capture what an autonomous or semi-autonomous system actually did.

This file consolidates the current field guidance from the ARBITR V1 process, class, component, and service-contract documents, plus the later design context around cross-boundary execution, portable evidence bundles, and multi-framework agentic support.

This is not yet the final official schema. It is the best current draft contract to build against while testing ARBITR with OpenClaw and other AI agentic frameworks.

## 2. Working contract status

This draft should be treated as:

- Stable enough to generate example envelopes.
- Stable enough to build connector adapters against.
- Stable enough to test ingestion, idempotency, graph materialisation, and export bundles.
- Not yet stable enough to publish externally as the official schema.
- Additive only unless the team explicitly approves a breaking change.

The current goal is to exercise the contract in real agentic workflows, discover missing fields, and then formalise the official schema.

## 3. Design commitments

SE v1 must preserve the following ARBITR commitments.

### 3.1 V1 in scope

- SE v1 envelope ingestion.
- Append-only system of record.
- Durable event bus notification after persistence.
- Deterministic graph materialisation.
- Read models and query APIs.
- Portable evidence bundles.
- Minimal semantics catalog support.
- Runtime-neutral connector integration.

### 3.2 V1 out of scope

- No policy engine.
- No real-time commit blocking.
- No wallet or payment rail infrastructure.
- No compliance certification claims.
- No raw secret storage.
- No cross-tenant trace merge.
- No cross-environment trace merge.
- No connector-specific SaaS domain logic.

### 3.3 Non-negotiable invariants

- Envelopes are append-only.
- Corrections are new envelopes.
- Ingestion persists before acknowledgement.
- Idempotency applies per tenant using `idempotency_key` or `envelope_id`.
- Materialisation is idempotent per `tenant_id`, `trace_id`, and `envelope_id`.
- The SaaS side consumes SE v1 only.
- Connector-specific semantics stay in the connector, semantics catalog, or `extensions`.
- Inputs and outputs are pointer and hash references only in V1.

## 4. Canonical JSON shape

This is the recommended draft JSON shape for engineering tests.

The shape keeps the confirmed field list visible at the top level, while also introducing structured blocks that support richer future schema evolution. The top-level scalar fields are intentionally retained for indexing, compatibility, and simple ingestion.

```json
{
  "version": "se.v1.draft",
  "envelope_id": "018f8f7a-7f30-7cc2-bb3d-6a1f16d88a10",
  "org_id": "018f8f7a-1000-7000-8000-000000000001",
  "tenant_id": "018f8f7a-1000-7000-8000-000000000101",
  "environment_id": "018f8f7a-1000-7000-8000-000000001001",
  "trace_id": "018f8f7a-2000-7000-8000-000000000001",
  "span_id": "018f8f7a-3000-7000-8000-000000000001",
  "parent_span_id": null,
  "event_kind": "tool_call.completed",
  "occurred_at": "2026-05-31T12:10:02.120Z",
  "emitted_at": "2026-05-31T12:10:02.880Z",
  "idempotency_key": "tenant-0101:trace-0001:span-0001:tool_call.completed:v1",
  "authority_scope": "local_files.write",
  "capability_id": "cap.file.write",
  "delegation_receipt_id": "del_01JZ8Z2Y7T3Y9K2W4EV0EAF9KQ",
  "actor_ref": "user:opaque:7f0b7f8d",
  "agent_ref": "agent:openclaw:finance-ops-worker",
  "target_system": "local_filesystem",
  "target_resource_type": "file",
  "target_resource_id": "sha256:7b65f0f1a6a8f4e8c1c3c98ec0e9c6ec...",
  "operation": "file.write",
  "result_status": "OK",
  "error_code": null,
  "error_message": null,
  "data_classification": "INTERNAL",
  "inputs_ref": {
    "uri": "customer-evidence://tenant-0101/trace-0001/input-0001.json",
    "sha256": "64d7c7a3b335bb2b4c813e4c7b8ab4b2b7f0d6a5b3c9f91a5029f7cf19f9d6a1",
    "content_type": "application/json",
    "size_bytes": 1542,
    "redaction_status": "REDACTED"
  },
  "outputs_ref": {
    "uri": "customer-evidence://tenant-0101/trace-0001/output-0001.json",
    "sha256": "d0b9f1f31a9a7d3e97f2d61ab0c6a92f24de67a7dcff1598eb8021f79cda9c3d",
    "content_type": "application/json",
    "size_bytes": 861,
    "redaction_status": "REDACTED"
  },
  "runtime": {
    "framework": "openclaw",
    "framework_version": "unknown",
    "connector_name": "arbitr-openclaw-connector",
    "connector_version": "0.1.0",
    "runtime_instance_ref": "host:opaque:devbox-01"
  },
  "authority_context": {
    "scope": "local_files.write",
    "purpose": "Write a generated summary file inside the approved workspace",
    "delegated_by_ref": "user:opaque:7f0b7f8d",
    "delegated_to_ref": "agent:openclaw:finance-ops-worker",
    "valid_from": "2026-05-31T12:00:00Z",
    "valid_until": "2026-05-31T13:00:00Z",
    "constraints": {
      "allowed_systems": ["local_filesystem"],
      "allowed_operations": ["file.write"],
      "workspace_boundary": "/workspace"
    }
  },
  "target": {
    "system": "local_filesystem",
    "resource_type": "file",
    "resource_id": "sha256:7b65f0f1a6a8f4e8c1c3c98ec0e9c6ec...",
    "resource_label": "workspace summary file"
  },
  "evidence_artifacts": [
    {
      "artifact_id": "018f8f7a-4000-7000-8000-000000000001",
      "artifact_type": "request",
      "uri": "customer-evidence://tenant-0101/trace-0001/input-0001.json",
      "sha256": "64d7c7a3b335bb2b4c813e4c7b8ab4b2b7f0d6a5b3c9f91a5029f7cf19f9d6a1",
      "content_type": "application/json",
      "size_bytes": 1542
    },
    {
      "artifact_id": "018f8f7a-4000-7000-8000-000000000002",
      "artifact_type": "response",
      "uri": "customer-evidence://tenant-0101/trace-0001/output-0001.json",
      "sha256": "d0b9f1f31a9a7d3e97f2d61ab0c6a92f24de67a7dcff1598eb8021f79cda9c3d",
      "content_type": "application/json",
      "size_bytes": 861
    }
  ],
  "semantics": {
    "semantic_keys": ["operation.file.write", "runtime.openclaw", "target.local_filesystem"],
    "display_hint": "agent_wrote_file"
  },
  "cross_scope": null,
  "signature": null,
  "extensions": {
    "openclaw": {
      "tool_name": "shell",
      "skill_name": "workspace-files",
      "command_class": "write_file"
    }
  }
}
```

## 5. Minimum field list

This section captures the confirmed draft field list.

| Field | Required | Type | Guidance |
|---|---:|---|---|
| `version` | Yes | string | Contract version. Use `se.v1.draft` until official release. |
| `envelope_id` | Yes | UUID string | Unique envelope identifier. Used for append-only storage and idempotency fallback. |
| `org_id` | Yes | UUID string | Organisation boundary. If derived from API key, the emitted value must match or be omitted only by agreed gateway policy. |
| `tenant_id` | Yes | UUID string | Primary RLS and idempotency boundary. |
| `environment_id` | Yes | UUID string | Environment boundary such as prod, staging, region, cloud provider, on-prem instance. |
| `trace_id` | Yes | UUID string | Workflow or run correlation id. |
| `span_id` | Yes | UUID string | Event or step id within the trace. |
| `parent_span_id` | No | UUID string or null | Parent step. Required when this event is a child of another event. |
| `event_kind` | Yes | string enum | Normalised lifecycle category. See event taxonomy below. |
| `occurred_at` | Yes | RFC 3339 timestamp | When the event happened in the runtime. |
| `emitted_at` | Yes | RFC 3339 timestamp | When the connector emitted the envelope. |
| `idempotency_key` | Yes | string | Stable key for duplicate-safe ingestion. |
| `authority_scope` | Yes | string | Compact scalar authority classification for indexing and filtering. |
| `capability_id` | No | string | Capability, skill, permission, or tool capability reference. |
| `delegation_receipt_id` | No | string | Reference to the delegated authority receipt, if available. |
| `actor_ref` | Strongly recommended | string | Opaque human, service, or system actor reference. Avoid PII. |
| `agent_ref` | Strongly recommended | string | Opaque agent or runtime actor reference. |
| `target_system` | Conditional | string | Required for tool, external system, and commit events. |
| `target_resource_type` | Conditional | string | Required where a target resource exists. |
| `target_resource_id` | Conditional | string | Opaque or hashed identifier. Avoid sensitive raw IDs where possible. |
| `operation` | Conditional | string | Action performed or attempted, such as `file.write`, `crm.update`, `payment.initiate`. |
| `result_status` | Yes | enum | `OK`, `ERROR`, `PARTIAL`, or `TIMEOUT`. |
| `error_code` | No | string | Required when result status is `ERROR` or `TIMEOUT` if available. |
| `error_message` | No | string | Sanitised error text. Must not contain secrets. |
| `data_classification` | Yes | enum | `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, or `RESTRICTED`. |
| `inputs_ref` | No | object or string | Pointer and hash only. No raw input payload in V1. |
| `outputs_ref` | No | object or string | Pointer and hash only. No raw output payload in V1. |
| `runtime` | Recommended | object | Runtime and connector metadata. Framework-specific values stay here or in `extensions`. |
| `authority_context` | Recommended | object | Rich authority context. Keeps `authority_scope` as the simple searchable scalar. |
| `target` | Recommended | object | Structured equivalent of the target scalar fields. |
| `evidence_artifacts` | Recommended | array | Structured pointers and hashes. Normalises `inputs_ref` and `outputs_ref`. |
| `semantics` | Recommended | object | Portable semantic keys only. Tenant-owned labels live in Semantics Catalog. |
| `cross_scope` | Optional | object or null | Navigation reference only. No merge. |
| `signature` | Reserved | object or null | Future signature and attestation block. |
| `extensions` | Optional | object | Namespaced connector or framework extras. Must not be required by SaaS core. |

## 6. Event taxonomy draft

This taxonomy is intentionally small and framework-neutral.

| Event kind | Meaning |
|---|---|
| `trace.started` | A workflow, run, job, or agent session started. |
| `trace.completed` | A workflow, run, job, or agent session completed. |
| `agent.started` | An agent instance or worker became active for a trace. |
| `agent.completed` | An agent instance or worker completed its assigned work. |
| `tool_call.requested` | A tool call or external action was requested. |
| `tool_call.completed` | A tool call or external action completed. |
| `external_commit.attempted` | Runtime attempted an irreversible or business-significant state change. |
| `external_commit.completed` | External system confirmed a state change. |
| `checkpoint.created` | Runtime crossed or recorded a checkpoint. |
| `handoff.created` | Control or continuation moved to another agent, runtime, tenant, or environment. |
| `error.reported` | Runtime, connector, ingestion, or tool reported a failure. |

Event kinds may be extended, but connector teams should first map framework-specific lifecycle events into this list. If a framework cannot map cleanly, propose a new event kind with examples.

## 7. Authority context guidance

SE v1 is not a policy decision and not a compliance certificate. It records the authority context around execution.

The scalar `authority_scope` is required for filtering. The object `authority_context` is recommended for useful interpretation.

Recommended structure:

```json
{
  "scope": "payments.refund.create",
  "purpose": "Refund customer within support workflow",
  "delegated_by_ref": "user:opaque:123",
  "delegated_to_ref": "agent:runtime:abc",
  "delegation_receipt_id": "del_01JZ8Z2Y7T3Y9K2W4EV0EAF9KQ",
  "valid_from": "2026-05-31T12:00:00Z",
  "valid_until": "2026-05-31T13:00:00Z",
  "constraints": {
    "max_amount": {
      "value": "250.00",
      "currency": "GBP"
    },
    "allowed_systems": ["stripe"],
    "allowed_operations": ["payment.refund.create"],
    "approval_required": false
  }
}
```

Rules:

- Use opaque references where possible.
- Do not store raw identity material.
- Do not store secrets.
- Do not claim that authority was enforced by ARBITR in V1.
- If another system enforces or blocks, record that fact as observed evidence, not as ARBITR enforcement.

## 8. Evidence pointer guidance

V1 stores pointers and hashes only.

Recommended pointer object:

```json
{
  "uri": "customer-evidence://tenant-0101/trace-0001/input-0001.json",
  "sha256": "64d7c7a3b335bb2b4c813e4c7b8ab4b2b7f0d6a5b3c9f91a5029f7cf19f9d6a1",
  "content_type": "application/json",
  "size_bytes": 1542,
  "redaction_status": "REDACTED"
}
```

Rules:

- `uri` must not expose secrets.
- `sha256` should be computed after redaction where the artifact itself is redacted.
- If raw customer-controlled evidence exists outside ARBITR, ARBITR stores a pointer and hash only.
- ARBITR does not fetch or store artifact body content in V1 unless a later controlled object-store mode is explicitly enabled.

## 9. Target guidance

The top-level target fields remain for indexing:

- `target_system`
- `target_resource_type`
- `target_resource_id`
- `operation`

The structured `target` object is recommended for richer interpretation:

```json
{
  "system": "salesforce",
  "resource_type": "opportunity",
  "resource_id": "sha256:...",
  "resource_label": "Opportunity record",
  "external_correlation_id": "opaque:sf-update-123"
}
```

Rules:

- Use hashed or opaque resource identifiers where raw identifiers are sensitive.
- Use `operation` verbs that can be grouped by system, domain, and action, for example `crm.opportunity.update` or `filesystem.file.write`.

## 10. Runtime and framework guidance

The SE core must work across multiple AI agentic frameworks.

Recommended `runtime` structure:

```json
{
  "framework": "langgraph",
  "framework_version": "0.x",
  "connector_name": "arbitr-langgraph-adapter",
  "connector_version": "0.1.0",
  "runtime_instance_ref": "runtime:opaque:worker-01"
}
```

Recommended framework mapping:

| Framework or agentic model | Trace mapping | Span mapping | Target mapping | Notes |
|---|---|---|---|---|
| OpenClaw | Session, task, cron job, or delegated workflow | Tool call, shell command, file action, browser action | Local file, shell, browser, messaging, external API | Primary V1 connector candidate. |
| LangGraph | Graph run or workflow execution | Node execution or edge transition | Tool, API, DB, workflow target | Strong fit for deterministic graph reconstruction. |
| CrewAI | Crew run or task chain | Agent task, tool invocation, handoff | Tool or external system | Good test case for multi-agent delegation. |
| AutoGen style systems | Conversation or task | Agent turn, function call, tool call | Tool, function, external resource | Useful for agent-to-agent handoff testing. |
| LlamaIndex workflows | Workflow run | Query step, tool step, retrieval step | Index, tool, data source | Useful for evidence pointers and data classification. |
| Custom cron or script agents | Job run | Script step or command | Host, file, database, HTTP endpoint | Useful for non-LLM automation baseline. |
| RPA or workflow tools | Workflow execution | Action block | SaaS app, browser, API endpoint | Useful to prove SE is not limited to LLM agents. |

## 11. Cross-scope guidance

Cross-scope support is navigation-only in V1. It must not merge storage across tenants or environments.

Recommended shape:

```json
{
  "boundary_type": "ENV_EXIT",
  "display_label": "Continues in: Client A / Production / AWS",
  "continuation_ref": {
    "source_trace_id": "018f8f7a-2000-7000-8000-000000000001",
    "source_envelope_id": "018f8f7a-7f30-7cc2-bb3d-6a1f16d88a10",
    "target_scope_fingerprint": "sha256:0cb5...",
    "target_trace_id": "018f8f7a-2000-7000-8000-000000000099",
    "target_entry_envelope_id": "018f8f7a-7f30-7cc2-bb3d-6a1f16d88a99",
    "reason": "workflow_handoff"
  }
}
```

Rules:

- The target trace is loaded only if the viewer is authorised.
- The UI may show a locked boundary handle if not authorised.
- Storage remains isolated.
- No automatic cross-tenant graph merge in V1.

## 12. Signature block reservation

`signature` is reserved for later versions.

Possible future shape:

```json
{
  "payload_hash": "sha256:...",
  "signed_at": "2026-05-31T12:10:03Z",
  "signature_alg": "ed25519",
  "signature_value": "base64url:...",
  "key_id": "kid:..."
}
```

V1 guidance:

- Permit `signature: null`.
- Do not make signatures mandatory for early pilots.
- Keep the field reserved so adding signatures later is additive.

## 13. Extension guidance

`extensions` is where connector-specific or framework-specific values live.

Rules:

- Extension keys must be namespaced, for example `openclaw`, `langgraph`, `crewai`.
- SaaS ingestion must not require extension fields to process the envelope.
- Extension fields must pass secret linting.
- Extension values must be safe to store.
- Any extension that becomes widely used should be considered for promotion into the core schema.

Example:

```json
{
  "extensions": {
    "langgraph": {
      "node_name": "update_customer_record",
      "edge_from": "classify_intent",
      "edge_to": "notify_user"
    }
  }
}
```

## 14. Internal alignment tests

Use these tests during in-house schema hardening.

### Test 1: Minimum ingest

Given a valid envelope with required fields, the gateway accepts `POST /v1/envelopes` and returns `202 Accepted`.

Pass criteria:

- Tenant binding is resolved from API key.
- Schema validation passes.
- Secret lint passes.
- Envelope persists before ACK.
- Event bus notification publishes after system-of-record commit.

### Test 2: Duplicate ingest

Given the same `tenant_id` and `idempotency_key`, resend the same envelope.

Pass criteria:

- Gateway returns `202 Accepted`.
- No second system-of-record row is created.
- No duplicate event bus notification is published.

### Test 3: Graph materialisation

Given three envelopes with a shared `trace_id` and parent-child span relationships.

Pass criteria:

- Materialiser creates deterministic graph nodes and edges.
- Applied marker prevents reprocessing on redelivery.
- Replay produces the same graph.

### Test 4: No raw secret persistence

Given an envelope containing an API key, token, password, private key, or obvious credential in any field.

Pass criteria:

- Connector redacts before send where possible.
- Ingestion secret lint rejects or redacts according to the agreed policy.
- Logs do not echo the secret.
- Error response is safe.

### Test 5: Evidence pointer only

Given input and output artifacts.

Pass criteria:

- Envelope stores only URI, hash, content type, size, and redaction status.
- Artifact body is not stored in the envelope.
- Export bundle includes pointers and hashes, not raw secret payloads.

### Test 6: Cross-scope navigation

Given a handoff from one environment or tenant to another.

Pass criteria:

- Source envelope stores a `cross_scope` continuation reference.
- UI can show a boundary handle.
- Target trace loads only if the viewer is authorised.
- Storage is not merged.

### Test 7: Framework portability

Emit equivalent file-write or CRM-update actions from OpenClaw, LangGraph, and a custom script.

Pass criteria:

- All three normalise into the same SE core fields.
- Framework differences appear only in `runtime`, `semantics`, or `extensions`.
- SaaS ingestion does not branch on framework type.

### Test 8: Export reconstruction

Export a trace bundle and re-import or replay it in a test harness.

Pass criteria:

- Ordered envelopes reconstruct the same graph.
- Hash summary is stable.
- Result can support both operational detail and executive evidence summaries.

## 15. Example event sequence

A simple file-write workflow should produce at least these envelopes:

1. `trace.started`
2. `agent.started`
3. `tool_call.requested`
4. `tool_call.completed`
5. `trace.completed`

A commit-sensitive workflow should add:

- `external_commit.attempted`
- `external_commit.completed`
- `checkpoint.created`, if the action crossed a declared business boundary.

## 16. Open questions for Martin and colleagues

The following questions should be answered before turning this guidance into the official schema.

1. Should `org_id`, `tenant_id`, and `environment_id` be mandatory in the emitted envelope, or should `tenant_id` and `environment_id` be injected by the gateway from the API key? Current recommendation: include them and verify against API-key binding.

2. Should the official version string be `se.v1`, `se.v1.draft`, or semantic versioned as `1.0.0-draft`? Current recommendation: use `se.v1.draft` now, reserve `se.v1` for first official release.

3. Should `authority_scope` remain a required top-level scalar once `authority_context.scope` exists? Current recommendation: yes, because it supports indexing, filtering, and dashboards.

4. Should `actor_ref` and `agent_ref` become mandatory for all event kinds, or only for agent and tool events? Current recommendation: strongly recommended for all, mandatory for `agent.*`, `tool_call.*`, and `external_commit.*`.

5. Do we want the first official event taxonomy to remain small, or should payment, file, browser, messaging, and database operations each get separate event kinds? Current recommendation: keep `event_kind` small and put domain detail in `operation`.

6. Should `inputs_ref` and `outputs_ref` remain top-level fields, or should they be replaced by `evidence_artifacts[]` in the formal schema? Current recommendation: keep both for draft compatibility, then decide whether to deprecate the scalar refs.

7. Should ARBITR support customer-managed artifact URI schemes only, or also an optional ARBITR-managed temporary object store for non-sensitive export convenience? Current recommendation: support customer-managed pointers first.

8. Should `cross_scope` be included in official SE v1, or reserved for SE v1.1? Current recommendation: include it as optional because the boundary-first UI depends on it.

9. Should `signature` be included as a nullable reserved block in official SE v1? Current recommendation: yes, to avoid later structural disruption.

10. Should `data_classification` use a simple four-value enum, or align with customer-defined classification schemes? Current recommendation: standard four-value enum in core, customer classification mapping in semantics catalog.

11. What is the minimum set of example frameworks for validation? Current recommendation: OpenClaw, LangGraph, CrewAI-style multi-agent flow, and custom script agent.

12. Should evidence bundles contain an executive summary manifest generated from read models, or only the raw ordered envelope and graph data? Current recommendation: both, with raw evidence preserved and executive summary generated as derived output.

## 17. Recommended next development cycle

### Cycle A: Local harness

Build a small local harness that emits SE v1 envelopes from:

- OpenClaw file operation.
- LangGraph tool call.
- Custom Python script action.

Validate that each produces equivalent core fields.

### Cycle B: Ingestion stub

Implement:

- `POST /v1/envelopes`
- schema validation
- secret lint stub
- idempotency table
- append-only store
- basic event bus publish or local queue substitute

### Cycle C: Materialisation stub

Build deterministic graph reconstruction from:

- `trace_id`
- `span_id`
- `parent_span_id`
- `event_kind`
- timestamps
- result status

### Cycle D: Evidence bundle stub

Export:

- ordered envelopes
- graph nodes and edges
- artifact pointer manifest
- hash summary
- draft executive summary metadata

### Cycle E: Schema hardening

Review failures and promote any repeated extension fields into the core or formally keep them namespaced.

## 18. Practical position

SE v1 should remain a portable evidence contract, not an enforcement model.

ARBITR wins if the same envelope can describe execution across OpenClaw, LangGraph, CrewAI-style workflows, custom automation, and future AIOS runtimes without turning ARBITR into a runtime, policy engine, wallet, or compliance certifier.

The draft above is intentionally usable now while preserving enough extension space to survive real-world agentic framework testing.
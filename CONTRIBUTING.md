# Contributing to AXES

Structured review is the point of publishing early. Contributions are welcome from practitioners in assurance, audit, risk, security, payments, law, engineering and standards work - you do not need to write code to materially improve this standard.

## How to contribute

1. **Open an issue** using the template matching your contribution category (below). One concern per issue.
2. Substantive specification changes follow as a **pull request** referencing the accepted issue.
3. Sign off your commits under the **Developer Certificate of Origin** (`git commit -s`). No copyright assignment is required - you keep your copyright; the contribution is licensed under the repository licences (CC-BY-4.0 for spec text, Apache-2.0 for code).

## Contribution categories

| Category | Use it for |
|---|---|
| **Field proposal** | A new data element for the envelope or a module |
| **Definition challenge** | A published field/term whose definition is ambiguous, wrong, or dangerous |
| **Vocabulary proposal** | New or amended controlled-vocabulary values |
| **Implementation issue** | Something impractical or costly to emit/consume as specified |
| **Framework mapping issue** | A gap or error in how AXES maps onto a specific runtime, framework or protocol (incl. MCP) |
| **Evidence gap** | A real-world scenario the schema cannot evidence |
| **Topology issue** | Trace/lineage/boundary/continuation reconstruction problems |
| **Assertion proposal** | New or amended assurance-assertion types |
| **Reporting requirement** | A report statement a real audience needs that current fields cannot support |
| **Security / privacy concern** | Attack surface, misuse potential, privacy or surveillance implications |
| **Conformance test proposal** | Test vectors, negative examples, validator behaviour |

Operator-facing conformance notes (corpus vs claims): [`CONFORMANCE.md`](CONFORMANCE.md). Informative mapping of AXES evidence to decision / control-in-force / outcome layers: [`docs/interop/three-layer-evidence-coverage.md`](docs/interop/three-layer-evidence-coverage.md). Programme tasks for closing independent control re-evaluation: [`registers/three-layer-evidence-and-control-reevaluation.md`](registers/three-layer-evidence-and-control-reevaluation.md).

## How proposals are assessed

Every proposal is evaluated in the open against the same fixed questions:

1. **Accountability support** - does it help answer who authorised, what became real, or whether evidence can be relied on?
2. **Report support** - which report statement(s), for which audience, does it enable? (No field without report, audit, topology, authority, integrity or implementation value.)
3. **Vendor and runtime neutrality** - can every serious runtime/framework emit or map it?
4. **Implementation burden** - what does it cost to produce, per implementation profile?
5. **Open vs implementation placement** - does it belong in the open envelope, the open derived annex, or the implementation layer?
6. **Duplication** - does an existing canonical key or vocabulary already cover it?
7. **Vocabulary impact** - does it require new controlled values, and are they mutually exclusive and complete?
8. **Conformance impact** - which SE-C level and profiles does it touch, and at what conformance level would a reader be entitled to rely on it?
9. **Evidence-to-claim traceability** - can every report claim the element enables link back to specific evidence references?
10. **Fact-vs-inference danger check** - could this element be misread as encoding fact when it is actually inference, assumption, model judgement or management assertion? If so, what provenance/confidence structure prevents that?
11. **Confidence and reliance wording** - what confidence, limitation, or reliance-boundary wording must accompany any statement built on this element?

These eleven questions carry the requirements-governance discipline of the original design programme (layer placement, claim traceability, reliance boundaries, dangerous-to-encode-as-fact) into every future contribution.

Additional standing rules: scoped-assurance language only (no field or definition may imply "compliant/safe/guaranteed"); fact and interpretation stay separated; personal data by reference and pseudonymous key only; no mandatory hidden chain-of-thought capture.

## What happens next

Decisions land in [`registers/decision-register.md`](registers/decision-register.md) with a recorded rationale - including rejections and deferrals, which are staged, not deleted. Accepted items flow into the field catalogue with full traceability to your issue.

## Not sure where it fits?

Open a **Definition challenge** or **Evidence gap** issue and describe the real-world situation. A concrete scenario beats a perfect category.

# Platform Validation Evidence

Status: G1 platform proof closed on 2026-08-12.

This is the canonical human-readable evidence record for G1. It consolidates platform,
model, Agent shell, Prompt Node, User Activity, Knowledge Base, and persistence evidence used
to freeze the G1 platform decisions. It contains no credentials, API keys, bearer tokens,
service-instance URLs beyond approved non-secret endpoints, or secret values.

Historical spike file paths named in this record are provenance references only. Superseded
spikes are not current production entry points; final reviewer-facing production assets are
listed in the repository README and artifact index.

## 1. G1 purpose and scope

G1 was a platform-proof gate. Its purpose was to prove the minimum remote Watson and IBM Cloud
capabilities needed before production G2/G3 implementation. G1 did not implement the production
IT request flow, orientation booking flow, five-document HR Knowledge Base, Part B classifier,
Part B dataset, production response drafting, or production persistence domain code.

Evidence rule: no evidence means no gate advancement.

## 2. Raw durable evidence artifacts

The machine-readable model-selection artifacts are retained with domain-oriented names:

| Artifact | SHA-256 |
|---|---|
| `artifacts/model_selection_smoke.json` | `730B4F32A2D83488DB6D1AF754C7794AE6AC5B846C8213425FFC5B085F9CDC6E` |
| `artifacts/model_selection_confirmation.json` | `F8A9E587F1ABCD847E82680AB159154E69EC168BFE1A6040E412F7799438B011` |

The authoritative G1B leave-policy source hash is:

`58010048238908492092F61022B97D1BF357BE6432F34E818174808187D29731`

The byte-identical ingestion representation `knowledge/sources/leave-policy.txt` has the same
SHA-256.

## 3. G1A platform, model, and Agent evidence

Remote watsonx Orchestrate authentication passed. The remote environment `project2` was created
and activated with IBM IAM authentication. The active workspace was Global workspace. Read-only
remote Orchestrate queries returned tenant records.

watsonx.ai connectivity passed. The supervisor proved IBM IAM API-key exchange, Frankfurt
watsonx.ai endpoint access, repository-local `ibm-watsonx-ai` SDK execution, successful
`APIClient` authentication, and successful project metadata retrieval.

Model discovery passed in both paths:

- Orchestrate model discovery returned nine model/provider entries.
- Direct Frankfurt watsonx.ai chat-model discovery returned four direct chat models and proved
  the project had the required Runtime association.

Selected model:

- Watson model ID: `meta-llama/llama-4-maverick-17b-128e-instruct-fp8`
- Orchestrate LLM reference: `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8`

Selection priority:

1. safety;
2. structured-output reliability and semantic correctness;
3. support-draft quality;
4. latency/token usage only as tie-breakers.

This was bounded G1 selection evidence, not a formal benchmark. Known residual risks preserved
for later Part B design and evaluation:

- unknown-urgency over-inference;
- unsupported future-action/SLA promises in support drafting.

The production HR Agent strategy is a native watsonx Orchestrate Agent using ReAct Core,
represented as `style: react_intrinsic`. The temporary COS proof harness used `react` only as a
remote execution harness and received a deprecation warning; that temporary style is not a
production architecture decision. The minimal `hr_onboarding_agent` remote proof passed and did
not prove the full G2 capabilities.

## 4. Prompt Node evidence and decision

Artifact used for evidence: `flows/g1b_prompt_node_spike.py`

Remote tool name: `g1b_prompt_node_spike`

The real Prompt Node Flow imported and executed in the tenant. The Prompt Node used
`watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8` internally and returned strict
structured output containing exactly:

- `category`
- `urgency`
- `confidence`
- `reasoning`

Structural strict-output behavior passed.

Semantic/input-fidelity/repeatability failed in the tested tenant path. A controlled duplicate
invoice input, `My invoice has a duplicate charge for this month.`, produced a materially
appropriate billing/high result in one run and a separate clean account/medium result with
account-access reasoning absent from the supplied input.

This does not prove Maverick is globally unreliable and does not prove Prompt Node is globally
broken. It proves that the tested Orchestrate Prompt Node path was not sufficiently reliable for
this project's Part B classification/drafting path.

Frozen decision:

`PIPELINE_LLM_MODE = PYTHON_WATSONX_TOOL`

Scope of decision: watsonx Orchestrate Flow remains the sole Part B orchestrator. Python is only
the bounded watsonx.ai LLM invocation mechanism for classification/drafting, with local
structured-output validation before returning control to the Flow.

## 5. User Activity evidence and decision

Artifact used for evidence: `flows/g1b_user_activity_spike.py`

Remote tool name: `g1b_user_activity_spike`

The initial form-based User Activity implementation failed remotely:

- first form rendered;
- `request_label` could be submitted;
- confirmation form rendered;
- retained value appeared blank;
- selecting Yes produced `Invalid 'confirmation_decision' node output. Value = {}`.

A correction based on local ADK field schemas and `.value` access still failed remotely in the
same way. This proved local ADK schema/serialization validity was insufficient to prove remote
User Activity runtime semantics.

The simplified native field-based User Activity pattern passed remotely:

- collected value;
- retained value;
- displayed explicit confirmation;
- No branch observed;
- Yes branch observed;
- no persistence;
- no side effect.

Frozen decision:

Native field-based multi-turn User Activity is the confirmation and conversational-state
strategy. Prompt-only confirmation remains forbidden. The failed form-based spike is historical
evidence and must not be treated as the production pattern.

## 6. Native Knowledge Base evidence and decision

Primary strategy proven: native watsonx Orchestrate Knowledge Base.

Authoritative HR policy sources remain Markdown under `mock_docs/`.

Platform ingestion findings:

1. The importer resolved document paths relative to the Knowledge Base YAML location, not the
   repository root assumption from the initial local test.
2. Direct `.md` ingestion was rejected as unsupported `text/markdown` in the tested path.
3. A byte-identical `.txt` representation succeeded.

Remote KB evidence:

- Knowledge Base name: `hr_leave_policy_g1b_kb`
- Knowledge Base ID: `8c8d9340-f545-44c6-9620-d71d87ee4762`
- Ready: true
- Built-in index: ready
- Document: `leave-policy.txt`
- Grounded annual-leave answer: 21 working days
- Unsupported pet-insurance question: abstained rather than inventing policy

No citation UI evidence was captured, so citation UI behavior is not claimed.

Frozen decision:

Native Orchestrate Knowledge Base remains primary. Authoritative Markdown policy sources are
preserved, and byte-identical `.txt` ingestion representations are used for tenant-compatible
native KB ingestion. Custom RAG is not active.

## 7. Persistence evidence and decision

Cloudant was the initial preferred candidate, but provisioning was blocked by IBM Cloud
account/admin approval. The original engineer requirement permits a file or simple datastore;
Cloudant was not a mandatory product requirement. IBM Cloud Object Storage was therefore
evaluated as an evidence-driven architecture amendment.

COS resources and access evidence:

- COS instance: `cos-697001jjp6`
- Dedicated bucket: `agentic-onboarding-p2-9g821`
- Region: `eu-de` / Frankfurt
- Endpoint: `https://s3.eu-de.cloud-object-storage.appdomain.cloud`
- Dedicated Service ID / credential: `project2-onboarding-cos`
- Least-privilege bucket scope: service instance `cos-697001jjp6`, resource type `bucket`,
  resource ID `agentic-onboarding-p2-9g821`
- Roles only: Object Reader, Object Writer

Remote Orchestrate connection:

- app ID: `cos_onboarding`
- Draft: `api_key_auth`, team, credentials configured
- Live: not configured

Local COS proof passed:

- IBM IAM API-key to bearer token: PASS
- token type: Bearer
- expires in: 3600 seconds
- COS PUT: HTTP 200
- object key: `g1c-persistence-probe.json`
- COS GET: HTTP 200
- semantic JSON read-back equality: PASS

Remote Orchestrate COS proof passed through evidence tool `cos_persistence_probe`:

- tool type: Python
- connection: `cos_onboarding`
- dedicated empty requirements input accepted by ADK import contract
- ADK packaging supplied `ibm-watsonx-orchestrate==2.13.0`
- no `requests`, `boto3`, `ibm-cos-sdk`, `httpx`, or `aiohttp` introduced
- temporary harness agent: `cos_persistence_probe_agent`
- harness Agent ID: `b050c969-b64a-4152-a58c-3c9a0d722ac0`
- Chat Thread ID: `157cb3b3-f634-4719-b59d-723543c2535a`

Observed remote structured result:

```json
{
  "backend": "ibm_cloud_object_storage",
  "bucket": "agentic-onboarding-p2-9g821",
  "data_match": true,
  "get_status": 200,
  "iam_authenticated": true,
  "object_key": "orchestrate-runtime-persistence-probe.json",
  "probe_id": "orchestrate-runtime-persistence",
  "put_status": 200,
  "status": "pass"
}
```

Directly proven:

watsonx Orchestrate remote Python runtime -> `cos_onboarding` connection -> IBM IAM -> COS REST
-> PUT -> GET -> semantic JSON equality.

Frozen decision:

IBM Cloud Object Storage is the simple JSON persistence backend. Persistence uses bounded JSON
objects, the `cos_onboarding` Orchestrate `API_KEY_AUTH` connection, IBM IAM token exchange,
COS REST API, Python standard-library HTTP, Python 3.12 remote runtime, and a read-only remote
filesystem assumption. No third-party COS SDK or HTTP dependency is authorized.

## 8. Final frozen platform-decision matrix

| Area | Frozen G1 decision |
|---|---|
| Production HR Agent style | ReAct Core / `react_intrinsic` |
| Selected LLM | `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` |
| Orchestrate LLM reference | `watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8` |
| Part B orchestration | watsonx Orchestrate Flow remains sole orchestrator |
| Part B LLM execution mode | `PIPELINE_LLM_MODE = PYTHON_WATSONX_TOOL` |
| Confirmation/state | native field-based multi-turn User Activity |
| Knowledge | native Orchestrate Knowledge Base |
| Knowledge source strategy | authoritative Markdown plus byte-identical `.txt` ingestion representations |
| Persistence backend | IBM Cloud Object Storage |
| Persistence format | bounded JSON objects |
| Remote credential mechanism | Orchestrate `API_KEY_AUTH` connection `cos_onboarding` |
| Persistence transport | IBM IAM token exchange plus COS REST API plus stdlib HTTP |
| Persistence dependency | no third-party COS SDK / HTTP dependency |
| Remote runtime assumption | Python 3.12, read-only filesystem |
| Custom RAG | not active |
| Cloudant | historical initial candidate only; not the frozen backend |

## 9. Important limitations and claims not made

- G1 did not implement production IT request persistence.
- G1 did not implement production orientation booking persistence.
- G1 did not prove cancel creates zero production records or confirm creates exactly one
  production record; that belongs to G2.
- G1 did not build the complete five-document HR Knowledge Base.
- G1 did not prove KB citation UI behavior.
- G1 did not implement the Part B classifier or dataset.
- G1 did not freeze a Part B review threshold.
- G1 did not configure Orchestrate Live for the COS connection.
- G1 did not prove Cloudant.
- G1 did not authorize custom RAG or a standalone Python pipeline.

## 10. Temporary remote cleanup manifest

No remote cleanup was performed by Codex during G1 closeout.

Temporary remote assets that supervisors may remove after this durable evidence is accepted:

- tool `g1b_prompt_node_spike`
- tool `g1b_user_activity_spike`
- tool `cos_persistence_probe`
- native agent `g1b_flow_test_agent_92185q`
- native agent `cos_persistence_probe_agent`
- Knowledge Base `hr_leave_policy_g1b_kb`
- COS probe object `g1c-persistence-probe.json`
- COS probe object `orchestrate-runtime-persistence-probe.json`

Resources that must not be deleted as part of temporary G1 cleanup:

- `hr_onboarding_agent`
- Orchestrate connection `cos_onboarding`
- COS bucket `agentic-onboarding-p2-9g821`
- Service ID / credential `project2-onboarding-cos`

<div align="center">

<br />

# 📋 Prior Authorization Research Agent

**Prior auth kills care delivery.**  
**AMA: 93% of physicians report care delays. 82% report patient abandonment.**  
**Clinicians spend 14+ hours per week on paperwork that delivers zero clinical value.**

This agent automates the research and justification pipeline **end-to-end** —  
policy retrieval, criteria matching, denial risk assessment, structured submission output —  
with a full append-only audit trail on every decision.

<br />

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Role--Based%20Crew-6B46C1?style=flat-square)](https://crewai.com)
[![RAG](https://img.shields.io/badge/RAG-Payer%20Policy%20Retrieval-FF6B35?style=flat-square)]()
[![CMS-0057-F](https://img.shields.io/badge/CMS--0057--F-Audit%20Compliant-22c55e?style=flat-square)]()
[![HIPAA](https://img.shields.io/badge/HIPAA-Compliant%20Design-6E93B0?style=flat-square)]()
[![Epic](https://img.shields.io/badge/Epic-FHIR%20R4%20Integration%20Path-C8102E?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](LICENSE)

<br />

[Architecture](#system-architecture) · [Agent Crew](#agent-crew) · [X12 278 Context](#the-x12-278-transaction-lifecycle) · [Denial Codes](#denial-codes-addressed) · [Quick Start](#local-development)

<br />

</div>

---

## The Real Problem

I spent 14 years architecting clinical workflows across 12 enterprise Epic health systems. Prior auth was broken at every single one of them.

The workflow looked the same everywhere:

> MA pulls the CPT. Looks up the payer portal. Navigates to the medical necessity criteria PDF. Reads through 40 pages of coverage policy. Matches clinical notes against criteria manually. Drafts a justification narrative. Submits. Waits. Gets denied. Starts over.

This happens **thousands of times per day** in every health system. There is no AI in that loop. There is no intelligence in that loop. There's just a human doing pattern matching between a PDF and a chart note.

This agent replaces that loop.

---

## What It Does

| Manual Workflow | This Agent |
|---|---|
| MA navigates payer portal manually | Policy Retriever Agent does RAG over ingested payer LCD/NCD docs |
| Clinician reads 40-page criteria PDF | Criteria Matcher Agent returns met/not-met checklist with citations |
| Staff drafts justification narrative by hand | Decision Summarizer Agent generates structured justification output |
| Denial discovered after submission | Denial risk codes flagged *before* submission with rebuttal language |
| Low-confidence cases fail silently | `HUMAN_REVIEW_FLAGGED` event surfaced explicitly for clinical escalation |
| Zero audit trail on AI-assisted decisions | Append-only event log on every agent transition, CMS-0057-F compliant |

---

## Screenshots

<img width="1433" alt="Prior Auth Agent UI — request submission" src="https://github.com/user-attachments/assets/7a6ae2d3-c4ca-498d-9f9c-2558072f71d9" />

<img width="1428" alt="Prior Auth Agent Output — justification + denial risk" src="https://github.com/user-attachments/assets/d0d7dcd0-3f1e-462c-9b0a-eb2eff175f6c" />

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     Auth Request Input                          │
│          patient context · CPT code · diagnosis · payer          │
└──────────────────────────────┬─────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│              CrewAI Sequential Agent Pipeline                    │
│                                                                  │
│  ┌─────────────────────────┐                                    │
│  │  Policy Retriever Agent          │                            │
│  │  RAG over payer LCD/NCD docs     │                            │
│  │  vector search · rerank · compress│                            │
│  └────────────┬────────────┘                                    │
│               │ criteria list                                      │
│               ▼                                                   │
│  ┌─────────────────────────┐                                    │
│  │  Criteria Matcher Agent          │                            │
│  │  clinical notes vs. policy       │                            │
│  │  met/not-met checklist + gaps    │                            │
│  └────────────┬────────────┘                                    │
│               │ match results + gaps                               │
│               ▼                                                   │
│  ┌─────────────────────────┐                                    │
│  │  Decision Summarizer Agent       │                            │
│  │  justification narrative draft   │                            │
│  │  denial risk code flagging       │                            │
│  │  Approve / Deny / Pend output    │                            │
│  └────────────┬────────────┘                                    │
│               │                                                   │
│               ▼                                                   │
│  ┌─────────────────────────┐                                    │
│  │  Confidence Check                │                            │
│  └─────┬──────────────┬──────┘                                    │
│         │ high            │ low                                   │
│         ▼                 ▼                                       │
│  ✅ Auth Request Ready   🔁 Human Review Flagged                    │
└────────────────────────────────────────────────────────────────┘
          │ Append-only audit log on every agent transition
          ▼
┌────────────────────────────────────────────────────────────────┐
│  PostgreSQL: prior_auth_audit_log (append-only)                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Agent Crew

### Core Design Principles

- **Sequential crew, not parallel** — each agent's output is the next agent's input. Policy retrieval must complete before criteria matching; criteria results must exist before denial risk assessment.
- **RAG over payer policy documents** — the Policy Retriever Agent queries a vector store of ingested payer LCD/NCD documents rather than relying on LLM training data, which is stale the moment a payer updates their policy.
- **Human review as a first-class output** — low confidence does not produce a silent failure. It produces a `HUMAN_REVIEW_FLAGGED` event and surfaces the request for clinical escalation.
- **Denial risk is preemptive** — the Decision Summarizer drafts rebuttal language for likely denial codes *before* submission, not after denial.

---

## Repository Structure

```
prior-auth-research-agent/
├── app.py                          # Streamlit UI for interactive request submission
├── main.py                         # CrewAI crew definition and kickoff entry point
├── requirements.txt
├── .env.example
│
├── audit/
│   ├── models.py                   # PriorAuthAuditEvent model (10 event types)
│   ├── logger.py                   # Append-only asyncpg writer — never raises
│   ├── queries.py                  # Denial risk summary, payer approval rates, CPT volume
│   └── migrations/
│       └── 001_create_prior_auth_audit_log.sql
│
└── tests/
    └── test_audit.py
```

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Agent Orchestration** | CrewAI | Role-based crew pattern — each agent has a distinct domain responsibility |
| **Pattern** | Sequential Multi-Agent + RAG | Policy retrieval must complete before criteria matching; no parallelism risk |
| **Retrieval** | LangChain RAG + vector store | Payer policy docs are too large and too frequently updated for LLM training data |
| **LLM** | OpenAI GPT-4o | Structured justification drafting + criteria assessment |
| **Audit Store** | PostgreSQL + asyncpg | Append-only event log with denial code array indexing |
| **UI** | Streamlit | Clinical-facing interface for request submission and output review |
| **Language** | Python 3.11+ | Async-native; Pydantic v2; type hints throughout |

---

## Prior Auth Workflow Context

### The X12 278 Transaction Lifecycle

Prior auth in production health systems follows the X12 278 EDI standard. This agent addresses steps 5–7.

| Step | Transaction | Description | Coverage |
|---|---|---|---|
| 1 | X12 270 | Eligibility inquiry | ❌ Upstream |
| 2 | X12 271 | Eligibility response | ❌ Upstream |
| 3 | X12 278 Request | Auth request submission | 📋 Roadmap |
| 4 | X12 278 Response | Payer approval/denial | 📋 Roadmap |
| 5 | Policy Research | Medical necessity criteria lookup | ✅ Policy Retriever Agent |
| 6 | Clinical Justification | Narrative drafting against criteria | ✅ Criteria Matcher Agent |
| 7 | Decision Summary | Approve / Deny / Pend rationale | ✅ Decision Summarizer Agent |
| 8 | Peer-to-Peer | Clinical escalation for denials | 📋 Roadmap |
| 9 | Appeal | Formal denial appeal submission | 📋 Roadmap |

### Denial Codes Addressed

| Code | Meaning | Agent Response |
|---|---|---|
| `CO-4` | Not authorized | Policy gaps flagged by Policy Retriever |
| `CO-50` | Not medically necessary | Clinical justification narrative built against necessity criteria |
| `CO-97` | CPT bundling conflict | CPT bundling flag in criteria match |
| `CO-167` | Diagnosis not covered | ICD-10 alignment check |
| `PR-204` | Not covered by plan | Coverage verification flag |

---

## Audit Event Lifecycle

Every agent transition writes an immutable event. No silent operations.

```
auth_request_received
    └── policy_research_started
            └── policy_research_completed
                    └── criteria_match_started
                            └── criteria_match_completed
                                    └── denial_risk_assessed
                                            └── justification_drafted
                                                    └── auth_request_ready
                                                    └── human_review_flagged
                                                    └── auth_request_failed
```

---

## Compliance Posture

- **HIPAA:** `patient_id` stored as de-identified token. Never log raw MRN, name, or DOB. Connect live Epic FHIR context only through a system-to-system SMART-on-FHIR integration with a signed BAA.
- **CMS-0057-F:** The 2024 CMS Interoperability and Prior Authorization Rule requires documentation of automated PA decision support. The `prior_auth_audit_log` append-only event log satisfies this requirement.
- **Denial Transparency:** Every `auth_request_ready` event records `denial_risk_codes[]` — the specific codes the agent preemptively addressed. Documented due diligence in any payer dispute.

---

## Known Failure Modes

Production healthcare AI needs an honest failure mode table. Here's mine.

| Failure Mode | Impact | Mitigation |
|---|---|---|
| Stale payer policy docs in vector store | Criteria mismatch — incorrect justification | Schedule nightly policy document refresh; version-stamp embeddings |
| LLM hallucinates CPT criteria | False-positive criteria-met determination | Retrieval-grounded output only — LLM must cite retrieved chunks, not training data |
| Payer changes criteria between request and response | Valid at submission, invalid at review | Log `policy_research_completed` timestamp; flag if payer policy version changed |
| Low confidence on rare CPT codes | Excessive human review flags | Expand policy corpus for rare procedures; fall back to human review explicitly |

---

## Local Development

```bash
git clone https://github.com/jsfaulkner86/prior-auth-research-agent
cd prior-auth-research-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Initialize audit log
psql $DATABASE_URL -f audit/migrations/001_create_prior_auth_audit_log.sql

# Run Streamlit UI
streamlit run app.py

# Or run headless
python main.py

# Run tests
pytest tests/ -v
```

### Environment Variables

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/prior_auth_db
AUDIT_LOG_ENABLED=true
HIPAA_MODE=true
VECTOR_STORE_PATH=./vector_store
```

---

## Roadmap

- [ ] Payer-specific policy document ingestion pipeline with version tracking
- [ ] X12 278 electronic submission integration
- [ ] Appeals agent for denied authorizations
- [ ] Epic FHIR live patient context via [`ehr-mcp`](https://github.com/jsfaulkner86/ehr-mcp)
- [ ] Peer-to-peer escalation workflow
- [ ] LangSmith tracing for production observability

---

## If You're Building Healthcare AI

If this pattern is useful to you, a ⭐ helps others find it.

If you're a health system, payer, or women's health tech company trying to automate prior auth — this is the kind of system I architect at [The Faulkner Group](https://thefaulknergroupadvisors.com).

---

<div align="center">

*Part of The Faulkner Group's healthcare agentic AI portfolio → [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*

*Built from 14 years and 12 Epic enterprise health system deployments.*

</div>

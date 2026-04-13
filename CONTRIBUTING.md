# Contributing to Prior Auth Research Agent

Prior authorization is one of the most broken workflows in healthcare. This agent exists to automate it. If you've been on the receiving end of a PA denial — as a clinician, patient, or operator — you understand why this matters.

Contributions that make this agent faster, more accurate, or more clinically useful are welcome.

This project is maintained by [John Faulkner](https://linkedin.com/in/johnathonfaulkner) and [The Faulkner Group](https://thefaulknergroupadvisors.com).

---

## What We're Building

A CrewAI + RAG multi-agent system that automates prior authorization research: identifying payer requirements, matching clinical criteria, and generating structured PA justification documentation — purpose-built for healthcare AI.

---

## Ways to Contribute

- **New payer coverage** — Add or improve payer-specific PA criteria for additional procedures or diagnoses
- **RAG improvements** — Better chunking strategies, re-ranking, hybrid search, or alternative vector stores
- **Agent role additions** — New specialized agents (e.g. appeals agent, CPT code validator)
- **Pydantic schema improvements** — Stronger structured output models for PA documentation
- **Test cases** — Synthetic PA scenarios with expected outcomes for regression testing
- **Documentation** — Clearer setup guides, clinical context, example walkthroughs
- **Bug reports** — Open an issue with reproduction steps and payer/procedure context if relevant

---

## Getting Started

```bash
git clone https://github.com/jsfaulkner86/prior-auth-research-agent
cd prior-auth-research-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your `OPENAI_API_KEY` (or Anthropic key) to `.env`. No real EHR connection is required for development — the agent works against synthetic PA scenarios.

To run the Streamlit UI:

```bash
streamlit run app.py
```

To run the CLI:

```bash
python main.py
```

---

## Contribution Guidelines

- **No PHI in commits** — All test cases and examples must use synthetic or fully de-identified data. No real patient names, MRNs, DOBs, or clinical notes.
- **One concern per PR** — Keep pull requests focused. A PR that adds a new payer AND refactors the RAG pipeline is two PRs.
- **Document the clinical context** — If you add a new payer rule, procedure category, or agent role, explain the clinical problem it solves in plain language in the PR description.
- **HIPAA awareness** — If your contribution touches data ingestion, storage, or output, note any compliance considerations explicitly.
- **Follow existing patterns** — Agent roles live in `agents/`; tools in `tools/`; Pydantic schemas in `schemas.py`. New work should fit existing structure or propose a documented architectural change.
- **Python 3.11+** — Type hints on all functions. Pydantic v2 for all structured models.

---

## Opening an Issue

Use GitHub Issues for:
- Bug reports (include payer type, procedure context, and error trace if available)
- Feature requests (describe the clinical use case first, then the technical ask)
- PA workflow gaps you've encountered in production

The most valuable issues come from people who have actually worked in revenue cycle, prior auth, or clinical operations. Don't hesitate to share that context.

---

## Code of Conduct

This project exists to reduce administrative burden on clinicians and improve patient access to care. Contributions should reflect that mission. Be respectful, be precise, and remember that PA delays have real consequences for real patients.

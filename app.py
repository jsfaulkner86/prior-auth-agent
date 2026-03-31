# app.py — Prior Authorization Research Agent
# Streamlit demo wrapper for The Faulkner Group
# Wires the 3-agent CrewAI pipeline to a web UI

import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Prior Auth Research Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏥 Prior Auth Agent")
    st.markdown("**The Faulkner Group**")
    st.divider()

    st.markdown("### Agent Pipeline")
    st.markdown(
        """
1. **Policy Retriever** — Fetches payer-specific medical necessity criteria for the CPT code  
2. **Criteria Matcher** — Compares clinical notes against criteria; flags met vs. missing  
3. **Decision Summarizer** — Generates Approve / Deny / Pend recommendation with rationale
        """
    )
    st.divider()

    st.markdown("### Sample CPT Codes")
    st.markdown(
        """
| Code | Procedure |
|------|-----------|
| 27447 | Total Knee Arthroplasty |
| 27130 | Total Hip Arthroplasty |
| 43239 | Upper GI Endoscopy w/ Biopsy |
| 70553 | MRI Brain w/ Contrast |
| 63047 | Lumbar Laminectomy |
        """
    )
    st.divider()

    st.caption(
        "⚠️ This is a demonstration tool. Output is AI-generated and does not constitute "
        "medical or legal advice. Do not use with real PHI."
    )

# ── HEADER ─────────────────────────────────────────────────────────────────────

st.title("Prior Authorization Research Agent")
st.markdown(
    "Enter a CPT code, payer name, and clinical notes below. "
    "The 3-agent CrewAI pipeline will retrieve payer policy criteria, "
    "match against the clinical documentation, and return a decision recommendation."
)

# ── INPUT FORM ─────────────────────────────────────────────────────────────────

with st.form("prior_auth_form"):
    col1, col2 = st.columns(2)

    with col1:
        cpt_code = st.text_input(
            "CPT Code",
            value="27447",
            help="Procedure code for the requested service (e.g. 27447 = Total Knee Arthroplasty)",
        )
    with col2:
        payer_name = st.text_input(
            "Payer Name",
            value="Blue Cross Blue Shield",
            help="Insurance payer whose policy will be retrieved",
        )

    clinical_notes = st.text_area(
        "Clinical Notes",
        height=220,
        value=(
            "Patient is a 67-year-old female with severe osteoarthritis of the right knee. "
            "X-rays confirm grade IV joint space narrowing. Conservative treatment including "
            "6 months of physical therapy, NSAIDs, and two corticosteroid injections have "
            "failed to provide relief. Patient reports 8/10 pain and significant functional "
            "limitation affecting activities of daily living. BMI is 28. No active infection "
            "or bleeding disorder. Patient is medically cleared for surgery."
        ),
        help="Paste or type the relevant clinical documentation for this request",
    )

    submitted = st.form_submit_button(
        "▶  Run Prior Auth Analysis",
        type="primary",
        use_container_width=True,
    )

# ── RUN PIPELINE ───────────────────────────────────────────────────────────────

if submitted:
    # Validate API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "**OPENAI_API_KEY not found.** "
            "If you are running this locally, create a `.env` file with `OPENAI_API_KEY=sk-...`. "
            "On Streamlit Community Cloud, add it under Settings → Secrets."
        )
        st.stop()

    if not cpt_code.strip() or not payer_name.strip() or not clinical_notes.strip():
        st.warning("Please fill in all three fields before running.")
        st.stop()

    st.divider()
    st.subheader("Analysis Results")

    # Live status container
    with st.status("Running 3-agent CrewAI pipeline...", expanded=True) as status:
        st.write("🔍 Agent 1: Retrieving payer policy criteria...")

        try:
            # ── LLM ──────────────────────────────────────────────────────────
            llm = ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=api_key)

            # ── AGENTS ───────────────────────────────────────────────────────

            policy_retriever = Agent(
                role="Policy Retriever",
                goal="Retrieve the correct payer policy criteria for the given CPT code",
                backstory=(
                    "You are a specialist in insurance payer policies. "
                    "You know exactly where to find coverage criteria for any procedure code "
                    "and return only what is clinically relevant for the authorization request."
                ),
                llm=llm,
                verbose=False,
            )

            criteria_matcher = Agent(
                role="Clinical Criteria Matcher",
                goal="Compare the patient's clinical notes against payer approval criteria",
                backstory=(
                    "You are a clinical reviewer with deep knowledge of medical necessity standards. "
                    "You match documented clinical findings to payer criteria with precision, "
                    "flagging gaps or missing documentation."
                ),
                llm=llm,
                verbose=False,
            )

            decision_summarizer = Agent(
                role="Decision Summarizer",
                goal="Generate a clear approval or denial rationale based on the criteria match",
                backstory=(
                    "You are a medical director experienced in prior authorization decisions. "
                    "You produce clear, defensible rationale that satisfies both clinical "
                    "and administrative stakeholders."
                ),
                llm=llm,
                verbose=False,
            )

            # ── TASKS ────────────────────────────────────────────────────────

            retrieve_policy = Task(
                description=(
                    f"Retrieve the payer policy for CPT code {cpt_code} "
                    f"from payer {payer_name}. Return the medical necessity criteria "
                    "required for approval as a numbered list."
                ),
                expected_output="A structured numbered list of medical necessity criteria for the procedure.",
                agent=policy_retriever,
            )

            st.write("🧬 Agent 2: Matching clinical notes to criteria...")

            match_criteria = Task(
                description=(
                    f"Review the following clinical notes and compare them "
                    f"against the retrieved payer criteria for CPT {cpt_code}:\n\n"
                    f"Clinical Notes: {clinical_notes}\n\n"
                    "For each criterion, state whether it is MET or NOT MET based on the documentation. "
                    "Flag any documentation gaps that would need to be resolved."
                ),
                expected_output=(
                    "A criteria checklist showing each criterion with status (MET / NOT MET / UNCLEAR) "
                    "and a brief explanation. Include a documentation gaps section."
                ),
                agent=criteria_matcher,
            )

            st.write("📋 Agent 3: Generating decision recommendation...")

            summarize_decision = Task(
                description=(
                    "Based on the criteria match results, generate a prior authorization "
                    "decision summary. Structure your output with these exact sections:\n"
                    "1. RECOMMENDATION: (APPROVE / DENY / PEND FOR ADDITIONAL INFORMATION)\n"
                    "2. CLINICAL RATIONALE: (2-4 sentences)\n"
                    "3. CRITERIA MET: (bullet list)\n"
                    "4. CRITERIA NOT MET OR MISSING: (bullet list, or 'None')\n"
                    "5. ADDITIONAL DOCUMENTATION REQUIRED: (bullet list, or 'None')"
                ),
                expected_output=(
                    "A structured prior authorization decision summary with recommendation, "
                    "rationale, and documentation requirements."
                ),
                agent=decision_summarizer,
            )

            # ── CREW ─────────────────────────────────────────────────────────

            prior_auth_crew = Crew(
                agents=[policy_retriever, criteria_matcher, decision_summarizer],
                tasks=[retrieve_policy, match_criteria, summarize_decision],
                process=Process.sequential,
                verbose=False,
            )

            result = prior_auth_crew.kickoff(
                inputs={
                    "cpt_code": cpt_code,
                    "payer_name": payer_name,
                    "clinical_notes": clinical_notes,
                }
            )

            status.update(label="✅ Analysis complete", state="complete", expanded=False)

        except Exception as e:
            status.update(label="❌ Pipeline error", state="error", expanded=True)
            st.error(f"**Agent error:** {e}")
            st.stop()

    # ── OUTPUT ───────────────────────────────────────────────────────────────

    result_text = str(result)

    # Determine recommendation badge color
    rec_color = "🟡"  # default: pend
    if "APPROVE" in result_text.upper() and "NOT APPROVE" not in result_text.upper():
        rec_color = "🟢"
    elif "DENY" in result_text.upper():
        rec_color = "🔴"

    col_badge, col_meta = st.columns([1, 2])
    with col_badge:
        if "APPROVE" in result_text.upper() and "NOT APPROVE" not in result_text.upper():
            st.success("**Recommendation: APPROVE**")
        elif "DENY" in result_text.upper():
            st.error("**Recommendation: DENY**")
        else:
            st.warning("**Recommendation: PEND / MORE INFO NEEDED**")

    with col_meta:
        st.markdown(f"**CPT Code:** `{cpt_code}`")
        st.markdown(f"**Payer:** {payer_name}")

    st.divider()

    st.markdown("### Full Decision Output")
    st.markdown(result_text)

    # Download button
    st.download_button(
        label="⬇ Download Decision Report (.txt)",
        data=f"Prior Auth Decision Report\nCPT: {cpt_code} | Payer: {payer_name}\n\n{result_text}",
        file_name=f"prior_auth_{cpt_code}_{payer_name.replace(' ', '_')}.txt",
        mime="text/plain",
    )

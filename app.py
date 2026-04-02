# app.py — Prior Authorization Research Agent
# Streamlit demo wrapper for The Faulkner Group
# Wires the 3-agent CrewAI pipeline to a web UI

import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Prior Auth Research Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── TFG BRAND THEME ────────────────────────────────────────────────────────────
# Colors: Blue #6E93B0 | Gold #D4AE48
# Dark navy backgrounds, gold accents, blue for interactive/info elements

st.markdown(
    """
    <style>
    /* ── Root palette ───────────────────────────────────────────────── */
    :root {
        --tfg-blue:        #6E93B0;
        --tfg-blue-light:  #8AAEC6;
        --tfg-blue-dark:   #4E7A9A;
        --tfg-gold:        #D4AE48;
        --tfg-gold-light:  #E2C46A;
        --tfg-gold-dark:   #B8912A;
        --tfg-bg:          #0F1117;
        --tfg-surface:     #1C2333;
        --tfg-surface-2:   #232B3E;
        --tfg-border:      rgba(110, 147, 176, 0.2);
        --tfg-text:        #E8EDF2;
        --tfg-text-muted:  #9AABB8;
    }

    /* ── App background ─────────────────────────────────────────────── */
    .stApp {
        background-color: var(--tfg-bg);
        color: var(--tfg-text);
    }

    /* ── Sidebar ────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: var(--tfg-surface);
        border-right: 1px solid var(--tfg-border);
    }
    [data-testid="stSidebar"] * {
        color: var(--tfg-text) !important;
    }
    [data-testid="stSidebar"] .stMarkdown table th {
        color: var(--tfg-gold) !important;
        border-bottom: 1px solid var(--tfg-border);
    }
    [data-testid="stSidebar"] .stMarkdown table td {
        color: var(--tfg-text-muted) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--tfg-border);
    }

    /* ── Page title & headings ──────────────────────────────────────── */
    h1 {
        color: var(--tfg-gold) !important;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    h2, h3 {
        color: var(--tfg-blue-light) !important;
        font-weight: 600;
    }

    /* ── Text ───────────────────────────────────────────────────────── */
    p, li, .stMarkdown {
        color: var(--tfg-text) !important;
    }

    /* ── Form inputs ────────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: var(--tfg-surface-2) !important;
        color: var(--tfg-text) !important;
        border: 1px solid var(--tfg-border) !important;
        border-radius: 6px !important;
        caret-color: var(--tfg-gold);
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--tfg-blue) !important;
        box-shadow: 0 0 0 2px rgba(110, 147, 176, 0.25) !important;
    }

    /* ── Input labels ───────────────────────────────────────────────── */
    .stTextInput label,
    .stTextArea label {
        color: var(--tfg-blue-light) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }

    /* ── Primary button (Run Analysis) ─────────────────────────────── */
    .stFormSubmitButton > button[kind="primaryFormSubmit"],
    .stButton > button[kind="primary"] {
        background-color: var(--tfg-gold) !important;
        color: #0F1117 !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        border-radius: 6px !important;
        transition: background-color 150ms ease !important;
    }
    .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: var(--tfg-gold-light) !important;
    }

    /* ── Secondary / download buttons ──────────────────────────────── */
    .stDownloadButton > button,
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: var(--tfg-blue-light) !important;
        border: 1px solid var(--tfg-blue) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover,
    .stButton > button[kind="secondary"]:hover {
        background-color: rgba(110, 147, 176, 0.12) !important;
    }

    /* ── Status / spinner box ───────────────────────────────────────── */
    [data-testid="stStatus"] {
        background-color: var(--tfg-surface) !important;
        border: 1px solid var(--tfg-border) !important;
        border-radius: 8px !important;
        color: var(--tfg-text) !important;
    }
    [data-testid="stStatus"] * {
        color: var(--tfg-text) !important;
    }

    /* ── Alert boxes ────────────────────────────────────────────────── */
    /* Success = APPROVE */
    [data-testid="stAlert"][data-baseweb="notification"][kind="success"],
    div.stSuccess {
        background-color: rgba(110, 147, 176, 0.15) !important;
        border-left: 4px solid var(--tfg-blue) !important;
        color: var(--tfg-text) !important;
    }
    /* Error = DENY */
    div.stError {
        background-color: rgba(180, 60, 60, 0.15) !important;
        border-left: 4px solid #B43C3C !important;
        color: var(--tfg-text) !important;
    }
    /* Warning = PEND */
    div.stWarning {
        background-color: rgba(212, 174, 72, 0.15) !important;
        border-left: 4px solid var(--tfg-gold) !important;
        color: var(--tfg-text) !important;
    }
    /* Info */
    div.stInfo {
        background-color: rgba(110, 147, 176, 0.12) !important;
        border-left: 4px solid var(--tfg-blue) !important;
        color: var(--tfg-text) !important;
    }
    /* Fix white text inside all alert types */
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    div.stSuccess p, div.stError p, div.stWarning p, div.stInfo p {
        color: var(--tfg-text) !important;
    }

    /* ── Dividers ───────────────────────────────────────────────────── */
    hr {
        border-color: var(--tfg-border) !important;
    }

    /* ── Code / inline code ─────────────────────────────────────────── */
    code {
        background-color: var(--tfg-surface-2) !important;
        color: var(--tfg-gold) !important;
        border-radius: 4px;
        padding: 1px 5px;
    }
    pre {
        background-color: var(--tfg-surface-2) !important;
        border: 1px solid var(--tfg-border) !important;
        border-radius: 6px;
    }
    pre code {
        color: var(--tfg-blue-light) !important;
    }

    /* ── Caption / small text ───────────────────────────────────────── */
    .stCaption, small, .caption {
        color: var(--tfg-text-muted) !important;
    }

    /* ── Spinner label ──────────────────────────────────────────────── */
    .stSpinner > div > div {
        border-top-color: var(--tfg-gold) !important;
    }

    /* ── TFG header branding bar ────────────────────────────────────── */
    .tfg-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0 16px 0;
        border-bottom: 1px solid var(--tfg-border);
        margin-bottom: 20px;
    }
    .tfg-header-logo {
        width: 36px;
        height: 36px;
    }
    .tfg-header-text {
        font-size: 0.75rem;
        color: var(--tfg-text-muted);
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* ── Result output card ─────────────────────────────────────────── */
    .result-card {
        background-color: var(--tfg-surface) !important;
        border: 1px solid var(--tfg-border);
        border-radius: 8px;
        padding: 20px 24px;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── TFG BRANDING HEADER ────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="tfg-header">
        <svg class="tfg-header-logo" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="The Faulkner Group">
            <rect width="36" height="36" rx="6" fill="#1C2333"/>
            <path d="M8 10h20M8 18h12M8 26h16" stroke="#D4AE48" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="27" cy="26" r="4" fill="#6E93B0"/>
        </svg>
        <span class="tfg-header-text">The Faulkner Group &nbsp;·&nbsp; Agentic AI</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Prior Auth Agent")
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
        "⚠️ Demonstration tool only. Output is AI-generated and does not constitute "
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
    api_key = os.getenv("PERPLEXITY_API_KEY") or os.getenv("PPLX_API_KEY")
    if not api_key:
        st.error(
            "**PERPLEXITY_API_KEY not found.** "
            "If running locally, add `PERPLEXITY_API_KEY=pplx-...` to your `.env` file. "
            "On Streamlit Community Cloud, add it under Settings → Secrets as:\n\n"
            "```toml\nPERPLEXITY_API_KEY = \"pplx-...\"\n```"
        )
        st.stop()

    if not cpt_code.strip() or not payer_name.strip() or not clinical_notes.strip():
        st.warning("Please fill in all three fields before running.")
        st.stop()

    st.divider()
    st.subheader("Analysis Results")

    with st.status("Running 3-agent CrewAI pipeline...", expanded=True) as status:
        st.write("🔍 Agent 1: Retrieving payer policy criteria...")

        try:
            # ── LLM: Perplexity Sonar Pro via crewai.LLM (LiteLLM provider prefix)
            # stop=[] suppresses CrewAI's default "\nObservation" stop words,
            # which Perplexity rejects with a 400 unsupported_parameter error.
            llm = LLM(
                model="perplexity/sonar-pro",
                api_key=api_key,
                temperature=0.2,
                stop=[],
            )

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
                context=[retrieve_policy],
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
                context=[match_criteria],
            )

            prior_auth_crew = Crew(
                agents=[policy_retriever, criteria_matcher, decision_summarizer],
                tasks=[retrieve_policy, match_criteria, summarize_decision],
                process=Process.sequential,
                verbose=False,
            )

            result = prior_auth_crew.kickoff()

            status.update(label="✅ Analysis complete", state="complete", expanded=False)

        except Exception as e:
            status.update(label="❌ Pipeline error", state="error", expanded=True)
            st.error(f"**Agent error:** {e}")
            st.stop()

    # ── OUTPUT ───────────────────────────────────────────────────────────────

    result_text = str(result)

    col_badge, col_meta = st.columns([1, 2])
    with col_badge:
        if "APPROVE" in result_text.upper() and "NOT APPROVE" not in result_text.upper() and "DENY" not in result_text.upper():
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
    st.markdown(
        f'<div class="result-card">{result_text}</div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        label="⬇ Download Decision Report (.txt)",
        data=f"Prior Auth Decision Report\nCPT: {cpt_code} | Payer: {payer_name}\n\n{result_text}",
        file_name=f"prior_auth_{cpt_code}_{payer_name.replace(' ', '_')}.txt",
        mime="text/plain",
    )

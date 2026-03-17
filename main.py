from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.2)

# ── AGENTS ──────────────────────────────────────────────

policy_retriever = Agent(
    role="Policy Retriever",
    goal="Retrieve the correct payer policy criteria for the given CPT code",
    backstory="""You are a specialist in insurance payer policies. 
    You know exactly where to find coverage criteria for any procedure code 
    and return only what is clinically relevant for the authorization request.""",
    llm=llm,
    verbose=True
)

criteria_matcher = Agent(
    role="Clinical Criteria Matcher",
    goal="Compare the patient's clinical notes against payer approval criteria",
    backstory="""You are a clinical reviewer with deep knowledge of 
    medical necessity standards. You match documented clinical findings 
    to payer criteria with precision, flagging gaps or missing documentation.""",
    llm=llm,
    verbose=True
)

decision_summarizer = Agent(
    role="Decision Summarizer",
    goal="Generate a clear approval or denial rationale based on the criteria match",
    backstory="""You are a medical director experienced in prior authorization 
    decisions. You produce clear, defensible rationale that satisfies both 
    clinical and administrative stakeholders.""",
    llm=llm,
    verbose=True
)

# ── TASKS ──────────────────────────────────────────────

retrieve_policy = Task(
    description="""Retrieve the payer policy for CPT code {cpt_code} 
    from payer {payer_name}. Return the medical necessity criteria 
    required for approval.""",
    expected_output="A structured list of medical necessity criteria for the procedure.",
    agent=policy_retriever
)

match_criteria = Task(
    description="""Review the following clinical notes and compare them 
    against the retrieved payer criteria:
    
    Clinical Notes: {clinical_notes}
    
    Identify which criteria are met, which are missing, and flag 
    any documentation gaps.""",
    expected_output="A criteria checklist with met/not met status and documentation gaps.",
    agent=criteria_matcher
)

summarize_decision = Task(
    description="""Based on the criteria match results, generate a prior 
    authorization decision summary. Include: 
    - Recommendation (Approve / Deny / Pend for more info)
    - Clinical rationale
    - Any additional documentation required""",
    expected_output="A prior authorization decision summary with rationale.",
    agent=decision_summarizer
)

# ── CREW ──────────────────────────────────────────────

prior_auth_crew = Crew(
    agents=[policy_retriever, criteria_matcher, decision_summarizer],
    tasks=[retrieve_policy, match_criteria, summarize_decision],
    process=Process.sequential,
    verbose=True
)

# ── RUN ──────────────────────────────────────────────

if __name__ == "__main__":
    # Mock inputs — replace with real data pipeline
    result = prior_auth_crew.kickoff(inputs={
        "cpt_code": "27447",  # Total knee arthroplasty
        "payer_name": "Blue Cross Blue Shield",
        "clinical_notes": """
            Patient is a 67-year-old female with severe osteoarthritis 
            of the right knee. X-rays confirm grade IV joint space narrowing. 
            Conservative treatment including 6 months of physical therapy, 
            NSAIDs, and two corticosteroid injections have failed to provide 
            relief. Patient reports 8/10 pain and significant functional limitation.
        """
    })

    print("\n── PRIOR AUTH DECISION ──")
    print(result)

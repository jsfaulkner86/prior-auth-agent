# app.py
import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

st.set_page_config(
    page_title="Prior Auth Research Agent",
    page_icon="🏥",
    layout="wide"
)

st.title("Prior Authorization Research Agent")
st.caption("AI-powered prior auth decision support · The Faulkner Group")

with st.form("prior_auth_form"):
    col1, col2 = st.columns(2)
    with col1:
        cpt_code = st.text_input("CPT Code", value="27447", help="e.g. 27447 for Total Knee Arthroplasty")
    with col2:
        payer_name = st.text_input("Payer Name", value="Blue Cross Blue Shield")
    
    clinical_notes = st.text_area(
        "Clinical Notes",
        height=200,
        value="""Patient is a 67-year-old female with severe osteoarthritis of the right knee. 
X-rays confirm grade IV joint space narrowing. Conservative treatment including 
6 months of physical therapy, NSAIDs, and two corticosteroid injections have 
failed to provide relief. Patient reports 8/10 pain and significant functional limitation."""
    )
    
    submitted = st.form_submit_button("Run Prior Auth Analysis", type="primary")

if submitted:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY not configured. Add it in Streamlit Cloud secrets.")
        st.stop()
    
    with st.spinner("Running 3-agent CrewAI analysis... this takes ~30-60 seconds"):
        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
            
            # ... (agents and tasks from main.py) ...
            
            result = prior_auth_crew.kickoff(inputs={
                "cpt_code": cpt_code,
                "payer_name": payer_name,
                "clinical_notes": clinical_notes
            })
            
            st.success("Analysis complete")
            st.subheader("Prior Auth Decision")
            st.markdown(str(result))
        
        except Exception as e:
            st.error(f"Agent error: {e}")

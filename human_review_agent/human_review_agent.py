# agent_7_human_review/human_review_agent.py

import json
import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from config.settings import DEFAULT_MODEL_ID
from utils.prompts import HUMAN_REVIEW_AGENT_ROLE, HUMAN_REVIEW_AGENT_INSTRUCTIONS

# -----------------------------------------------------------------
# PART 1: THE AGENT'S "BRAIN" (No Change)
# -----------------------------------------------------------------

def create_human_review_agent() -> Agent:
    """
    Factory function to create the Human Review Agent.
    This agent's *only* job is to summarize the case data.
    """
    
    human_review_llm = Gemini(id=DEFAULT_MODEL_ID)
    
    human_review_agent = Agent(
        name="HumanReviewAgent",
        role=HUMAN_REVIEW_AGENT_ROLE,
        instructions=HUMAN_REVIEW_AGENT_INSTRUCTIONS,
        model=human_review_llm,
        tools=[],
        markdown=True
    )
    
    return human_review_agent

# -----------------------------------------------------------------
# PART 2: THE AGENT'S "UI" (--- THIS IS THE FIX ---)
# -----------------------------------------------------------------

def render_hitl_ui(case_summary: str, app_state: dict) -> str | None:
    """
    This function renders the dashboard for the human analyst.
    It now shows CONTEXTUAL buttons based on the trigger step.
    
    Args:
        case_summary: The AI-generated summary.
        app_state: The full application state.
        
    Returns:
        The human's decision (e.g., "CONTINUE_TO_KYC", "REJECTED", etc.)
    """
    
    reason = app_state.get("reason_for_review", "No reason specified.")
    trigger_step = app_state.get("trigger_step", "")
    
    st.warning(f"**CASE FLAGGED FOR HUMAN REVIEW**\n\n**Reason:** {reason}")
    st.markdown("---")
    
    st.subheader("AI-Generated Case Summary")
    st.markdown(case_summary)
    st.markdown("---")
    
    # Create tabs to show the raw data
    st.subheader("Full Case Data")
    tab1, tab2, tab3 = st.tabs(["Document Data", "KYC Report", "Credit Analysis"])
    
    with tab1:
        st.json(app_state.get("document_data", "No data"))
    with tab2:
        st.json(app_state.get("kyc_report", "No data"))
    with tab3:
        st.json(app_state.get("credit_analysis", "No data"))
        
    st.markdown("---")
    
    # Get the human's decision
    st.subheader("Analyst Decision")
    analyst_notes = st.text_area("Analyst Notes (Required)")
    
    col1, col2 = st.columns(2)
    
    human_decision = None
    
    # --- THIS IS THE NEW LOGIC ---
    
    # If the review was triggered by the final credit check, show FINAL approval.
    if trigger_step == "CREDIT_ANALYSIS":
        with col1:
            if st.button("Approve Application", type="primary"):
                human_decision = "FINAL_APPROVE"
        with col2:
            if st.button("Reject Application", type="secondary"):
                human_decision = "REJECTED"
    
    # If triggered by an earlier step (Doc or KYC), show "Continue" button.
    else:
        with col1:
            if st.button("Clear Issue & Continue", type="primary"):
                if trigger_step == "DOC_VERIFICATION":
                    human_decision = "CONTINUE_TO_KYC"
                elif trigger_step == "KYC_CHECKS":
                    human_decision = "CONTINUE_TO_CREDIT"
                else: # Failsafe
                    human_decision = "REJECTED" 
        with col2:
            if st.button("Reject Application", type="secondary"):
                human_decision = "REJECTED"

    # Check if notes are provided
    if human_decision:
        if analyst_notes:
            app_state["human_notes"] = analyst_notes
            return human_decision
        else:
            st.error("Please provide analyst notes before making a decision.")
            
    return None

# -----------------------------------------------------------------
# PART 3: TEST THE AGENT'S "BRAIN" (No Change)
# -----------------------------------------------------------------

if __name__ == "__main__":
    from dotenv import load_dotenv
    import json
    
    load_dotenv()
    
    print("--- Testing Human Review Agent's Brain (Summarization) ---")
    hitl_agent = create_human_review_agent()
    
    fake_case_data = {
        "reason_for_review": "Credit score in 'gray zone' (65)",
        "trigger_step": "CREDIT_ANALYSIS",
        "document_data": {"status": "All documents consistent"},
        "kyc_report": {"risk_score": "Low"},
        "credit_analysis": {"credit_score": 65}
    }
    
    test_query = f"Please summarize this case data: {json.dumps(fake_case_data)}"
    hitl_agent.print_response(test_query)
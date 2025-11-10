# main.py (Manual, Robust, FINAL)

import streamlit as st
import os
import json
import time
import re # <-- Import Regular Expressions
from dotenv import load_dotenv

# --- 1. Import all our agent factory functions ---
from orchestrator_agent.orchestrator import create_orchestrator_agent

from doc_intel_agent.document_agent import create_document_agent

from kyc_agent.kyc_agent import create_kyc_agent

from credit_agent.credit_agent import create_credit_agent

from product_agent.product_agent import create_product_agent

from commn_agent.commn_agent import create_communication_agent

from human_review_agent.human_review_agent import create_human_review_agent, render_hitl_ui
# --- Import the tool for Agent 6 ---
from utils.tools.communication_tools import send_customer_communication

# --- 2. Load Environment Variables ---
load_dotenv()

# -----------------------------------------------------------------
# --- 3. HELPER FUNCTION: "Safe JSON Parser" ---
# -----------------------------------------------------------------

def safe_json_load(agent_response_content: str) -> dict:
    """
    Tries to find and parse a JSON object from an agent's
    potentially conversational response.
    """
    # 1. Try to find a JSON markdown block (e.g., ```json {...} ```)
    match = re.search(r'```json\s*(\{.*?\})\s*```', agent_response_content, re.DOTALL)
    
    if match:
        json_str = match.group(1)
    else:
        # 2. If no markdown, find the first '{' and last '}'
        match = re.search(r'(\{.*\})', agent_response_content, re.DOTALL)
        
        if not match:
            # No JSON object found at all.
            return {
                "error": "Agent did not return a valid JSON object.",
                "raw_response": agent_response_content
            }
        json_str = match.group(0)
    
    try:
        # Try to parse the found JSON
        return json.loads(json_str)
    except json.JSONDecodeError:
        # The found text was not valid JSON.
        return {
            "error": "Agent returned malformed JSON.",
            "raw_response": json_str
        }

# -----------------------------------------------------------------
# --- 4. App Configuration & Agent Initialization ---
# -----------------------------------------------------------------

st.set_page_config(
    page_title="TechVenture Bank Onboarding",
    page_icon="🏦",
    layout="wide"
)
st.title("🏦 TechVenture Bank: Multi-Agent Onboarding System")

@st.cache_resource
def load_all_agents():
    """Create and cache one instance of all 7 agents."""
    print("--- Caching all agents ---")
    agents = {
        "OrchestratorAgent": create_orchestrator_agent(),
        "DocumentIntelligenceAgent": create_document_agent(),
        "KYCAgent": create_kyc_agent(),
        "CreditAgent": create_credit_agent(),
        "ProductAgent": create_product_agent(),
        "CommunicationAgent": create_communication_agent(),
        "HumanReviewAgent": create_human_review_agent()
    }
    return agents

agents = load_all_agents()

# --- 5. Initialize Session State (Our "Persistent Memory") ---
if "application_state" not in st.session_state:
    st.session_state.application_state = {
        "status": "NONE", "business_name": "", "owner_name": "", "file_path": "",
        "chat_log": [], "document_data": {}, "kyc_report": {},
        "credit_analysis": {}, "product_recommendation": {},
        "final_decision": "", "reason_for_review": "",
        "trigger_step": "" # <-- Stores HITL CONTEXT
    }

# -----------------------------------------------------------------
# --- 6. The "Manual" Workflow Logic ---
# -----------------------------------------------------------------

def run_next_step():
    """
    This is our robust, manual, linear workflow.
    It runs the next agent based on the current status.
    """
    app_state = st.session_state.application_state
    current_status = app_state["status"]

    try:
        # --- STEP 1: PENDING -> Run Document Agent ---
        if current_status == "PENDING":
            app_state["status"] = "DOC_VERIFICATION" # Mark as "in progress"
            st.rerun() # Re-run to show the spinner
            
        elif current_status == "DOC_VERIFICATION":
            with st.spinner("Document Agent is analyzing PDF..."):
                doc_agent = agents["DocumentIntelligenceAgent"]
                query = f"Please analyze the application document at '{app_state['file_path']}'."
                response_str = doc_agent.run(query).content
                response_json = safe_json_load(response_str) # Use safe parser
                
                if "error" in response_json:
                    raise Exception(f"DocumentAgent failed: {response_json['error']}")
                
                if "extracted_data" in response_json:
                    app_state["owner_name"] = response_json["extracted_data"].get("Full Name", "")
                
                app_state["document_data"] = response_json
                app_state["status"] = response_json.get("state_recommendation", "ERROR")
                app_state["chat_log"].append(f"Document Agent: {response_json.get('reasoning', 'No reasoning.')}")
                
                if app_state["status"] == "AWAITING_REVIEW (HITL)":
                    app_state["reason_for_review"] = response_json.get("reasoning", "Doc Agent flagged for review.")
                    app_state["trigger_step"] = "DOC_VERIFICATION" # <-- Store the trigger

        # --- STEP 2: KYC_CHECKS -> Run KYC Agent (FIXED) ---
        elif current_status == "KYC_CHECKS":
            with st.spinner("KYC Agent is running checks..."):
                kyc_agent = agents["KYCAgent"]
                query = f"Perform KYC/AML checks on business: '{app_state['business_name']}' and owner: '{app_state['owner_name']}'"
                response_str = kyc_agent.run(query).content
                response_json = safe_json_load(response_str)
                
                if "error" in response_json:
                    raise Exception(f"KYCAgent failed: {response_json['error']}")
                
                # --- THIS IS THE FIX ---
                # We are now correctly reading the NESTED keys
                app_state["kyc_report"] = response_json
                app_state["status"] = response_json.get("recommendation", {}).get("next_state", "ERROR")
                app_state["chat_log"].append(f"KYC Agent: {response_json.get('summary', {}).get('findings', 'No findings.')}")
                
                if app_state["status"] == "AWAITING_REVIEW (HITL)":
                    app_state["reason_for_review"] = response_json.get("recommendation", {}).get("reason", "KYC Agent flagged for review.")
                    app_state["trigger_step"] = "KYC_CHECKS" # Store the trigger
                # --- END OF FIX ---

        # --- STEP 3: CREDIT_ANALYSIS -> Run Credit Agent (FIXED) ---
        elif current_status == "CREDIT_ANALYSIS":
            with st.spinner("Credit Agent is analyzing financials..."):
                credit_agent = agents["CreditAgent"]
                doc_data = app_state["document_data"].get("extracted_data", {})
                financial_data = {
                    "revenue": doc_data.get("Annual Revenue", 0),
                    "net_income": doc_data.get("Net Income", 0),
                    "total_debt": doc_data.get("Total Business Debt", 0),
                    "total_assets": doc_data.get("Total Business Assets", 0)
                }
                doc_data_str = json.dumps(financial_data)
                
                query = f"Please analyze the financial data: {doc_data_str}"
                response_str = credit_agent.run(query).content
                response_json = safe_json_load(response_str)
                
                if "error" in response_json:
                    raise Exception(f"CreditAgent failed: {response_json['error']}")
                
                # --- THIS IS THE FIX ---
                # We are reading the FLAT keys
                app_state["credit_analysis"] = response_json
                app_state["status"] = response_json.get("next_state", "ERROR")
                app_state["chat_log"].append(f"Credit Agent: {response_json.get('reasoning', 'No reasoning provided.')}")
                
                if app_state["status"] == "AWAITING_REVIEW (HITL)":
                    app_state["reason_for_review"] = response_json.get("hitl_reason", "Credit agent flagged for review.")
                    app_state["trigger_step"] = "CREDIT_ANALYSIS" # <-- Store the trigger
                # --- END OF FIX ---

        # --- STEP 4: PRODUCT_RECOMMENDATION -> Run Product Agent (FIXED) ---
        elif current_status == "PRODUCT_RECOMMENDATION":
            with st.spinner("Product Agent is recommending products..."):
                product_agent = agents["ProductAgent"]
                credit_score = app_state["credit_analysis"].get("credit_score", 700)
                query = f"Please recommend products for: '{app_state['business_name']}' with credit score {credit_score}"
                response_str = product_agent.run(query).content
                response_json = safe_json_load(response_str)
                
                if "error" in response_json:
                    raise Exception(f"ProductAgent failed: {response_json['error']}")
                
                # --- THIS IS THE FIX ---
                # We are reading the FLAT keys
                app_state["product_recommendation"] = response_json
                app_state["status"] = response_json.get("next_state", "ERROR") # e.g., "APPROVED"
                app_state["chat_log"].append(f"Product Agent: {response_json.get('reasoning', 'No reasoning provided.')}")
                
                if app_state["status"] == "APPROVED":
                    app_state["final_decision"] = "APPROVED (Auto)"
                # --- END OF FIX ---

        # --- STEP 5: APPROVED/REJECTED -> Run Communication Agent (FIXED) ---
        elif current_status in ["APPROVED", "REJECTED"]:
            with st.spinner("Communication Agent is drafting email..."):
                comm_agent = agents["CommunicationAgent"]
                task = "send_approval" if current_status == "APPROVED" else "send_rejection"
                
                if current_status == "REJECTED" and not app_state["final_decision"]:
                    app_state["final_decision"] = "REJECTED (Auto)"

                query = f"""
                Task: '{task}'
                Customer: {{ "name": "{app_state['business_name']}", "email": "customer@example.com" }}
                Products: {app_state["product_recommendation"].get("recommended_products", [])}
                Reason: {app_state.get("final_decision", "N/A")}
                """
                
                # 1. Run the agent to get the JSON
                response_str = comm_agent.run(query).content
                response_json = safe_json_load(response_str)
                
                if "error" in response_json:
                    raise Exception(f"CommunicationAgent failed: {response_json['error']}")
                
                # 2. Call the tool OURSELVES using the agent's JSON
                try:
                    email_body = response_json.get('body', 'No body generated.')
                    email_subject = response_json.get('subject', 'No subject generated.')
                    email_to = response_json.get('to_email', 'customer@example.com')
                    
                    send_customer_communication(
                        to_email=email_to,
                        subject=email_subject,
                        body=email_body
                    )
                    
                    app_state["final_email"] = {
                        "to_email": email_to,
                        "subject": email_subject,
                        "body": email_body
                    }
                    app_state["status"] = "COMPLETED"
                    app_state["chat_log"].append(f"Communication Agent: Email drafted for {task}.")
                    
                except Exception as e:
                    raise Exception(f"CommunicationAgent Tool failed: {str(e)}")
        
        elif current_status in ["COMPLETED", "AWAITING_REVIEW (HITL)"]:
             st.toast("Workflow is paused or complete.")

    # --- THIS CATCHES ALL ERRORS (503, 429, JSON) ---
    except Exception as e:
        st.error(f"An error occurred: {e}")
        app_state["chat_log"].append(f"ERROR: {e}")
        # Reset status to let the user retry the step
        app_state["status"] = current_status 
    
    st.rerun() # Update the UI

# -----------------------------------------------------------------
# --- 7. The Streamlit UI (FIXED) ---
# -----------------------------------------------------------------

app_state = st.session_state.application_state

# --- SIDEBAR: Application Intake ---
with st.sidebar:
    st.header("Application Intake")
    
    input_method = st.radio(
        "Select Input Method",
        ["Upload PDF", "Enter Manually"],
        horizontal=True
    )
    
    if input_method == "Enter Manually":
        with st.form("manual_form"):
            st.subheader("Section 1: Business Information")
            form_business_name = st.text_input("Legal Business Name*")
            form_dba = st.text_input("Doing Business As (DBA) (Optional)")
            form_industry = st.text_input("Industry*")
            form_address = st.text_area("Business Address (Optional)")

            st.subheader("Section 2: Principal Owner")
            form_owner_name = st.text_input("Full Name*")
            form_owner_title = st.text_input("Title (Optional)")
            form_owner_email = st.text_input("Email*")
            
            st.subheader("Section 3: Financial Summary")
            st.caption("Enter data for the last fiscal year.")
            form_revenue = st.number_input("Annual Revenue", min_value=0, value=0)
            form_net_income = st.number_input("Net Income", min_value=-10000000, value=0)
            form_total_debt = st.number_input("Total Business Debt", min_value=0, value=0)
            form_total_assets = st.number_input("Total Business Assets", min_value=0, value=0)
            
            st.subheader("Section 4: Attestation")
            form_signed_for_name = st.text_input("Signed For (Company Name)*")
            form_attestation_check = st.checkbox("I certify that all information provided is true and accurate.*")
            
            submitted = st.form_submit_button("Start New Application")
            
            if submitted:
                if not all([form_business_name, form_industry, form_owner_name, form_owner_email, form_signed_for_name]):
                    st.error("Please fill in all required fields marked with *.")
                elif not form_attestation_check:
                    st.error("Attestation is required to submit.")
                else:
                    # --- THIS IS THE MANUAL CONSISTENCY CHECK ---
                    is_consistent = (form_business_name.strip().lower() == form_signed_for_name.strip().lower())
                    reasoning = "Data provided via manual form."
                    trigger_step = ""
                    
                    if is_consistent:
                        start_status = "KYC_CHECKS" # Go to KYC
                        reasoning = "Data provided via manual form. Consistency check passed."
                        reason_for_review = ""
                    else:
                        start_status = "AWAITING_REVIEW (HITL)" # Go to HITL
                        reasoning = f"Manual entry inconsistent: Legal Name ('{form_business_name}') does not match Attestation Name ('{form_signed_for_name}')."
                        reason_for_review = reasoning
                        trigger_step = "DOC_VERIFICATION" # Set trigger for HITL
                    # --- END OF FIX ---

                    st.session_state.application_state = {
                        "status": start_status,
                        "business_name": form_business_name,
                        "owner_name": form_owner_name,
                        "file_path": None,
                        "chat_log": [f"New manual application started for {form_business_name}.", reasoning],
                        "document_data": {
                            "extracted_data": {
                                "Legal Business Name": form_business_name,
                                "Doing Business As (DBA)": form_dba,
                                "Industry": form_industry,
                                "Business Address": form_address,
                                "Full Name": form_owner_name,
                                "Title": form_owner_title,
                                "Email": form_owner_email,
                                "Annual Revenue": form_revenue,
                                "Net Income": form_net_income,
                                "Total Business Debt": form_total_debt,
                                "Total Business Assets": form_total_assets,
                                "Signed For (Company)": form_signed_for_name
                            },
                            "validation_summary": [
                                { "check": "Data Consistency", "status": "PASS" if is_consistent else "FAIL", "details": reasoning }
                            ],
                            "state_recommendation": start_status,
                            "reasoning": reasoning
                        },
                        "kyc_report": {},
                        "credit_analysis": {},
                        "product_recommendation": {},
                        "final_decision": "",
                        "reason_for_review": reason_for_review,
                        "trigger_step": trigger_step # Store the trigger
                    }
                    st.success("Application started!")
                    st.rerun()

    else: 
        st.subheader("PDF Upload")
        business_name_input = st.text_input("Business Name")
        uploaded_file = st.file_uploader("Upload Business Documents (PDF)", type=["pdf"])
        
        if st.button("Start New Application", type="primary"):
            if business_name_input and uploaded_file:
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.application_state = {
                    "status": "PENDING", # Start the workflow
                    "business_name": business_name_input,
                    "owner_name": "", 
                    "file_path": file_path,
                    "chat_log": [f"New application started for {business_name_input}."],
                    "document_data": {}, "kyc_report": {}, "credit_analysis": {},
                    "product_recommendation": {}, "final_decision": "", "reason_for_review": "",
                    "trigger_step": "" # Initialize trigger_step
                }
                st.success("Application started! Click 'Run Next Step'.")
                st.rerun()
            else:
                st.error("Please provide a business name and upload a file.")

# --- MAIN PAGE: Dashboard ---
col1, col2 = st.columns([1, 1])
current_status = app_state['status']

# --- Column 1: Workflow Log & Status ---
with col1:
    st.subheader("Workflow Status")
    
    if current_status == "ERROR":
        st.error(f"**Current State: ERROR** (See log)")
    elif current_status == "AWAITING_REVIEW (HITL)":
        st.warning("**Current State: AWAITING HUMAN REVIEW**")
    elif current_status == "COMPLETED":
        st.success("**Current State: COMPLETED**")
    else:
        st.info(f"**Current State:** {current_status}")

    if current_status not in ["NONE", "AWAITING_REVIEW (HITL)", "COMPLETED"]:
        st.button("Run Next Step ➡️", on_click=run_next_step, type="primary")

    st.subheader("Workflow Log")
    log_container = st.container(height=500, border=True)
    for log_entry in app_state["chat_log"]:
        if "ERROR:" in log_entry:
            log_container.error(f"- {log_entry}")
        else:
            log_container.markdown(f"- {log_entry}")

    if current_status == "COMPLETED":
        st.subheader("Final Communication")
        email_data = app_state.get("final_email", {})
        if email_data:
            st.text(f"To: {email_data.get('to_email')}")
            st.text(f"Subject: {email_data.get('subject')}")
            st.text_area("Body", value=email_data.get('body', ''), height=200)

# --- Column 2: HITL Dashboard & Data ---
with col2:
    if current_status == "AWAITING_REVIEW (HITL)":
        st.subheader("🕵️‍♂️ Human-in-the-Loop Review")
        
        hitl_agent = agents["HumanReviewAgent"]
        full_case_data_str = json.dumps(app_state, default=str)
        summary_query = f"Please summarize this case data: {full_case_data_str}"
        
        with st.spinner("AI is summarizing the case..."):
            try:
                case_summary = hitl_agent.run(summary_query).content
            except Exception as e:
                st.error(f"Error summarizing case: {e}")
                case_summary = "Could not generate AI summary."

        # Render the UI
        human_decision = render_hitl_ui(
            case_summary, 
            app_state
        )
        
        # --- THIS IS THE NEW, SMARTER LOGIC ---
        if human_decision:
            app_state["final_decision"] = f"Human Analyst: {human_decision}"
            app_state["chat_log"].append(f"Human decision: {human_decision}")
            
            # Route to the correct next step
            if human_decision == "CONTINUE_TO_KYC":
                app_state["status"] = "KYC_CHECKS"
            elif human_decision == "CONTINUE_TO_CREDIT":
                app_state["status"] = "CREDIT_ANALYSIS"
            elif human_decision == "FINAL_APPROVE":
                app_state["status"] = "PRODUCT_RECOMMENDATION"
            elif human_decision == "REJECTED":
                app_state["status"] = "REJECTED"
            
            st.success(f"Case updated. Resuming workflow...")
            st.toast("Click 'Run Next Step' to continue.")
            time.sleep(2)
            st.rerun()
    else:
        st.subheader("Application Data")
        st.json(app_state, expanded=False)
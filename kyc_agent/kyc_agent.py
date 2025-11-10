# agent_3_kyc/kyc_agent.py

from agno.agent import Agent
from agno.models.google import Gemini
# --- 1. IMPORT THE REAL TOOL ---
from agno.tools.duckduckgo import DuckDuckGoTools 
# --- 2. IMPORT THE PRO MODEL ---
from config.settings import GEMINI_PRO_MODEL_ID
from utils.prompts import KYC_AGENT_ROLE, KYC_AGENT_INSTRUCTIONS
import time # For the test block

# -----------------------------------------------------------------
# STEP 1: CREATE THE AGENT
# -----------------------------------------------------------------

def create_kyc_agent() -> Agent:
    """
    Factory function to create the REAL KYC/Compliance Agent.
    This version uses the PRO model and real web search tools.
    """
    
    kyc_agent_llm = Gemini(id=GEMINI_PRO_MODEL_ID)
    
    kyc_agent = Agent(
        name="KYCAgent",
        role=KYC_AGENT_ROLE,
        instructions=KYC_AGENT_INSTRUCTIONS,
        model=kyc_agent_llm,
        
        # --- 3. ADD THE TOOL BACK ---
        tools=[DuckDuckGoTools()],
        
        markdown=True
    )
    
    return kyc_agent

# -----------------------------------------------------------------
# STEP 2: TEST THE AGENT
# -----------------------------------------------------------------

if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    print("--- Testing KYC/Compliance Agent (REAL Version) ---")
    kyc_agent = create_kyc_agent()
    
    print("\n--- Running Test 1: Clean Entity ---")
    test_query_clean = """
    Perform KYC/AML checks on the following entity and owner:
    - Business Name: 'Innovate Solutions Inc.'
    - Owner: 'Dr. Alisha Chen'
    """
    kyc_agent.print_response(test_query_clean)
    
    print("\n--- Waiting 30s to avoid rate limit... ---")
    time.sleep(30)

    print("\n--- Running Test 2: High-Risk (Simulated) Entity ---")
    test_query_risk = """
    Perform KYC/AML checks on the following entity:
    - Business Name: 'Global Trade Ventures Ltd.'
    - Owner: 'Mr. Alexey Volkov'
    """
    kyc_agent.print_response(test_query_risk)
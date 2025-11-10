from agno.agent import Agent
from agno.models.google import Gemini
# --- 1. We are using the PRO model ---
from config.settings import DEFAULT_MODEL_ID
from utils.prompts import CREDIT_AGENT_ROLE, CREDIT_AGENT_INSTRUCTIONS
from utils.tools.credit_tools import calculate_financial_ratios
import json # <-- We need json and time for the test block
import time

# -----------------------------------------------------------------
# --- 2. DEFINE THE METADATA ---
# -----------------------------------------------------------------
def create_credit_agent() -> Agent:
    """
    Factory function to create the Credit Analysis Agent.
    """
    
    # --- 2. We are using the PRO model ---
    credit_agent_llm = Gemini(id=DEFAULT_MODEL_ID)
    
    credit_agent = Agent(
        name="CreditAgent",
        role=CREDIT_AGENT_ROLE,
        instructions=CREDIT_AGENT_INSTRUCTIONS,
        model=credit_agent_llm,
        tools=[calculate_financial_ratios],
        markdown=True
    )
    return credit_agent

# -----------------------------------------------------------------
# --- 3. THE TEST BLOCK (REMAINS THE SAME) ---
# -----------------------------------------------------------------
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    print("--- Testing Credit Analysis Agent (Refactored) ---")
    
    credit_agent = create_credit_agent()
    
    # --- Test 1: Good Financials (Should recommend PRODUCT_RECOMMENDATION) ---
    print("\n--- Running Test 1: Good Financials ---")
    good_financials = {
        "revenue": 500000,
        "net_income": 100000,  # High profit (20% margin)
        "total_debt": 50000,   # Low debt
        "total_assets": 300000
    }
    test_query_good = f"""
    Please analyze the financial statements for 'TechSolutions Inc.'
    Data: {json.dumps(good_financials)}
    """
    credit_agent.print_response(test_query_good)
    
    
    # Wait to avoid rate limit
    print("\n--- Waiting to avoid rate limit... ---")
    time.sleep(30) 
    
    
    # --- Test 2: "Gray Zone" Financials (Should recommend AWAITING_REVIEW) ---
    print("\n--- Running Test 2: Gray Zone Financials ---")
    gray_financials = {
        "revenue": 700000,
        "net_income": 35000,   # Low profit (5% margin)
        "total_debt": 450000,  # High debt
        "total_assets": 600000
    }
    test_query_gray = f"""
    Please analyze the financial statements for 'Global Trade Ventures Ltd.'
    Data: {json.dumps(gray_financials)}
    """
    credit_agent.print_response(test_query_gray)
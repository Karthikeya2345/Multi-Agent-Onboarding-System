# agent_5_product/product_agent.py

import json
from agno.agent import Agent
from agno.models.google import Gemini
from config.settings import GEMINI_PRO_MODEL_ID
from utils.prompts import PRODUCT_AGENT_ROLE, PRODUCT_AGENT_INSTRUCTIONS

# --- 1. IMPORT THE LOGIC ---
from utils.tools.product_tools import get_internal_product_database

# -----------------------------------------------------------------
# --- 2. DEFINE THE METADATA ---
# -----------------------------------------------------------------
def create_product_agent() -> Agent:
    """
    Factory function to create the Product Recommendation Agent.
    """
    product_agent_llm = Gemini(id=GEMINI_PRO_MODEL_ID)
    
    product_agent = Agent(
        name="ProductAgent",
        role=PRODUCT_AGENT_ROLE,
        instructions=PRODUCT_AGENT_INSTRUCTIONS,
        model=product_agent_llm,
        tools=[get_internal_product_database], # <-- Pass the imported tool
        markdown=True
    )
    return product_agent

# -----------------------------------------------------------------
# --- 3. THE TEST BLOCK (REMAINS THE SAME) ---
# -----------------------------------------------------------------
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("--- Testing Product Recommendation Agent (Refactored) ---")
    
    product_agent = create_product_agent()
    
    # --- Test 1: A good applicant in the "Tech" industry ---
    print("\n--- Running Test for Tech Company ---")
    test_query = """
    Please recommend products for the following applicant:
    - Business Name: 'TechSolutions Inc.'
    - Industry: 'Tech'
    - Credit Score: 780
    - Credit Limit Approved: $50,000
    - Notes: Applicant is looking for a primary checking account and a credit card.
    """
    product_agent.print_response(test_query)
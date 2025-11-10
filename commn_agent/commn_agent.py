# agent_6_communication/communication_agent.py

import time
from agno.agent import Agent
from agno.models.google import Gemini
from config.settings import DEFAULT_MODEL_ID
from utils.prompts import COMM_AGENT_ROLE, COMM_AGENT_INSTRUCTIONS
# --- 1. IMPORT THE TOOL ---
from utils.tools.communication_tools import send_customer_communication

# -----------------------------------------------------------------
# --- 2. DEFINE THE METADATA ---
# -----------------------------------------------------------------
def create_communication_agent() -> Agent:
    """
    Factory function to create the Communication Agent.
    This agent's ONLY job is to call the 'send_customer_communication' tool.
    """
    comm_agent_llm = Gemini(id=DEFAULT_MODEL_ID)
    
    communication_agent = Agent(
        name="CommunicationAgent",
        role=COMM_AGENT_ROLE,
        instructions=COMM_AGENT_INSTRUCTIONS,
        model=comm_agent_llm,
        
        # --- 2. ADD THE TOOL BACK ---
        tools=[send_customer_communication], 
        
        markdown=True,
        # Force the agent to call the tool
        tool_call_limit=1
    )
    return communication_agent

# -----------------------------------------------------------------
# --- 3. THE TEST BLOCK ---
# -----------------------------------------------------------------
if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    print("--- Testing Communication Agent (Tool Call Version) ---")
    
    comm_agent = create_communication_agent()
    
    test_query_approve = """
    Task: 'send_approval'
    Customer: { "name": "Jane Doe", "email": "jane.doe@techsolutions.com" }
    Products: [ 'Business Growth Checking', 'Business Rewards Visa' ]
    """
    comm_agent.print_response(test_query_approve)
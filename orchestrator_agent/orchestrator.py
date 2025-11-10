import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from agno.agent import Agent
from agno.models.google import Gemini
from config.settings import DEFAULT_MODEL_ID
from utils.prompts import ORCHESTRATOR_ROLE, ORCHESTRATOR_INSTRUCTIONS

def create_orchestrator_agent() -> Agent:
    """
    Factory function to create the Orchestrator Agent.
    This function will be called by our main.py to build the agent.
    """
    
    # Define the LLM
    orchestrator_llm = Gemini(id=DEFAULT_MODEL_ID)
    
    # Create the Agent
    orchestrator_agent = Agent(
        name="OrchestratorAgent",
        role=ORCHESTRATOR_ROLE,         
        instructions=ORCHESTRATOR_INSTRUCTIONS, 
        model=orchestrator_llm,
        
        tools=[],
        markdown=True
    )
    
    return orchestrator_agent

if __name__ == "__main__":
    """
    This allows us to run this file directly to test the agent:
    python agent_1_orchestrator/orchestrator.py
    """
    from dotenv import load_dotenv
    import os

    load_dotenv()
    
    print("--- Testing Orchestrator Agent ---")

    test_agent = create_orchestrator_agent()

    test_query = "New application received for 'TechSolutions Inc.' Current state is 'PENDING'."

    test_agent.print_response(test_query)
    
    # A test query simulating a later step
    test_query_2 = "KYC checks complete. Analyst report is clean. Current state is 'KYC_CHECKS'."
    test_agent.print_response(test_query_2)
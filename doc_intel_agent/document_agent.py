# agent_2_document/document_agent.py

from agno.agent import Agent
from agno.models.google import Gemini
# --- 1. We are using the PRO model ---
from config.settings import GEMINI_PRO_MODEL_ID
from utils.prompts import DOC_AGENT_ROLE, DOC_AGENT_INSTRUCTIONS
from utils.tools.document_tools import read_pdf_file
import os # <-- We need os for the test block

# -----------------------------------------------------------------
# STEP 2: CREATE THE AGENT "METADATA"
# -----------------------------------------------------------------

def create_document_agent() -> Agent:
    """
    Factory function to create the Document Intelligence Agent.
    """
    
    # --- 2. We are using the PRO model ---
    doc_agent_llm = Gemini(id=GEMINI_PRO_MODEL_ID)
    
    document_agent = Agent(
        name="DocumentIntelligenceAgent",
        role=DOC_AGENT_ROLE,
        instructions=DOC_AGENT_INSTRUCTIONS,
        model=doc_agent_llm,
        tools=[read_pdf_file],
        markdown=True
    )
    
    return document_agent

# -----------------------------------------------------------------
# STEP 3: TEST THE AGENT (Improvised)
# -----------------------------------------------------------------

if __name__ == "__main__":
    from dotenv import load_dotenv
    
    load_dotenv()
    print("--- Testing Document Intelligence Agent (PRO Model) ---")
    
    test_pdf_path = os.path.join("temp", "sample_application.pdf")
    
    if not os.path.exists(test_pdf_path):
        print(f"ERROR: Test file not found at {test_pdf_path}")
    else:
        print(f"Found test file: {test_pdf_path}")
        doc_agent = create_document_agent()
        test_query = f"Please analyze the application document at '{test_pdf_path}'."
        doc_agent.print_response(test_query)
# Multi-Agent-Onboarding-System
This agentic AI system automates a bank's small business onboarding process using a team of 7 specialized agents. It manages the entire workflow—from document extraction and KYC checks to credit analysis and final approval—while using a Human-in-the-Loop (HITL) to escalate "gray zone" cases for human review.

# 🏦 TechVenture Bank: Multi-Agent Onboarding System

This project is a multi-agent AI system, built with the **Agno framework** and **Google's Gemini models**, designed to automate the complex small business onboarding process for a bank.

It transforms a slow, expensive, and error-prone manual process into a fast, intelligent, and auditable workflow. The system features a **Human-in-the-Loop (HITL)** capability to ensure that complex "gray zone" cases are escalated to a human analyst for a final decision.

## Key Features

* **Multi-Agent Workflow:** The system uses a team of 7 specialized AI agents, each with a unique role (e.g., Document Analyst, KYC Analyst, Credit Analyst).
* **Human-in-the-Loop (HITL):** Automatically flags ambiguous cases (like document inconsistencies or "gray zone" credit scores) for human review via a built-in Streamlit dashboard.
* **Dynamic Document Processing:** Uses the `gemini-2.5-pro` model to extract and validate data from uploaded PDF applications.
* **Dual Input System:** Allows users to either upload a PDF for AI analysis or enter application data manually via a dynamic form.
* **Live Web Checks:** The KYC Agent (using `gemini-2.5-pro` and `DuckDuckGoTools`) performs real-time web searches for sanctions, PEP, and adverse media.
* **Persistent Memory:** Uses Streamlit's `session_state` to maintain a complete record of each application as it moves through the workflow.
* **Modular & Separated Logic:** A clean project structure that separates agent "metadata" (roles, prompts) from their "logic" (Python tools).

## System Architecture

The application is orchestrated by a team of 7 core agents:

1.  **Orchestrator Agent (Planner):** The "brain" of the operation. It routes tasks to the correct specialist agent based on the application's current state.
2.  **Document Intelligence Agent:** Reads uploaded PDFs, extracts key data (like financial figures and owner names), and validates it for internal consistency (e.g., `Inc.` vs. `LLC`).
3.  **KYC/Compliance Agent:** Performs real-time web searches to check the business and owner against sanctions lists, PEP databases, and adverse media, assigning a final risk score.
4.  **Credit Analysis Agent:** Uses a custom tool to calculate financial ratios (e.g., Profit Margin, Debt-to-Asset Ratio) and analyzes them to generate a credit score and recommendation.
5.  **Product Recommendation Agent:** Matches the approved applicant's profile and credit score against a database of bank products.
6.  **Communication Agent:** Generates the final, personalized approval or rejection email for the customer.
7.  **Human Review Agent:** Activates when an issue is flagged. It generates an AI-powered summary of the case and provides the UI for a human analyst to make the final decision.

## Tech Stack

* **AI Framework:** `agno`
* **UI / Web App:** `streamlit`
* **LLM:** Google Gemini (`gemini-2.5-pro` and `gemini-2.5-flash`)
* **Core Libraries:** `google-genai`, `pypdf` (for PDF reading), `duckduckgo-search` (for web tools), `pandas`

---

## Setup & Installation

Follow these steps to run the project locally.

### 1. Create a Virtual Environment

It is recommended to use a virtual environment.

```bash
# Navigate to the project folder
cd MAO_System

# Create the venv
python -m venv venv

# Activate the venv
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

### 2. Install Dependencies
Install all required Python libraries from the requirements.txt file.

Bash

pip install -r requirements.txt

### 3. Set Up Environment Variables
Create a file named .env in the root of the MAO_System/ folder.

Bash

# In CMD
type nul > .env

# In PowerShell
New-Item -ItemType File .env
Open this .env file and add your Google API key in the following format:

Code snippet

GEMINI_API_KEY="YOUR_API_KEY_HERE"
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
(Note: Both keys should be the same. We provide both to satisfy the library's logger.)

4. Create the temp Folder
The application needs a folder to store temporary PDF uploads.

Bash

mkdir temp

5. Run the Application
Once your venv is active and your .env file is set, run the Streamlit application.

Bash

streamlit run main.py
Your web browser will open automatically to http://localhost:8501.

How to Use the Application
This app uses a manual, step-by-step workflow to prevent hitting the Gemini API's free-tier rate limits.

Start an Application:

In the sidebar, choose "Upload PDF" or "Enter Manually".

Click "Start New Application".

Run the Workflow:

Click the "Run Next Step ➡️" button to run each agent one by one.

IMPORTANT: Wait 5-10 seconds between each click to avoid 429 Too Many Requests (rate limit) errors.

Continue clicking to proceed through all agent steps.

Testing Scenarios
"Happy Path" (Approval):

Use the sample_application_good.pdf file.

OR select "Enter Manually" and enter identical names for "Legal Business Name" and "Signed For (Company Name)".

The workflow will proceed through all steps to COMPLETED.

"HITL Path" (Human Review):

Use the sample_application_error.pdf (the one with the "Inc. vs. LLC" error).

OR select "Enter Manually" and enter mismatched names (e.g., "Innovate Inc." and "Innovate LLC").

The app will immediately set the status to AWAITING_REVIEW (HITL).

The HITL dashboard will appear, allowing you to "Clear Issue & Continue" to the next agent.

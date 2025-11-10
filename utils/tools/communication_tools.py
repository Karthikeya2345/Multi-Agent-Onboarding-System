# utils/tools/communication_tools.py

import json
import time

def send_customer_communication(to_email: str, subject: str, body: str) -> str:
    """
    Simulates sending an email to a customer.
    In a real system, this would integrate with an API like SendGrid, AWS SES, or MSG91.
    
    Args:
        to_email: The customer's email address.
        subject: The subject line of the email.
        body: The content of the email.
        
    Returns:
        A JSON string confirming the message was "sent".
    """
    print("\n--- TOOL CALLED: send_customer_communication ---")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print("Body:")
    print(body)
    print("-------------------------------------------------")
    
    # Simulate success
    result = {
        "status": "success",
        "message_id": f"simulated_id_{int(time.time())}",
        "to_email": to_email
    }
    return json.dumps(result)
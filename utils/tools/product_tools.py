# utils/tools/product_tools.py

import json

def get_internal_product_database() -> str:
    """
    Simulates a call to the bank's internal product database.
    Returns a JSON string of all available business products.
    """
    print("--- Tool: Calling Internal Product Database ---")
    
    # This is our hard-coded "database"
    products = [
        {
            "product_id": "B-CHK-001",
            "name": "Basic Business Checking",
            "type": "Checking Account",
            "monthly_fee": 10,
            "min_credit_score": 0,
            "good_for_industry": ["all"],
            "features": ["100 free transactions", "Online banking"]
        },
        {
            "product_id": "B-CHK-002",
            "name": "Business Growth Checking",
            "type": "Checking Account",
            "monthly_fee": 25,
            "min_credit_score": 680,
            "good_for_industry": ["retail", "services", "tech"],
            "features": ["500 free transactions", "Interest bearing", "Free wire transfers"]
        },
        {
            "product_id": "B-CARD-001",
            "name": "Business Rewards Visa",
            "type": "Credit Card",
            "monthly_fee": 0,
            "min_credit_score": 720,
            "good_for_industry": ["all"],
            "features": ["2% cashback on all purchases", "$10,000 limit"]
        },
        {
            "product_id": "B-LOAN-001",
            "name": "Small Business Term Loan",
            "type": "Loan",
            "monthly_fee": 0,
            "min_credit_score": 700,
            "good_for_industry": ["services", "retail", "manufacturing"],
            "features": ["Fixed rates", "Up to $100,000"]
        }
    ]
    return json.dumps(products)
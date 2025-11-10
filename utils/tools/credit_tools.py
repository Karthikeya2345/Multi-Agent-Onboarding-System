# utils/tools/credit_tools.py

import json

def calculate_financial_ratios(financial_data_json: str) -> str:
    """
    Analyzes a JSON string of financial data to calculate key ratios.
    
    Args:
        financial_data_json: A JSON string containing financial data, e.g.,
        '{"revenue": 500000, "net_income": 80000, "total_debt": 150000, "total_assets": 300000}'
    
    Returns:
        A JSON string with the calculated ratios and a preliminary assessment.
    """
    print(f"--- Tool: Analyzing Financial Data ---")
    try:
        data = json.loads(financial_data_json)
        
        revenue = data.get("revenue", 0)
        net_income = data.get("net_income", 0)
        total_debt = data.get("total_debt", 0)
        total_assets = data.get("total_assets", 0)

        # Calculate ratios
        profit_margin = (net_income / revenue) * 100 if revenue > 0 else 0
        debt_to_asset_ratio = (total_debt / total_assets) * 100 if total_assets > 0 else 0
        
        # A simple score simulation
        preliminary_score = 70  # Start with a base
        if profit_margin > 15:
            preliminary_score += 10
        elif profit_margin < 5:
            preliminary_score -= 10
            
        if debt_to_asset_ratio < 40:
            preliminary_score += 10
        elif debt_to_asset_ratio > 70:
            preliminary_score -= 10

        result = {
            "calculated_ratios": {
                "profit_margin_percent": round(profit_margin, 2),
                "debt_to_asset_ratio_percent": round(debt_to_asset_ratio, 2)
            },
            "preliminary_credit_score": preliminary_score,
            "notes": "Calculations complete. Ready for agent analysis."
        }
        return json.dumps(result)
        
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON format."})
    except Exception as e:
        return json.dumps({"error": f"Error in calculation: {e}"})
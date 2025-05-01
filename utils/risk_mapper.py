import os
import json

def load_risks():
    import json
    with open('risk_mapping.json', 'r') as f:
        risks = json.load(f)
    return risks

def map_risks(non_compliant_settings, risks_data, rules):
    mapped = {}
    for setting in non_compliant_settings:
        mapped[setting] = {
            "cyber_risk": risks_data.get(setting, {}).get("cyber_risk", "Unknown"),
            "impact_estimate_usd": risks_data.get(setting, {}).get("impact_estimate_usd", 0),
            "recommendation": risks_data.get(setting, {}).get("recommendation", "No recommendation available."),
            "legal_risk": risks_data.get(setting, {}).get("legal_risk", {}),
            "severity": rules.get(setting, {}).get("severity", "Medium"),
            "recommendations": risks_data.get(setting, {}).get("recommendations", {})  # 👈 Role-based recommendations
        }
    return mapped



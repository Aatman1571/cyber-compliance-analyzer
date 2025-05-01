import os
import json

def load_rules():
    base_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_path, ".."))
    file_path = os.path.join(project_root, 'compliance_rules.json')
    with open(file_path, 'r') as f:
        return json.load(f)

def check_compliance(user_inputs, rules, selected_framework):
    results = {}
    for setting, value in user_inputs.items():
        if setting in rules and selected_framework in rules[setting]['frameworks']:
            required_value = rules[setting]['required_value']

            # If input is a dictionary (structured input), extract "configured"
            if isinstance(value, dict):
                configured_value = value.get("configured", 0)
            else:
                configured_value = value

            results[setting] = (configured_value >= required_value)
    return results


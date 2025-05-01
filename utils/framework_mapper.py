def get_cross_mappings(rules):
    cross_mappings = {}
    for control, details in rules.items():
        cross_mappings[control] = details.get("reference", {})
    return cross_mappings

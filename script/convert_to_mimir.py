import yaml

# Flag to control whether to include recording rules in the main output
INCLUDE_RECORDING_RULES = False

try:
    with open("rules.yaml", "r") as f:
        # Use safe_load_all to handle multi-document YAML files
        k8s_rules = list(yaml.safe_load_all(f))
except FileNotFoundError:
    print("Error: rules.yaml file not found")
    exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing YAML file: {e}")
    exit(1)

all_groups = []
recording_groups = []
for doc in k8s_rules:
    if not doc:  # Skip empty documents
        print("Warning: Skipping empty YAML document")
        continue

    # Handle single PrometheusRule or list of rules
    items = doc.get("items", []) if doc.get("kind") == "List" else [doc]
    
    for item in items:
        # Ensure the item is a valid PrometheusRule
        if item.get("kind") != "PrometheusRule":
            print(f"Warning: Skipping invalid item with kind: {item.get('kind', 'unknown')}")
            continue

        # Extract namespace from metadata, default to 'observability'
        namespace = item.get("metadata", {}).get("namespace", "observability")
        
        # Extract groups from spec
        spec = item.get("spec", {})
        groups = spec.get("groups", [])
        
        for group in groups:
            if not isinstance(group, dict) or "name" not in group or "rules" not in group:
                print(f"Warning: Skipping invalid group: {group}")
                continue
                
            # Separate alerting and recording rules
            alerting_rules = []
            group_recording_rules = []
            for rule in group.get("rules", []):
                if "record" in rule:
                    print(f"Warning: Found recording rule in group '{group['name']}': {rule.get('record', 'unknown')}")
                    group_recording_rules.append(rule)
                    if INCLUDE_RECORDING_RULES:
                        alerting_rules.append(rule)
                elif "alert" in rule:
                    alerting_rules.append(rule)
                else:
                    print(f"Warning: Skipping invalid rule in group '{group['name']}': neither 'alert' nor 'record' key found - {rule}")
            
            # Add alerting rules to main output if any exist
            if alerting_rules:
                group_entry = {
                    "name": group["name"],
                    "rules": alerting_rules
                }
                if "interval" in group:
                    group_entry["interval"] = group["interval"]
                all_groups.append(group_entry)
                print(f"Info: Included group '{group['name']}' with {len(alerting_rules)} alerting rules")
            else:
                print(f"Warning: Group '{group['name']}' has no valid alerting rules, skipping from main output")
            
            # Store recording rules for separate output
            if group_recording_rules:
                recording_group_entry = {
                    "name": group["name"],
                    "rules": group_recording_rules
                }
                if "interval" in group:
                    recording_group_entry["interval"] = group["interval"]
                recording_groups.append(recording_group_entry)

# Write alerting rules to main output
if all_groups:
    output = {
        "namespace": "observability",
        "groups": all_groups
    }
    try:
        with open("mimirtool-rules.yaml", "w") as out:
            yaml.dump(output, out, sort_keys=False, default_flow_style=False)
        print("Successfully converted alerting rules to mimirtool-rules.yaml")
    except Exception as e:
        print(f"Error writing alerting rules file: {e}")
        exit(1)
else:
    print("Warning: No valid alerting rule groups found to convert")

# Write recording rules to separate file
if recording_groups:
    recording_output = {
        "namespace": "observability",
        "groups": recording_groups
    }
    try:
        with open("recording-rules.yaml", "w") as out:
            yaml.dump(recording_output, out, sort_keys=False, default_flow_style=False)
        print("Successfully saved recording rules to recording-rules.yaml")
    except Exception as e:
        print(f"Error writing recording rules file: {e}")
else:
    print("No recording rules found to save")

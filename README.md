#  Prometheus to Grafana Alerting Migration (Grafana v12+)

This project guides you through migrating existing Kubernetes `PrometheusRule` resources into **Grafana v12+ Unified Alerting**, using [`mimirtool`](https://grafana.com/docs/mimir/latest/operators-guide/mimirtool/).  
It provides tools and examples for converting rule formats, importing into Grafana, and managing them programmatically.

---

## Prerequisites

Ensure you have the following tools and setup in place:

- Python 3
- PyYAML Python package  
  Install with pip:
  ```bash
  pip install pyyaml
  ```
- [mimirtool](https://grafana.com/docs/mimir/latest/operators-guide/mimirtool/)
- `kubectl` access to your Kubernetes cluster
- Grafana v12 or newer with unified alerting enabled
- Grafana API Key with `Alerting:Write` permissions

---

##  Project Structure

```
prometheus-grafana-alert-migration/
├── README.md
├── scripts/
│   └── convert_to_mimir.py
├── rules/
│   ├── rules.yaml
│   └── mimirtool-rules.yaml
├── docs/
│   ├── migration-guide.md
│   └── troubleshooting.md
├── .gitignore
```

---

##  Step-by-Step Migration Guide

###  Step 1: Export PrometheusRule Resources

Export all PrometheusRule resources from your namespace (e.g. `observability`) into a file:

```bash
kubectl get prometheusrules -n observability -o yaml > rules/rules.yaml
```

---

###  Step 2: Convert to `mimirtool` Format

Create the script at `scripts/convert_to_mimir.py`:

```python
import yaml

with open("rules/rules.yaml") as f:
    k8s_rules = yaml.safe_load(f)

all_groups = []
items = k8s_rules.get("items", [])
if not items and k8s_rules.get("kind") == "PrometheusRule":
    items = [k8s_rules]

for item in items:
    spec = item.get("spec", {})
    groups = spec.get("groups", [])
    for group in groups:
        group_entry = {
            "name": group["name"],
            "rules": group["rules"]
        }
        if "interval" in group:
            group_entry["interval"] = group["interval"]
        all_groups.append(group_entry)

output = {
    "namespace": "observability",
    "groups": all_groups
}

with open("rules/mimirtool-rules.yaml", "w") as out:
    yaml.dump(output, out, sort_keys=False, default_flow_style=False)
```

Run the script:

```bash
python3 scripts/convert_to_mimir.py
```

This generates `rules/mimirtool-rules.yaml`.

---

###  Step 3: Enable Grafana Feature Flags

To use recording rules and the alerting migration UI, enable these flags.

**If using Helm**, add this to your `values.yaml`:

```yaml
grafana.ini:
  unified_alerting:
    enabled: true
  feature_toggles:
    enable: |
      alertingMigrationUI
      grafanaManagedRecordingRulesDatasources
```

Upgrade your Grafana deployment:

```bash
helm upgrade --install grafana grafana/grafana -f values.yaml
```

---

###  Step 4: Import Rules Using `mimirtool`

1. **Get the UID** of your Prometheus data source from Grafana:  
   Go to: `Configuration > Data Sources > Prometheus > UID`

2. **Create an API Key** with `Alerting:Write` permission:  
   Go to: `Administration > API Keys > Create Key`

3. **Import rules**:

```bash
mimirtool rules load rules/mimirtool-rules.yaml   --address https://<your-grafana>/api/convert/   --id 1   --extra-headers "Authorization=Bearer <YOUR_GRAFANA_API_KEY>"   --extra-headers "X-Grafana-Alerting-Datasource-UID=<PROMETHEUS_UID>"
```

Replace:

- `<your-grafana>` → Your Grafana domain or IP
- `<YOUR_GRAFANA_API_KEY>` → The API key you created
- `<PROMETHEUS_UID>` → The UID of your Prometheus data source

---

###  Step 5: Manage Rules via `mimirtool`

####  List all rule groups:

```bash
mimirtool rules list   --address https://<your-grafana>/api/convert/   --id 1   --extra-headers "Authorization=Bearer <YOUR_GRAFANA_API_KEY>"
```

####  Export all rules:

```bash
mimirtool rules print --output-dir=rules
```

####  Get a specific rule group:

```bash
mimirtool rules get observability <group_name> --output-dir=rules
```

####  Delete a rule group:

```bash
mimirtool rules delete observability <group_name>
```

####  Compare local rules to remote rules:

```bash
mimirtool rules diff rules/mimirtool-rules.yaml
```

####  Sync (force remote rules to match local rules):

```bash
mimirtool rules sync rules/mimirtool-rules.yaml
```

---

##  Troubleshooting

| Issue                                     | Solution                                                                 |
|------------------------------------------|--------------------------------------------------------------------------|
| Cannot import recording rules            | Ensure `grafanaManagedRecordingRulesDatasources` is enabled              |
| Repeated namespace attempted to be loaded| Ensure all rule groups use the same top-level `namespace`               |
| Not all rules appear after import        | Ensure the conversion script includes all `groups` and `rules`          |
| 401 or 403 errors during import          | Verify API key permissions and Grafana URL                              |

---

## 🔗 References

- 📘 [Grafana Alerting Documentation](https://grafana.com/docs/grafana/latest/alerting/)
- 📙 [Alerting Migration Guide](https://grafana.com/docs/grafana/latest/alerting/alerting-rules/alerting-migration/)
- 🛠️ [mimirtool CLI Docs](https://grafana.com/docs/mimir/latest/operators-guide/mimirtool/)

# 🛡️ Cyber-Compliance Risk Analyzer

A Streamlit-powered tool for assessing cybersecurity compliance across frameworks like GDPR, HIPAA, PCI-DSS, and SOC 2. It identifies risks, estimates financial impact, recommends actions, and generates professional reports.

## 🚀 Features

- Framework-based compliance checks
- Risk scoring and heatmap visualization
- Role-based recommendations (Legal, IT, Compliance)
- PDF report generation with charts and legend
- Control effectiveness scoring
- Dynamic treatment planning

## 📂 Project Structure

```
cyber-compliance-risk-analyzer/
├── app.py                      # Main Streamlit app
├── requirements.txt            # All required Python packages
├── README.md                   # Project description and usage
├── .gitignore                  # Files to exclude from Git
├── reports/                    # Generated PDF reports (add to .gitignore)
│
├── utils/                      # Modular logic
│   ├── compliance_checker.py
|   ├── framework_mapper.py 
│   ├── risk_mapper.py
│   └── report_generator.py
```

## 🧪 How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📘 Example Output

See the `reports/` directory for example PDF outputs.

## 🛡️ Supported Frameworks

- GDPR
- HIPAA
- PCI-DSS
- SOC 2

---

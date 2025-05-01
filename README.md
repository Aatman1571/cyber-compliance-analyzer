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
![Screenshot 2025-05-01 100314](https://github.com/user-attachments/assets/2b009939-a637-4238-a8ea-c246581c233d)
![Screenshot 2025-05-01 100335](https://github.com/user-attachments/assets/3b87d611-62e8-49ba-84d7-92a650806b4c)
![Screenshot 2025-05-01 102852](https://github.com/user-attachments/assets/b1cd7a25-137e-401a-a6c5-6dec89062a77)
![Screenshot 2025-05-01 102939](https://github.com/user-attachments/assets/19c8b9f8-f131-4a2b-b339-24944610d8dd)
![Screenshot 2025-05-01 102958](https://github.com/user-attachments/assets/c9504bca-74d1-4186-a74e-be03084ff3f2)


import streamlit as st
import matplotlib.pyplot as plt
from utils.compliance_checker import load_rules, check_compliance
from utils.risk_mapper import load_risks, map_risks
from utils.report_generator import generate_pdf
import os

# Setup page
st.set_page_config(page_title="Cyber-Compliance Risk Analyzer", layout="centered", page_icon="🛡️")

# Initialize session state
if "page_step" not in st.session_state:
    st.session_state.page_step = 1
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {}
if "compliance_results" not in st.session_state:
    st.session_state.compliance_results = {}
if "risk_assessment" not in st.session_state:
    st.session_state.risk_assessment = {}
if "framework_selected" not in st.session_state:
    st.session_state.framework_selected = ""
if "risk_score" not in st.session_state:
    st.session_state.risk_score = 0
if "maturity_percentage" not in st.session_state:
    st.session_state.maturity_percentage = 0
if "chart_path" not in st.session_state:
    st.session_state.chart_path = ""

# Sidebar
st.sidebar.title("⚙️ Framework Selection")
framework_options = ["GDPR", "HIPAA", "PCI-DSS", "SOC 2"]
selected_framework = st.sidebar.selectbox("Choose Compliance Framework", framework_options)

# Load rules and risks
rules = load_rules()
risks_data = load_risks()

# Enhance risk data with default role-based recommendations
default_roles = ["Legal", "IT", "Compliance"]
for setting, info in risks_data.items():
    if "recommendations" not in info:
        info["recommendations"] = {}
    for role in default_roles:
        if role not in info["recommendations"]:
            base = info.get("recommendation", "Review this control for compliance.")
            if role == "Legal":
                info["recommendations"][role] = f"Legal team should evaluate if contracts and policies support: {base.lower()}"
            elif role == "IT":
                info["recommendations"][role] = f"IT should implement technical measures to: {base.lower()}"
            elif role == "Compliance":
                info["recommendations"][role] = f"Compliance should update internal documentation to reflect: {base.lower()}"

# Severity Badge Helper
def get_severity_badge(severity):
    if severity == "Critical":
        return "🔴"
    elif severity == "High":
        return "🟠"
    elif severity == "Medium":
        return "🟡"
    elif severity == "Low":
        return "🟢"
    else:
        return "⚪"

# Step 1: System Inputs
if st.session_state.page_step == 1:
    st.title("🛡️ Cyber-Compliance Risk Analyzer")
    st.markdown(f"### 📥 Step 1: System Configuration for {selected_framework}")

    applicable_controls = {k: v for k, v in rules.items() if selected_framework in v["frameworks"]}
    control_groups = {}
    for setting, details in applicable_controls.items():
        group = details.get("control_group", "Other")
        control_groups.setdefault(group, []).append((setting, details))

    dynamic_inputs = {}

    for group, controls in control_groups.items():
        st.subheader(f"🛡️ {group}")

        for setting, details in controls:
            badge = get_severity_badge(details.get("severity", ""))
            st.markdown(f"{badge} **{setting.replace('_', ' ').title()}** [{details.get('severity', '')}]", unsafe_allow_html=True)

            references = details.get('reference', {})
            if references:
                ref_string = ", ".join([f"{fw}: {ref}" for fw, ref in references.items()])
                st.markdown(f"📖 References: {ref_string}", unsafe_allow_html=True)

            st.markdown(f"📋 {details.get('description', '')}", unsafe_allow_html=True)

            if isinstance(details["required_value"], int) and details["required_value"] > 1:
                dynamic_inputs[setting] = st.number_input(
                    f"Enter value for {setting.replace('_', ' ').title()}",
                    min_value=0,
                    value=details["required_value"],
                    key=f"{setting}_value"
                )
            else:
                configured_option = st.selectbox(
                    f"Is {setting.replace('_', ' ').title()} configured?",
                    ("No", "Yes"),
                    key=f"{setting}_configured"
                )
                configured = 1 if configured_option == "Yes" else 0

                effectiveness = st.selectbox(
                    f"Control Effectiveness for {setting.replace('_', ' ').title()}",
                    ["Not Implemented", "Partially Implemented", "Fully Implemented"],
                    disabled=(configured_option == "No"),
                    key=f"{setting}_effectiveness"
                )

                dynamic_inputs[setting] = {
                    "configured": configured,
                    "effectiveness": effectiveness
                }

            st.markdown("---")

    if st.button("✅ Analyze Compliance"):
        with st.spinner('Analyzing your system...'):
            st.session_state.user_inputs = dynamic_inputs
            st.session_state.compliance_results = check_compliance(dynamic_inputs, rules, selected_framework)
            st.session_state.framework_selected = selected_framework
            st.session_state.page_step = 2


    #if submitted:
    #    with st.spinner('Analyzing your system...'):
     #       st.session_state.user_inputs = dynamic_inputs
      #      st.session_state.compliance_results = check_compliance(dynamic_inputs, rules, selected_framework)
       #     st.session_state.framework_selected = selected_framework
        #    st.session_state.page_step = 2

# Step 2: Compliance Results
if st.session_state.page_step == 2:
    st.title("🛡️ Cyber-Compliance Risk Analyzer")
    st.markdown("### 📊 Step 2: Compliance Results Overview")

    compliant_count = sum(1 for v in st.session_state.compliance_results.values() if v)
    non_compliant_count = sum(1 for v in st.session_state.compliance_results.values() if not v)
    total_controls = len(st.session_state.compliance_results)
    failed_controls = non_compliant_count

    risk_score = max(0, 100 - int((failed_controls / total_controls) * 100))
    maturity_percentage = int((total_controls - failed_controls) / total_controls * 100)

    st.session_state.risk_score = risk_score
    st.session_state.maturity_percentage = maturity_percentage

    st.subheader("Compliance Status")
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie([compliant_count, non_compliant_count], labels=['Compliant', 'Non-Compliant'],
           autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#FF6F61'])
    ax.axis('equal')
    st.pyplot(fig)

    if not os.path.exists('reports'):
        os.makedirs('reports')
    chart_path = 'reports/compliance_chart.png'
    fig.savefig(chart_path, bbox_inches='tight')
    st.session_state.chart_path = chart_path

    st.subheader("🎯 Overall Risk Score")
    st.progress(risk_score)
    if risk_score >= 80:
        st.success(f"🟢 Healthy Risk Score: {risk_score}/100")
    elif risk_score >= 50:
        st.warning(f"🟠 Medium Risk Score: {risk_score}/100")
    else:
        st.error(f"🔴 Critical Risk Score: {risk_score}/100")

    st.subheader("🔍 Framework Maturity Level")
    st.write(f"Your {selected_framework} compliance maturity is **{maturity_percentage}%**")
    st.progress(maturity_percentage)

    if st.button("➡️ Proceed to Risk Treatment Planning"):
        non_compliant_settings = [k for k, v in st.session_state.compliance_results.items() if not v]
        st.session_state.risk_assessment = map_risks(non_compliant_settings, risks_data, rules)
        st.session_state.page_step = 3
# Step 3: Risk Treatments
if st.session_state.page_step == 3:
    st.title("🛡️ Cyber-Compliance Risk Analyzer")
    st.markdown("### 🛠️ Step 3: Risk Treatment Selection")

    severity_weights = {"Critical": 5, "High": 4, "Medium": 3, "Low": 1}
    total_score = 0
    max_score = 0

    # Sort risks by estimated impact
    sorted_risks = sorted(
        st.session_state.risk_assessment.items(),
        key=lambda x: x[1].get('impact_estimate_usd', 0),
        reverse=True
    )

    for setting, details in sorted_risks:
        legal_risk = details.get('legal_risk', {}).get(st.session_state.framework_selected, 'Not Applicable')
        st.markdown(f"""
        <div style=\"background-color: #fff3cd; padding: 10px; border-radius: 10px;\">
        <b>{setting.replace('_', ' ').title()}</b><br/>
        - Cyber Risk: {details['cyber_risk']}<br/>
        - Estimated Impact ($): {details.get('impact_estimate_usd', 'N/A')}<br/>
        - Legal Exposure: {legal_risk}<br/>
        - Recommendation: {details.get('recommendation', '')}<br/>" +
        "{''.join([f'- {role} Recommendation: {text}<br/>' for role, text in details.get('recommendations', {}).items()]) if 'recommendations' in details else ''}
        </div><br/>
        """, unsafe_allow_html=True)

        treatment_key = f"treatment_{setting}"
        st.session_state.risk_assessment[setting]['treatment'] = st.selectbox(
            f"Select Treatment for {setting.replace('_', ' ').title()}",
            ["Accept", "Transfer", "Mitigate", "Avoid"],
            key=treatment_key
        )

        severity = details.get("severity", "Medium")
        impact = details.get("impact_estimate_usd", 10000)
        effectiveness = st.session_state.user_inputs.get(setting, {}).get("effectiveness", "Not Implemented")
        effectiveness_multiplier = 1.0 if effectiveness == "Fully Implemented" else 0.5 if effectiveness == "Partially Implemented" else 0
        treatment = st.session_state.risk_assessment[setting]['treatment']
        weight = severity_weights.get(severity, 3)
        likelihood = 0.3 + (weight * 0.1)
        multiplier = 1 if treatment == "Accept" else 0.8 if treatment == "Transfer" else 0.5 if treatment == "Mitigate" else 0
        risk_value = weight * likelihood * multiplier * effectiveness_multiplier * (impact / 10000)

        total_score += risk_value
        max_score += weight * 1.0 * (impact / 10000)

    st.session_state.risk_score = max(0, 100 - int((total_score / max_score) * 100)) if max_score else 100

    st.subheader("🛠️ Auto-Generated Action Plan")
    action_plan_items = []
    for setting, details in st.session_state.risk_assessment.items():
        if details.get('treatment') in ["Mitigate", "Avoid"]:
            action_plan_items.append({
                "Risk": setting.replace('_', ' ').title(),
                "Description": details.get('recommendation', ''),
                "Impact ($)": details.get('impact_estimate_usd', 0),
                "Treatment": details.get('treatment')
            })

    if action_plan_items:
        action_plan_items.sort(key=lambda x: x["Impact ($)"], reverse=True)
        for idx, item in enumerate(action_plan_items, 1):
            st.markdown(f"""
            <div style=\"background-color: #e6f7ff; padding: 10px; border-radius: 10px;\">
            <b>{idx}. {item['Risk']}</b><br/>
            - 📄 Description: {item['Description']}<br/>
            - 💵 Impact: ${item['Impact ($)']}<br/>
            - 🛡️ Action: {item['Treatment']}
            </div><br/>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 No high-priority mitigation needed!")


    st.subheader("📈 Risk Heatmap")
    heatmap_data = []
    for setting, details in st.session_state.risk_assessment.items():
        severity = details.get("severity", "Medium")
        impact = details.get("impact_estimate_usd", 0)
        treatment = details.get("treatment", "Accept")

        base_likelihood = severity_weights.get(severity, 3) * 10
        if treatment == "Accept":
            base_likelihood += 10
        elif treatment == "Mitigate":
            base_likelihood -= 5
        elif treatment == "Avoid":
            base_likelihood -= 10
        elif treatment == "Transfer":
            base_likelihood -= 3

        likelihood = min(max(base_likelihood, 0), 100)

        heatmap_data.append({
            "name": setting.replace("_", " ").title(),
            "impact": impact,
            "likelihood": likelihood
        })

    fig, ax = plt.subplots(figsize=(3, 3))
    for risk in heatmap_data:
        color = 'green'
        if risk["impact"] > 50000 and risk["likelihood"] > 70:
            color = 'red'
        elif risk["impact"] > 20000 and risk["likelihood"] > 50:
            color = 'orange'
        elif risk["impact"] > 10000:
            color = 'yellow'

        ax.scatter(risk["likelihood"], risk["impact"], color=color, s=100, label=risk["name"])

    ax.set_xlabel("Likelihood (%)")
    ax.set_ylabel("Impact ($)")
    ax.set_title("Risk Heatmap")
    ax.grid(True)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize="small", bbox_to_anchor=(1.05, 1), loc='upper left')


    st.pyplot(fig)

    st.markdown("""
    **Legend:**
    - 🔴 Red: High Impact & High Likelihood
    - 🟠 Orange: Medium Impact & Likelihood
    - 🟡 Yellow: Moderate Risk
    - 🟢 Green: Low Risk
    """)

    if st.button("📄 Export Full Risk Report (PDF)"):
        filename = generate_pdf({
            "compliance_results": st.session_state.compliance_results,
            "risk_mapping": st.session_state.risk_assessment,
            "framework": st.session_state.framework_selected,
            "chart_path": st.session_state.chart_path,
            "risk_score": st.session_state.risk_score,
            "maturity_percentage": st.session_state.maturity_percentage,
            "heatmap_data": heatmap_data  # NEW: pass heatmap data to PDF
        })
        st.balloons()
        st.success(f"✅ PDF Report saved at: {filename}")


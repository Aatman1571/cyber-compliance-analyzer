from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import matplotlib.pyplot as plt
import tempfile
import os

def generate_pdf(data):
    filename = f"reports/Compliance_Report_{data['framework']}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SmallHeading', fontSize=12, leading=14, spaceAfter=10))
    styles.add(ParagraphStyle(name='SmallText', fontSize=12, leading=14))
    styles.add(ParagraphStyle(name='Normal12', fontSize=12, leading=16))

    elements.append(Paragraph(f"<b>Cyber-Compliance Risk Report - {data['framework']}</b>", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    # Recompute risk score from risk_mapping
    severity_weights = {"Critical": 5, "High": 4, "Medium": 3, "Low": 1}
    total_score = 0
    max_score = 0
    for setting, details in data["risk_mapping"].items():
        severity = details.get("severity", "Medium")
        impact = details.get("impact_estimate_usd", 10000)
        treatment = details.get("treatment", "Accept")
        weight = severity_weights.get(severity, 3)
        likelihood = 0.3 + (weight * 0.1)
        multiplier = 1 if treatment == "Accept" else 0.8 if treatment == "Transfer" else 0.5 if treatment == "Mitigate" else 0
        risk_value = weight * likelihood * multiplier * (impact / 10000)
        total_score += risk_value
        max_score += weight * 1.0 * (impact / 10000)

    final_risk_score = max(0, 100 - int((total_score / max_score) * 100)) if max_score else 100

    elements.append(Paragraph(f"<b>Overall Risk Score:</b> {final_risk_score}/100", styles['Normal12']))
    elements.append(Paragraph(f"<b>Framework Maturity:</b> {data['maturity_percentage']}%", styles['Normal12']))
    elements.append(Spacer(1, 0.2 * inch))

    # Pie chart
    if os.path.exists(data['chart_path']):
        elements.append(Paragraph("<b>Compliance Chart</b>", styles['Heading3']))
        elements.append(Image(data['chart_path'], width=3.5 * inch, height=3.5 * inch))
        elements.append(Spacer(1, 0.2 * inch))

    # Heatmap + Legend
    if 'heatmap_data' in data:
        fig, ax = plt.subplots(figsize=(3.5, 3.5))
        for risk in data['heatmap_data']:
            color = 'green'
            if risk["impact"] > 50000 and risk["likelihood"] > 70:
                color = 'red'
            elif risk["impact"] > 20000 and risk["likelihood"] > 50:
                color = 'orange'
            elif risk["impact"] > 10000:
                color = 'yellow'
            ax.scatter(risk["likelihood"], risk["impact"], color=color, s=40)
        ax.set_xlabel("Likelihood (%)")
        ax.set_ylabel("Impact ($)")
        ax.set_title("Risk Heatmap")
        ax.grid(True)

        heatmap_path = os.path.join(tempfile.gettempdir(), "heatmap.png")
        fig.savefig(heatmap_path, bbox_inches='tight')
        plt.close(fig)

        legend_fig, legend_ax = plt.subplots(figsize=(3.5, len(data['heatmap_data']) * 0.25))
        legend_ax.axis('off')
        for i, risk in enumerate(data['heatmap_data']):
            label = risk['name']
            impact = risk["impact"]
            likelihood = risk["likelihood"]
            color = 'green'
            if impact > 50000 and likelihood > 70:
                color = 'red'
            elif impact > 20000 and likelihood > 50:
                color = 'orange'
            elif impact > 10000:
                color = 'yellow'
            legend_ax.scatter(0, i, color=color, s=100)
            legend_ax.text(0.2, i, label, va='center', fontsize=10)

        legend_ax.set_xlim(-0.1, 4)
        legend_ax.set_ylim(-1, len(data['heatmap_data']))
        legend_path = os.path.join(tempfile.gettempdir(), "legend.png")
        legend_fig.savefig(legend_path, bbox_inches='tight')
        plt.close(legend_fig)

        heatmap_img = Image(heatmap_path, width=3.5 * inch, height=3.5 * inch)
        legend_img = Image(legend_path, width=3.5 * inch, height=len(data['heatmap_data']) * 0.25 * inch)
        table = Table([[heatmap_img, legend_img]], colWidths=[3.5 * inch, 3.5 * inch])
        table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))

        elements.append(Paragraph("<b>Risk Heatmap</b>", styles['Heading3']))
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))

    # Compliance check
    elements.append(Paragraph("<b>Compliance Check Results</b>", styles['Heading3']))
    for setting, compliant in data["compliance_results"].items():
        status = "Compliant" if compliant else "Non-Compliant"
        elements.append(Paragraph(f"• {setting.replace('_', ' ').title()}: {status}", styles['SmallText']))
    elements.append(Spacer(1, 0.3 * inch))

    # Score breakdown table (no effectiveness column)
    elements.append(Paragraph("<b>Risk Score Breakdown by Control</b>", styles['Heading3']))
    score_data = [["Control", "Risk Score", "Severity", "Treatment"]]
    severity_weights = {"Critical": 5, "High": 4, "Medium": 3, "Low": 1}
    for setting, details in data["risk_mapping"].items():
        name = setting.replace("_", " ").title()
        severity = details.get("severity", "Medium")
        impact = details.get("impact_estimate_usd", 10000)
        treatment = details.get("treatment", "Accept")
        weight = severity_weights.get(severity, 3)
        likelihood = 0.3 + (weight * 0.1)
        treat_mult = 1 if treatment == "Accept" else 0.8 if treatment == "Transfer" else 0.5 if treatment == "Mitigate" else 0
        risk_value = weight * likelihood * treat_mult * (impact / 10000)
        score_data.append([name, round(risk_value, 2), severity, treatment])
    score_table = Table(score_data, repeatRows=1)
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(1,1),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Risk mapping details (excluding effectiveness)
    elements.append(Paragraph("<b>Risk Mapping Details</b>", styles['Heading3']))
    for setting, details in data["risk_mapping"].items():
        elements.append(Paragraph(f"<b>{setting.replace('_', ' ').title()}</b>", styles['SmallHeading']))
        elements.append(Paragraph(f"Cyber Risk: {details.get('cyber_risk', 'N/A')}", styles['SmallText']))
        legal = details.get('legal_risk', {}).get(data['framework'], 'N/A')
        elements.append(Paragraph(f"Legal Risk: {legal}", styles['SmallText']))
        elements.append(Paragraph(f"Impact ($): {details.get('impact_estimate_usd', 'N/A')}", styles['SmallText']))
        elements.append(Paragraph(f"Risk Treatment: {details.get('treatment', 'N/A')}", styles['SmallText']))

        if 'recommendations' in details:
            for role, rec in details['recommendations'].items():
                elements.append(Paragraph(f"{role} Recommendation: {rec}", styles['SmallText']))
        else:
            elements.append(Paragraph(f"Recommendation: {details.get('recommendation', 'N/A')}", styles['SmallText']))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return filename

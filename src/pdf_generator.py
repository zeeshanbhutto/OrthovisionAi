from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as ReportImage,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_ai_report(
    output_path,
    patient_id,
    body_region,
    model_name,
    prediction,
    confidence,
    risk_level,
    original_image_path=None,
    gradcam_image_path=None,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "OrthoTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "OrthoHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#0F766E"),
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "OrthoNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
    )

    story = []

    story.append(Paragraph("OrthoVision AI", title_style))
    story.append(Paragraph("AI-Assisted Bone Fracture Screening Report", heading_style))
    story.append(Spacer(1, 12))

    report_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    summary_data = [
        ["Patient / Image ID", patient_id],
        ["Body Region", body_region],
        ["Model Used", model_name],
        ["Prediction", prediction.upper()],
        ["Confidence Score", f"{confidence:.2f}%"],
        ["Risk Level", risk_level],
        ["Report Generated On", report_time],
    ]

    table = Table(summary_data, colWidths=[2.2 * inch, 3.8 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E0F2FE")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("AI Interpretation", heading_style))

    if prediction.lower() == "fractured":
        interpretation = (
            "The AI model has detected signs that may indicate a bone fracture. "
            "The Grad-CAM visualization highlights the regions that contributed most "
            "to the model prediction. This result should be reviewed by a qualified "
            "medical professional."
        )
    else:
        interpretation = (
            "The AI model did not detect clear signs of fracture in the uploaded X-ray. "
            "However, this result should still be verified by a qualified medical professional."
        )

    story.append(Paragraph(interpretation, normal_style))
    story.append(Spacer(1, 16))

    image_table_data = []

    if original_image_path and Path(original_image_path).exists():
        img = ReportImage(str(original_image_path), width=2.4 * inch, height=2.4 * inch)
        image_table_data.append([Paragraph("<b>Original X-ray</b>", normal_style), img])

    if gradcam_image_path and Path(gradcam_image_path).exists():
        img = ReportImage(str(gradcam_image_path), width=2.4 * inch, height=2.4 * inch)
        image_table_data.append([Paragraph("<b>Grad-CAM Overlay</b>", normal_style), img])

    if image_table_data:
        story.append(Paragraph("Visual Evidence", heading_style))

        image_table = Table(image_table_data, colWidths=[2.0 * inch, 3.5 * inch])
        image_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        story.append(image_table)
        story.append(Spacer(1, 16))

    story.append(Paragraph("Medical Disclaimer", heading_style))
    story.append(Paragraph(
        "This report is generated for educational and research purposes only. "
        "It is not a replacement for clinical diagnosis, medical advice, or radiologist interpretation. "
        "Final diagnosis must be made by a certified healthcare professional.",
        normal_style,
    ))

    doc.build(story)

    return str(output_path)
from pathlib import Path
from datetime import datetime
import tempfile

import qrcode
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
    doctor_feedback=None,
    doctor_notes=None,
    doctor_name=None,
    doctor_specialization=None,
    doctor_shift=None,
    doctor_review_time=None,
    report_id=None,
    qr_payload=None,
):
    """
    Generate an AI-assisted fracture screening PDF report.

    QR Code:
    - If qr_payload is provided, that text/URL will be encoded.
    - If qr_payload is not provided, a report summary will be encoded automatically.

    Doctor Review:
    - doctor_name stores the reviewing doctor / supervisor name.
    - doctor_specialization stores the specialty such as Radiologist or Orthopedic Specialist.
    - doctor_shift stores Morning / Evening / Night / On Call.
    - doctor_review_time stores the exact review timestamp.
    - doctor_feedback can be Agree / Disagree / Needs Review / Not reviewed.
    - doctor_notes can contain supervisor/doctor notes.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    if report_id is None:
        report_id = f"ORT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        confidence_value = float(confidence)
    except (TypeError, ValueError):
        confidence_value = 0.0

    if qr_payload is None:
        qr_payload = (
            f"OrthoVision AI Report\n"
            f"Report ID: {report_id}\n"
            f"Patient/Image ID: {patient_id}\n"
            f"Body Region: {body_region}\n"
            f"Model Used: {model_name}\n"
            f"Prediction: {prediction}\n"
            f"Confidence: {confidence_value:.2f}%\n"
            f"Risk Level: {risk_level}\n"
            f"Doctor: {doctor_name or 'Not provided'}\n"
            f"Specialization: {doctor_specialization or 'Not provided'}\n"
            f"Shift: {doctor_shift or 'Not provided'}\n"
            f"Review Time: {doctor_review_time or 'Not provided'}\n"
            f"Doctor Feedback: {doctor_feedback or 'Not reviewed'}\n"
            f"Generated On: {report_time}"
        )

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

    summary_data = [
        ["Report ID", report_id],
        ["Patient / Image ID", patient_id],
        ["Body Region", body_region],
        ["Model Used", model_name],
        ["Prediction", str(prediction).upper()],
        ["Confidence Score", f"{confidence_value:.2f}%"],
        ["Risk Level", risk_level],
        ["Report Generated On", report_time],
    ]

    table = Table(summary_data, colWidths=[2.2 * inch, 3.8 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E0F2FE")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("AI Interpretation", heading_style))

    if str(prediction).lower() == "fractured":
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
        original_img = ReportImage(
            str(original_image_path),
            width=2.4 * inch,
            height=2.4 * inch,
        )
        image_table_data.append([Paragraph("<b>Original X-ray</b>", normal_style), original_img])

    if gradcam_image_path and Path(gradcam_image_path).exists():
        gradcam_img = ReportImage(
            str(gradcam_image_path),
            width=2.4 * inch,
            height=2.4 * inch,
        )
        image_table_data.append([Paragraph("<b>Grad-CAM Overlay</b>", normal_style), gradcam_img])

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

    story.append(Paragraph("Doctor Review", heading_style))

    doctor_review_data = [
        ["Doctor Name", doctor_name or "Not provided"],
        ["Specialization", doctor_specialization or "Not provided"],
        ["Shift", doctor_shift or "Not provided"],
        ["Review Time", doctor_review_time or "Not provided"],
        ["Doctor Feedback", doctor_feedback or "Not reviewed"],
        ["Doctor Notes", doctor_notes or "No notes added."],
    ]

    doctor_table = Table(doctor_review_data, colWidths=[2.2 * inch, 3.8 * inch])
    doctor_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0FDF4")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(doctor_table)
    story.append(Spacer(1, 16))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")

    temp_qr_path = Path(tempfile.gettempdir()) / f"{report_id}_qr.png"
    qr_img.save(temp_qr_path)

    story.append(Paragraph("Report Verification QR Code", heading_style))

    qr_table = Table(
        [
            [
                ReportImage(str(temp_qr_path), width=1.5 * inch, height=1.5 * inch),
                Paragraph(
                    "Scan this QR code to view the AI report summary and verification details. "
                    "This QR code is generated for educational and research demonstration purposes.",
                    normal_style,
                ),
            ]
        ],
        colWidths=[1.8 * inch, 4.2 * inch],
    )

    qr_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(qr_table)
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

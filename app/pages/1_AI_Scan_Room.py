from datetime import datetime
from pathlib import Path
import csv
import re
import sys
from urllib.parse import urlencode

import streamlit as st
from PIL import Image

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

from components.ui_styles import apply_custom_style
from src.predict import FracturePredictor
from src.pdf_generator import generate_ai_report


APP_BASE_URL = "https://orthovisionai-7qcmmcpxyudjc4ntut8d3s.streamlit.app"

st.set_page_config(
    page_title="AI Scan Room | OrthoVision AI",
    page_icon="🩻",
    layout="wide",
)

apply_custom_style()


query_params = st.query_params
is_verification_mode = query_params.get("verification") == "true"


def qp(name, default=""):
    value = query_params.get(name, default)

    if isinstance(value, list):
        return value[0] if value else default

    return value if value not in [None, ""] else default


@st.cache_resource
def load_predictor():
    return FracturePredictor()


def clean_filename(value):
    value = value.strip()
    value = re.sub(r"[^a-zA-Z0-9_-]", "_", value)
    return value or "case"


def safe_confidence_value(confidence):
    try:
        return f"{float(confidence):.2f}"
    except (TypeError, ValueError):
        return str(confidence)


def build_report_verification_url(
    report_id,
    patient_id,
    body_region,
    model_name,
    prediction,
    confidence,
    risk_level,
    doctor_name=None,
    doctor_specialization=None,
    doctor_shift=None,
    doctor_review_time=None,
):
    query_string = urlencode({
        "report_id": report_id,
        "patient_id": patient_id,
        "body_region": body_region,
        "model": model_name,
        "prediction": prediction,
        "confidence": safe_confidence_value(confidence),
        "risk": risk_level,
        "doctor_name": doctor_name or "Not provided",
        "doctor_specialization": doctor_specialization or "Not provided",
        "doctor_shift": doctor_shift or "Not provided",
        "doctor_review_time": doctor_review_time or "Not provided",
    })

    # QR opens the main dashboard/root page, where Report Verification is shown.
    return f"{APP_BASE_URL}/?{query_string}"


def save_doctor_feedback(
    report_id,
    patient_id,
    body_region,
    model_name,
    prediction,
    confidence,
    risk_level,
    doctor_feedback,
    doctor_notes,
    doctor_name=None,
    doctor_specialization=None,
    doctor_shift=None,
    doctor_review_time=None,
):
    feedback_dir = APP_DIR / "feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)

    feedback_file = feedback_dir / "doctor_feedback.csv"
    file_exists = feedback_file.exists()

    with open(feedback_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "report_id",
                "patient_id",
                "body_region",
                "model_name",
                "ai_prediction",
                "confidence",
                "risk_level",
                "doctor_name",
                "doctor_specialization",
                "doctor_shift",
                "doctor_review_time",
                "doctor_feedback",
                "doctor_notes",
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            report_id,
            patient_id,
            body_region,
            model_name,
            prediction,
            safe_confidence_value(confidence),
            risk_level,
            doctor_name or "Not provided",
            doctor_specialization or "Not provided",
            doctor_shift or "Not provided",
            doctor_review_time or datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            doctor_feedback,
            doctor_notes,
        ])


def render_report_summary(
    report_id,
    patient_id,
    body_region,
    model_name,
    prediction,
    confidence,
    risk_level,
):
    st.markdown("### Loaded Report Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Prediction", str(prediction).upper())

    with c2:
        st.metric("Confidence", f"{confidence}%")

    with c3:
        st.metric("Risk Level", risk_level)

    st.write("**Report ID:**", report_id)
    st.write("**Patient / Image ID:**", patient_id)
    st.write("**Body Region:**", body_region)
    st.write("**Model:**", model_name)

    st.info(
        "Original X-ray and Grad-CAM are available in the downloaded PDF report. "
        "This online page is for report verification and doctor review feedback."
    )


def render_doctor_review_form(
    report_id,
    patient_id,
    body_region,
    model_name,
    prediction,
    confidence,
    risk_level,
    form_key="doctor_feedback_form",
):
    st.markdown("### 👨‍⚕️ Doctor Review Mode")

    default_doctor_name = qp("doctor_name", st.session_state.get("doctor_name", ""))
    default_specialization = qp(
        "doctor_specialization",
        st.session_state.get("doctor_specialization", "Orthopedic Specialist"),
    )
    default_shift = qp("doctor_shift", st.session_state.get("doctor_shift", "Morning"))

    specializations = [
        "Orthopedic Specialist",
        "Radiologist",
        "Emergency Physician",
        "General Physician",
        "Medical Officer",
        "Supervisor / Examiner",
        "Other",
    ]

    shifts = ["Morning", "Evening", "Night", "On Call"]

    specialization_index = (
        specializations.index(default_specialization)
        if default_specialization in specializations
        else 0
    )

    shift_index = shifts.index(default_shift) if default_shift in shifts else 0

    with st.form(form_key):
        doctor_name = st.text_input(
            "Doctor Name",
            value=default_doctor_name,
            placeholder="Example: Dr. Ahmed Khan",
        )

        doctor_specialization = st.selectbox(
            "Doctor Specialization",
            specializations,
            index=specialization_index,
        )

        doctor_shift = st.selectbox(
            "Shift",
            shifts,
            index=shift_index,
        )

        doctor_review_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        st.info(f"Review Time: {doctor_review_time}")

        selected_feedback = st.radio(
            "Do you agree with the AI prediction?",
            ["Agree", "Disagree", "Needs Review"],
            horizontal=True,
        )

        notes_value = st.text_area(
            "Doctor / Supervisor Notes",
            value=st.session_state.get("doctor_notes", ""),
            placeholder=(
                "Write each note on a new line, for example:\n"
                "Fracture line visible near wrist joint\n"
                "Grad-CAM focus area looks relevant\n"
                "Recommend orthopedic consultation"
            ),
            height=150,
        )

        feedback_submitted = st.form_submit_button("Save Doctor Feedback")

        if feedback_submitted:
            save_doctor_feedback(
                report_id=report_id,
                patient_id=patient_id,
                body_region=body_region,
                model_name=model_name,
                prediction=prediction,
                confidence=confidence,
                risk_level=risk_level,
                doctor_feedback=selected_feedback,
                doctor_notes=notes_value,
                doctor_name=doctor_name,
                doctor_specialization=doctor_specialization,
                doctor_shift=doctor_shift,
                doctor_review_time=doctor_review_time,
            )

            st.session_state["doctor_name"] = doctor_name
            st.session_state["doctor_specialization"] = doctor_specialization
            st.session_state["doctor_shift"] = doctor_shift
            st.session_state["doctor_review_time"] = doctor_review_time
            st.session_state["doctor_feedback"] = selected_feedback
            st.session_state["doctor_notes"] = notes_value

            st.success("Doctor feedback saved successfully.")

    return {
        "doctor_name": st.session_state.get("doctor_name", default_doctor_name or "Not provided"),
        "doctor_specialization": st.session_state.get("doctor_specialization", default_specialization or "Not provided"),
        "doctor_shift": st.session_state.get("doctor_shift", default_shift or "Not provided"),
        "doctor_review_time": st.session_state.get(
            "doctor_review_time",
            datetime.now().strftime("%d-%m-%Y %I:%M %p"),
        ),
        "doctor_feedback": st.session_state.get("doctor_feedback", "Not reviewed"),
        "doctor_notes": st.session_state.get("doctor_notes", "No doctor notes added."),
    }


if is_verification_mode:
    st.markdown(
        """
        <div class="section-card">
            <h2>✅ AI Report Verification</h2>
            <p>
                Report verification opened successfully. The report details are loaded below.
                A doctor can review the case and submit feedback from the Doctor Review section.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🩻 AI Scan Room</div>
        <div class="hero-subtitle">
            Upload an X-ray image and generate fracture prediction, confidence score, risk level, Grad-CAM explanation, doctor review, and PDF report with QR verification.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


left_panel, right_panel = st.columns([0.85, 1.55])

body_regions = ["Hand", "Wrist", "Elbow", "Shoulder", "Hip", "Knee", "Leg", "Ankle", "Other"]
default_body_region = qp("body_region", "Hand")
body_region_index = body_regions.index(default_body_region) if default_body_region in body_regions else 0

with left_panel:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.subheader("Patient / Image Details")

    patient_id = st.text_input(
        "Patient / Image ID",
        value=qp("patient_id", "CASE-001"),
    )

    body_region = st.selectbox(
        "Body Region",
        body_regions,
        index=body_region_index,
    )

    model_name = st.selectbox(
        "Select Model",
        ["ResNet18"],
        index=0,
    )

    uploaded_file = st.file_uploader(
        "Upload X-ray Image",
        type=["jpg", "jpeg", "png"],
    )

    analyze_button = st.button("Analyze X-ray")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card">
            <h3>How to Demo</h3>
            <p>1. Upload X-ray image</p>
            <p>2. Click Analyze X-ray</p>
            <p>3. Show prediction and Grad-CAM</p>
            <p>4. Add doctor notes line-by-line</p>
            <p>5. Generate PDF report with QR code</p>
            <p>6. Scan QR to open AI Scan Room verification mode</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with right_panel:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.subheader("AI Analysis Workspace")

    if is_verification_mode and uploaded_file is None:
        qr_report_id = qp("report_id", "N/A")
        qr_prediction = qp("prediction", "N/A")
        qr_confidence = qp("confidence", "N/A")
        qr_risk = qp("risk", "N/A")
        qr_body_region = qp("body_region", body_region)
        qr_model = qp("model", model_name)
        qr_patient_id = qp("patient_id", patient_id)

        st.success("Verified AI report loaded from QR code.")

        render_report_summary(
            report_id=qr_report_id,
            patient_id=qr_patient_id,
            body_region=qr_body_region,
            model_name=qr_model,
            prediction=qr_prediction,
            confidence=qr_confidence,
            risk_level=qr_risk,
        )

        render_doctor_review_form(
            report_id=qr_report_id,
            patient_id=qr_patient_id,
            body_region=qr_body_region,
            model_name=qr_model,
            prediction=qr_prediction,
            confidence=qr_confidence,
            risk_level=qr_risk,
            form_key="doctor_feedback_form_verification",
        )

    elif uploaded_file is None:
        st.info("Upload an X-ray image from the left panel to begin AI analysis.")

    else:
        image = Image.open(uploaded_file).convert("RGB")

        if analyze_button:
            with st.spinner("Analyzing X-ray image and generating Grad-CAM..."):
                predictor = load_predictor()
                result = predictor.predict(image, generate_gradcam=True)

            report_id = f"ORT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            st.session_state["scan_result"] = result
            st.session_state["scan_image"] = image
            st.session_state["scan_uploaded_name"] = uploaded_file.name
            st.session_state["scan_report_id"] = report_id

            for key in [
                "doctor_feedback",
                "doctor_notes",
                "doctor_name",
                "doctor_specialization",
                "doctor_shift",
                "doctor_review_time",
            ]:
                st.session_state.pop(key, None)

        if "scan_result" in st.session_state:
            result = st.session_state["scan_result"]
            original_image = st.session_state["scan_image"]

            prediction = result["prediction"]
            confidence = result["confidence"]
            risk_level = result["risk_level"]
            report_id_value = st.session_state.get(
                "scan_report_id",
                f"ORT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            )

            if prediction.lower() == "fractured":
                result_class = "result-fractured"
                risk_class = "risk-high" if risk_level == "High" else "risk-medium"
            else:
                result_class = "result-normal"
                risk_class = "risk-low" if risk_level == "Low" else "risk-medium"

            st.markdown(
                f"""
                <div class="{result_class}">
                    Diagnosis Suggestion: {prediction.upper()}
                </div>
                """,
                unsafe_allow_html=True,
            )

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric("Confidence", f"{confidence:.2f}%")
                st.progress(min(confidence / 100, 1.0))

            with m2:
                st.markdown("### Risk Level")
                st.markdown(
                    f'<span class="{risk_class}">{risk_level} Risk</span>',
                    unsafe_allow_html=True,
                )

            with m3:
                st.metric("Model Used", model_name)

            st.caption(f"Report ID: {report_id_value}")

            st.markdown("### Visual Explanation")

            img_col1, img_col2, img_col3 = st.columns(3)

            with img_col1:
                st.image(
                    result["original_image"],
                    caption="Original X-ray",
                    use_container_width=True,
                )

            with img_col2:
                if result["heatmap_image"] is not None:
                    st.image(
                        result["heatmap_image"],
                        caption="Grad-CAM Heatmap",
                        use_container_width=True,
                    )

            with img_col3:
                if result["overlay_image"] is not None:
                    st.image(
                        result["overlay_image"],
                        caption="Grad-CAM Overlay",
                        use_container_width=True,
                    )

            st.markdown("### AI Interpretation")

            if prediction.lower() == "fractured":
                st.error(
                    "The model detected possible fracture-related patterns. "
                    "The Grad-CAM overlay highlights regions that influenced the model prediction. "
                    "Medical expert review is recommended."
                )
            else:
                st.success(
                    "The model did not detect clear fracture-related patterns. "
                    "However, the result should still be clinically verified by a qualified professional."
                )

            doctor_values = render_doctor_review_form(
                report_id=report_id_value,
                patient_id=patient_id,
                body_region=body_region,
                model_name=model_name,
                prediction=prediction,
                confidence=confidence,
                risk_level=risk_level,
                form_key="doctor_feedback_form_prediction",
            )

            st.markdown("### Generate AI Report")

            verification_url = build_report_verification_url(
                report_id=report_id_value,
                patient_id=patient_id,
                body_region=body_region,
                model_name=model_name,
                prediction=prediction,
                confidence=confidence,
                risk_level=risk_level,
                doctor_name=doctor_values["doctor_name"],
                doctor_specialization=doctor_values["doctor_specialization"],
                doctor_shift=doctor_values["doctor_shift"],
                doctor_review_time=doctor_values["doctor_review_time"],
            )

            st.caption(f"QR verification URL: {verification_url}")

            if st.button("Generate PDF Report"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                case_name = clean_filename(patient_id)

                generated_img_dir = PROJECT_ROOT / "outputs" / "generated_images"
                generated_img_dir.mkdir(parents=True, exist_ok=True)

                original_path = generated_img_dir / f"{case_name}_{timestamp}_original.png"
                overlay_path = generated_img_dir / f"{case_name}_{timestamp}_gradcam.png"

                original_image.save(original_path)

                if result["overlay_image"] is not None:
                    result["overlay_image"].save(overlay_path)
                else:
                    overlay_path = None

                report_name = f"{case_name}_{timestamp}_orthovision_report.pdf"
                report_path = APP_DIR / "generated_reports" / report_name

                final_report_path = generate_ai_report(
                    output_path=report_path,
                    patient_id=patient_id,
                    body_region=body_region,
                    model_name=model_name,
                    prediction=prediction,
                    confidence=confidence,
                    risk_level=risk_level,
                    original_image_path=original_path,
                    gradcam_image_path=overlay_path,
                    doctor_feedback=doctor_values["doctor_feedback"],
                    doctor_notes=doctor_values["doctor_notes"],
                    doctor_name=doctor_values["doctor_name"],
                    doctor_specialization=doctor_values["doctor_specialization"],
                    doctor_shift=doctor_values["doctor_shift"],
                    doctor_review_time=doctor_values["doctor_review_time"],
                    report_id=report_id_value,
                    qr_payload=verification_url,
                )

                with open(final_report_path, "rb") as file:
                    st.download_button(
                        label="Download AI Report PDF",
                        data=file,
                        file_name=report_name,
                        mime="application/pdf",
                    )

                st.success(
                    "PDF report generated successfully. Scan the QR code in the PDF to open AI Scan Room verification mode."
                )

    st.markdown("</div>", unsafe_allow_html=True)

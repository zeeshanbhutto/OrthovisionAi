from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

from components.ui_styles import apply_custom_style


st.set_page_config(
    page_title="OrthoVision AI",
    page_icon="🦴",
    layout="wide",
)

apply_custom_style()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🦴 OrthoVision AI</div>
        <div class="hero-subtitle">
            Explainable Bone Fracture Detection System using Deep Learning, ResNet18, Grad-CAM, and AI-assisted report generation.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">AI Models</div>
            <div class="metric-value">CNN + ResNet18</div>
            <div class="metric-caption">Trained fracture classifiers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">Prediction</div>
            <div class="metric-value">2 Classes</div>
            <div class="metric-caption">Fractured / Not Fractured</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">Explainability</div>
            <div class="metric-value">Grad-CAM</div>
            <div class="metric-caption">Visual model focus area</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-title">Reports</div>
            <div class="metric-value">PDF</div>
            <div class="metric-caption">AI-assisted screening report</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1.2, 1])

with left:
    st.markdown(
        """
        <div class="section-card">
            <h2>Clinical AI Workflow</h2>
            <p>
                OrthoVision AI allows users to upload an X-ray image, classify it as fractured or not fractured,
                visualize the model focus area using Grad-CAM, and generate an AI-assisted PDF report.
            </p>
            <ul>
                <li>Upload X-ray image</li>
                <li>Run ResNet18 fracture classification</li>
                <li>View confidence score and risk level</li>
                <li>Generate Grad-CAM explanation</li>
                <li>Download AI-assisted PDF report</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="section-card">
            <h2>Showcase Pages</h2>
            <p><b>AI Scan Room:</b> Main fracture prediction demo</p>
            <p><b>Batch Screening:</b> Analyze multiple X-rays</p>
            <p><b>Explainability Viewer:</b> Grad-CAM visualization</p>
            <p><b>Model Performance:</b> Metrics and confusion matrix</p>
            <p><b>Case Gallery:</b> Preloaded demo X-rays</p>
            <p><b>Report History:</b> Download generated PDF reports</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("Use the left sidebar to open the AI Scan Room and start the live fracture detection demo.")
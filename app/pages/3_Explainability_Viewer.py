from pathlib import Path
import sys

import cv2
import numpy as np
import streamlit as st
from PIL import Image

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

from components.ui_styles import apply_custom_style
from src.predict import FracturePredictor


st.set_page_config(
    page_title="Explainability Viewer | OrthoVision AI",
    page_icon="🔥",
    layout="wide",
)

apply_custom_style()


@st.cache_resource
def load_predictor():
    return FracturePredictor()


predictor = load_predictor()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🔥 Explainability Viewer</div>
        <div class="hero-subtitle">
            Visualize how the model focuses on X-ray regions using Grad-CAM heatmaps.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload X-ray for Grad-CAM visualization",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    with st.spinner("Generating Grad-CAM explanation..."):
        result = predictor.predict(image, generate_gradcam=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.subheader("Prediction Summary")

    col_a, col_b, col_c = st.columns(3)

    col_a.metric("Prediction", result["prediction"].upper())
    col_b.metric("Confidence", f"{result['confidence']:.2f}%")
    col_c.metric("Risk Level", result["risk_level"])

    st.markdown("### Grad-CAM Comparison")

    opacity = st.slider(
        "Heatmap Opacity",
        min_value=0.10,
        max_value=0.90,
        value=0.40,
        step=0.05,
    )

    original_np = np.array(result["original_image"])
    heatmap_np = np.array(result["heatmap_image"])

    custom_overlay = cv2.addWeighted(
        original_np,
        1 - opacity,
        heatmap_np,
        opacity,
        0,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.image(result["original_image"], caption="Original X-ray", use_container_width=True)

    with c2:
        st.image(result["heatmap_image"], caption="Grad-CAM Heatmap", use_container_width=True)

    with c3:
        st.image(Image.fromarray(custom_overlay), caption="Custom Overlay", use_container_width=True)

    st.info(
        "Grad-CAM highlights the image regions that contributed most to the model prediction. "
        "It is an explainability tool, not a replacement for radiologist diagnosis."
    )

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Upload an X-ray image to view Grad-CAM explanation.")
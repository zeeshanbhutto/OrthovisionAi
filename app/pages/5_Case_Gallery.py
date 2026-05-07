from pathlib import Path
import sys

import streamlit as st
from PIL import Image

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

from components.ui_styles import apply_custom_style
from src.predict import FracturePredictor


st.set_page_config(
    page_title="Case Gallery | OrthoVision AI",
    page_icon="🖼️",
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
        <div class="hero-title">🖼️ AI Case Gallery</div>
        <div class="hero-subtitle">
            Use preloaded X-ray cases for smooth showcase demo without needing live file selection.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

gallery_dirs = [
    APP_DIR / "assets" / "sample_xrays",
    PROJECT_ROOT / "data" / "samples",
]

image_paths = []

for gallery_dir in gallery_dirs:
    if gallery_dir.exists():
        image_paths.extend(list(gallery_dir.rglob("*.jpg")))
        image_paths.extend(list(gallery_dir.rglob("*.jpeg")))
        image_paths.extend(list(gallery_dir.rglob("*.png")))

root_test_image = PROJECT_ROOT / "test.png"
if root_test_image.exists():
    image_paths.append(root_test_image)

if not image_paths:
    st.warning(
        "No sample X-ray images found. Add images inside app/assets/sample_xrays/ "
        "or data/samples/."
    )
else:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    selected_image = st.selectbox(
        "Select sample case",
        image_paths,
        format_func=lambda x: x.name,
    )

    image = Image.open(selected_image).convert("RGB")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(image, caption=selected_image.name, use_container_width=True)

    with col2:
        if st.button("Analyze Selected Case"):
            with st.spinner("Analyzing selected case..."):
                result = predictor.predict(image, generate_gradcam=True)

            st.metric("Prediction", result["prediction"].upper())
            st.metric("Confidence", f"{result['confidence']:.2f}%")
            st.metric("Risk Level", result["risk_level"])

            if result["overlay_image"] is not None:
                st.image(
                    result["overlay_image"],
                    caption="Grad-CAM Overlay",
                    use_container_width=True,
                )

    st.markdown('</div>', unsafe_allow_html=True)